<template>
  <div class="users-page">
    <div class="page-header">
      <h1>用户管理</h1>
      <p>查看和管理平台用户账号及学习进度</p>
    </div>

    <div class="users-container">
      <el-card class="search-card">
        <div class="search-bar">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索用户名" 
            class="search-input"
            @input="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>
      </el-card>

      <el-card class="users-card">
        <div class="card-header">
          <h2>用户列表</h2>
          <el-button type="primary" @click="showAddModal = true">添加用户</el-button>
        </div>

        <el-table :data="filteredUsers" border style="width: 100%">
          <el-table-column prop="id" label="ID" width="80"></el-table-column>
          <el-table-column prop="username" label="用户名"></el-table-column>
          <el-table-column prop="role" label="角色" width="100">
            <template #default="scope">
              <el-tag :type="getRoleTagType(scope.row.role)">{{ getRoleText(scope.row.role) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="学习进度" width="180">
            <template #default="scope">
              <span v-if="scope.row.role === 'student'">
                {{ getCompletionRate(scope.row.id) }}%
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
          <el-table-column label="操作" width="320">
            <template #default="scope">
              <el-button size="small" v-if="scope.row.role === 'student'" @click="viewProgress(scope.row)">查看进度</el-button>
              <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteUser(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-if="total > pageSize"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @current-change="handlePageChange"
          layout="prev, pager, next, jumper"
          class="pagination"
        />
      </el-card>
    </div>

    <div v-if="showProgressModal" class="modal-overlay" @click.self="closeProgressModal">
      <div class="modal-content progress-modal">
        <div class="modal-header">
          <h3>学生学习进度 - {{ selectedUser?.username }}</h3>
          <button class="modal-close" @click="closeProgressModal">×</button>
        </div>
        <div class="modal-body">
          <div class="stats-summary">
            <div class="stat-item">
              <span class="stat-label">总尝试次数</span>
              <span class="stat-value">{{ selectedUserStats?.total_attempts || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">成功次数</span>
              <span class="stat-value">{{ selectedUserStats?.total_success || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">完成率</span>
              <span class="stat-value">{{ getSelectedUserCompletionRate() }}%</span>
            </div>
          </div>
          <h4 class="detail-title">实验记录详情</h4>
          <el-table :data="selectedUserExperiments" border style="width: 100%;">
            <el-table-column prop="vulnerability_type" label="漏洞类型" width="150"></el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getExperimentStatusType(scope.row)">
                  {{ getExperimentStatusText(scope.row) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="attempt_count" label="尝试次数" width="100"></el-table-column>
            <el-table-column prop="success_count" label="成功次数" width="100"></el-table-column>
            <el-table-column label="最后尝试" width="160">
              <template #default="scope">
                {{ scope.row.last_attempt || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="modal-footer">
          <el-button type="success" icon="Download" @click="exportProgress">导出成绩</el-button>
          <el-button @click="closeProgressModal">关闭</el-button>
        </div>
      </div>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingUser ? '编辑用户' : '添加用户' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <el-form :model="formData" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="formData.username" placeholder="请输入用户名"></el-input>
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="formData.password" type="password" placeholder="请输入密码"></el-input>
            </el-form-item>
            <el-form-item label="角色">
              <el-select v-model="formData.role" placeholder="请选择角色">
                <el-option label="学生" value="student"></el-option>
                <el-option label="教师" value="teacher"></el-option>
              </el-select>
            </el-form-item>
          </el-form>
        </div>
        <div class="modal-footer">
          <el-button @click="closeModal">取消</el-button>
          <el-button type="primary" @click="saveUser">{{ editingUser ? '保存' : '添加' }}</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { users as usersApi } from '../api'

const users = ref([])
const searchQuery = ref('')
const showAddModal = ref(false)
const showProgressModal = ref(false)
const editingUser = ref(null)
const selectedUser = ref(null)
const selectedUserStats = ref(null)
const selectedUserExperiments = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const formData = ref({
  username: '',
  password: '',
  role: 'student'
})

const vulnerabilities = [
  'SQL注入-入门', 'SQL注入-中级', 'SQL注入-高级',
  '反射型XSS', '存储型XSS', 'DOM型XSS',
  'PHP反序列化', 'Python反序列化', '文件上传'
]

const filteredUsers = computed(() => {
  let result = users.value
  if (searchQuery.value) {
    result = result.filter(u => u.username.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  return result.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value)
})

const getRoleTagType = (role) => {
  switch (role) {
    case 'teacher': return 'warning'
    case 'student': return 'success'
    default: return 'info'
  }
}

const getRoleText = (role) => {
  switch (role) {
    case 'teacher': return '教师'
    case 'student': return '学生'
    default: return role
  }
}

const getCompletionRate = (userId) => {
  const userData = users.value.find(u => u.id === userId)
  if (!userData) return 0
  const userExp = userData.experiments || []
  if (userExp.length === 0) return 0
  const completedCount = userExp.filter(e => e.status === 'completed').length
  return Math.round((completedCount / vulnerabilities.length) * 100)
}

const getSelectedUserCompletionRate = () => {
  const userExp = selectedUserExperiments.value
  if (userExp.length === 0) return 0
  const completedCount = userExp.filter(e => e.success_count > 0).length
  return Math.round((completedCount / vulnerabilities.length) * 100)
}

const getExperimentStatusType = (exp) => {
  if (exp.success_count > 0) return 'success'
  if (exp.attempt_count > 0) return 'warning'
  return 'info'
}

const getExperimentStatusText = (exp) => {
  if (exp.success_count > 0) return '已完成'
  if (exp.attempt_count > 0) return '进行中'
  return '未开始'
}

const loadUsers = async () => {
  try {
    const response = await usersApi.list()
    if (response.success) {
      users.value = response.data
      total.value = users.value.length
    }
  } catch (error) {
    console.error('加载用户失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const viewProgress = async (user) => {
  selectedUser.value = user
  try {
    const response = await usersApi.getProfile(user.id)
    if (response.success) {
      selectedUserStats.value = response.data.statistics
      selectedUserExperiments.value = response.data.experiments || []
    }
    showProgressModal.value = true
  } catch (error) {
    console.error('加载学生进度失败:', error)
  }
}

const closeProgressModal = () => {
  showProgressModal.value = false
  selectedUser.value = null
  selectedUserStats.value = null
  selectedUserExperiments.value = []
}

const getAuthToken = () => {
  const user = localStorage.getItem('user')
  if (user) {
    try {
      return JSON.parse(user).token
    } catch {
      return null
    }
  }
  return null
}

const exportProgress = async () => {
  if (!selectedUser.value) {
    console.error('导出失败: 未选择用户')
    return
  }
  
  const userId = selectedUser.value.id
  if (!userId) {
    console.error('导出失败: 用户ID不存在', selectedUser.value)
    return
  }
  
  try {
    const token = getAuthToken()
    console.log('开始导出, userId:', userId, 'token:', token ? '存在' : '不存在')
    const response = await fetch(`/api/stats/export_scores?userId=${userId}`, {
      method: 'GET',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    })
    
    console.log('导出响应状态:', response.status)
    
    if (response.ok) {
      const blob = await response.blob()
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = `${selectedUser.value.username}_progress.csv`
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=(.+)/)
        if (match) {
          filename = match[1]
        }
      }
      
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } else {
      const errorText = await response.text()
      console.error('导出失败, 状态:', response.status, '响应:', errorText)
    }
  } catch (error) {
    console.error('导出失败:', error)
  }
}

const addUser = () => {
  editingUser.value = null
  formData.value = {
    username: '',
    password: '',
    role: 'student'
  }
  showAddModal.value = true
}

const editUser = (user) => {
  editingUser.value = user
  formData.value = {
    username: user.username,
    password: '',
    role: user.role
  }
  showAddModal.value = true
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 ${user.username} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await usersApi.delete(user.id)
    await loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
    }
  }
}

const saveUser = async () => {
  try {
    if (editingUser.value) {
      await usersApi.update(editingUser.value.id, formData.value)
    } else {
      await usersApi.create(formData.value)
    }
    closeModal()
    await loadUsers()
  } catch (error) {
    console.error('保存用户失败:', error)
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingUser.value = null
  formData.value = {
    username: '',
    password: '',
    role: 'student'
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-page {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #64748b;
}

.users-container {
  max-width: 1200px;
  margin: 0 auto;
}

.search-card {
  margin-bottom: 1.5rem;
}

.search-bar {
  display: flex;
  gap: 1rem;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.users-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.pagination {
  margin-top: 1.5rem;
  text-align: right;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
}

.modal-content.progress-modal {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  display: block;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.detail-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1rem;
}
</style>
