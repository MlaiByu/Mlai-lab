<template>
  <div class="users-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>用户管理</h1>
          <p>查看和管理平台用户账号及学习进度</p>
        </div>
      </div>
    </div>

    <div class="users-container">
      <div class="search-section">
        <div class="search-card">
          <div class="search-bar">
            <el-input 
              v-model="searchQuery" 
              placeholder="搜索用户名" 
              class="search-input"
              @input="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch" class="search-btn">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
        </div>
      </div>

      <div class="users-section">
        <div class="section-header">
          <h2>用户列表</h2>
          <el-button type="primary" @click="showAddModal = true" class="add-btn">
            <el-icon><Plus /></el-icon>
            添加用户
          </el-button>
        </div>

        <div class="users-table-wrapper">
          <el-table :data="filteredUsers" border class="users-table">
            <el-table-column prop="id" label="ID" width="80">
              <template #default="scope">
                <span class="id-badge">{{ scope.row.id }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="username" label="用户名" min-width="150">
              <template #default="scope">
                <div class="user-info-cell">
                  <div class="user-avatar-mini">
                    <el-icon><User /></el-icon>
                  </div>
                  <span class="username">{{ scope.row.username }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="role" label="角色" width="120">
              <template #default="scope">
                <el-tag :type="getRoleTagType(scope.row.role)">{{ getRoleText(scope.row.role) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="学习进度" width="160">
              <template #default="scope">
                <span v-if="scope.row.role === 'student'">
                  <div class="progress-mini">
                    <el-progress 
                      :percentage="getCompletionRate(scope.row.id)" 
                      :show-text="true" 
                      stroke-width="8"
                      class="mini-progress"
                    />
                  </div>
                </span>
                <span v-else class="no-progress">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="380">
              <template #default="scope">
                <div class="action-buttons">
                  <el-button 
                    size="small" 
                    v-if="scope.row.role === 'student'" 
                    @click="viewProgress(scope.row)"
                    class="action-btn view-btn"
                  >
                    <el-icon><View /></el-icon>
                    查看进度
                  </el-button>
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="changePassword(scope.row)"
                    class="action-btn edit-btn"
                  >
                    <el-icon><Key /></el-icon>
                    修改密码
                  </el-button>
                  <el-button 
                    size="small" 
                    v-if="scope.row.role === 'student'" 
                    type="success" 
                    @click="promoteUser(scope.row)"
                    class="action-btn promote-btn"
                  >
                    <el-icon><TrendCharts /></el-icon>
                    提升为教师
                  </el-button>
                  <el-button 
                    size="small" 
                    v-if="scope.row.role === 'teacher'" 
                    type="warning" 
                    @click="demoteUser(scope.row)"
                    class="action-btn demote-btn"
                  >
                    <el-icon><ArrowDown /></el-icon>
                    降为学生
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="deleteUser(scope.row)"
                    class="action-btn delete-btn"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="total > pageSize"
            :current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            @current-change="handlePageChange"
            layout="prev, pager, next, jumper, ->, total"
            class="pagination"
          />
        </div>
      </div>
    </div>

    <div v-if="showProgressModal" class="modal-overlay" @click.self="closeProgressModal">
      <div class="modal-content progress-modal">
        <div class="modal-header">
          <h3>学生学习进度 - {{ selectedUser?.username }}</h3>
          <button class="modal-close" @click="closeProgressModal">
            <el-icon><Close /></el-icon>
          </button>
        </div>
        <div class="modal-body">
          <div class="stats-summary">
            <div class="stat-card-mini">
              <span class="stat-label">总尝试次数</span>
              <span class="stat-value">{{ selectedUserStats?.total_attempts || 0 }}</span>
            </div>
            <div class="stat-card-mini">
              <span class="stat-label">成功次数</span>
              <span class="stat-value success">{{ selectedUserStats?.total_success || 0 }}</span>
            </div>
            <div class="stat-card-mini">
              <span class="stat-label">完成率</span>
              <span class="stat-value primary">{{ getSelectedUserCompletionRate() }}%</span>
            </div>
          </div>
          <h4 class="detail-title">实验记录详情</h4>
          <div v-if="selectedUserExperiments.length === 0" class="empty-state">
            <el-empty description="暂无实验记录" />
          </div>
          <div v-else class="experiment-cards">
            <div 
              v-for="(exp, index) in selectedUserExperiments" 
              :key="index" 
              :class="['experiment-card', { completed: exp.success, 'in-progress': !exp.success && exp.attempt_count > 0 }]"
            >
              <div class="card-header">
                <div class="vuln-info-mini">
                  <div :class="['status-dot', exp.success ? 'completed' : 'pending']"></div>
                  <span class="vuln-name">{{ exp.vulnerability_type }}</span>
                </div>
                <el-tag :type="getExperimentStatusType(exp)" size="small">
                  {{ getExperimentStatusText(exp) }}
                </el-tag>
              </div>
              <div class="card-body">
                <div class="stat-row">
                  <span class="stat-label">尝试次数</span>
                  <span class="stat-value">{{ exp.attempt_count }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">成功次数</span>
                  <span class="stat-value">{{ exp.success_count }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">最后尝试</span>
                  <span class="stat-value">{{ formatDate(exp.last_attempt) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <el-button type="success" @click="exportProgress">
            <el-icon><Download /></el-icon>
            导出成绩
          </el-button>
          <el-button @click="closeProgressModal">关闭</el-button>
        </div>
      </div>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingUser ? '编辑用户' : '添加用户' }}</h3>
          <button class="modal-close" @click="closeModal">
            <el-icon><Close /></el-icon>
          </button>
        </div>
        <div class="modal-body">
          <el-form :model="formData" label-width="100px" class="user-form">
            <el-form-item label="用户名">
              <el-input v-model="formData.username" placeholder="请输入用户名"></el-input>
            </el-form-item>
            <el-form-item label="密码" v-if="!editingUser">
              <el-input v-model="formData.password" type="password" placeholder="请输入密码"></el-input>
            </el-form-item>
            <el-form-item label="角色">
              <el-select 
                v-model="formData.role" 
                placeholder="请选择角色"
                :disabled="editingUser && editingUser.role === 'admin'"
              >
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
import { 
  Search, Plus, View, Key, TrendCharts, ArrowDown, Delete, User, Close, Download
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { users as usersApi } from '../api'
import { formatDate } from '../utils/date'

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

const vulnerabilityCount = 11

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
    case 'admin': return 'danger'
    default: return 'info'
  }
}

const getRoleText = (role) => {
  switch (role) {
    case 'teacher': return '教师'
    case 'student': return '学生'
    case 'admin': return '管理员'
    default: return role
  }
}

const getCompletionRate = (userId) => {
  const userData = users.value.find(u => u.id === userId)
  if (!userData) return 0
  const userExp = userData.experiments || []
  if (userExp.length === 0) return 0
  const completedCount = userExp.filter(e => e.success).length
  return Math.round((completedCount / vulnerabilityCount) * 100)
}

const getSelectedUserCompletionRate = () => {
  const userExp = selectedUserExperiments.value
  if (userExp.length === 0) return 0
  const completedCount = userExp.filter(e => e.success).length
  return Math.round((completedCount / vulnerabilityCount) * 100)
}

const getExperimentStatusType = (exp) => {
  const status = exp.status || (exp.success ? 'completed' : (exp.attempt_count > 0 ? 'attempted' : 'not_started'))
  switch (status) {
    case 'completed':
      return 'success'
    case 'in_progress':
      return 'warning'
    case 'attempted':
      return 'info'
    default:
      return 'info'
  }
}

const getExperimentStatusText = (exp) => {
  const status = exp.status || (exp.success ? 'completed' : (exp.attempt_count > 0 ? 'attempted' : 'not_started'))
  switch (status) {
    case 'completed':
      return '已完成'
    case 'in_progress':
      return '进行中'
    case 'attempted':
      return '已尝试'
    default:
      return '未开始'
  }
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
  selectedUserStats.value = null
  selectedUserExperiments.value = []
  
  try {
    const response = await usersApi.getProfile(user.id)
    if (response.success) {
      selectedUserStats.value = response.data.statistics
      selectedUserExperiments.value = (response.data.experiments || []).filter(exp => exp.attempt_count > 0)
    }
    showProgressModal.value = true
  } catch (error) {
    console.error('加载学生进度失败:', error)
    showProgressModal.value = true
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
    const response = await fetch(`/api/stats/export_scores?userId=${userId}`, {
      method: 'GET',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    })
    
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
      if (editingUser.value.role === 'admin') {
        ElMessage.warning('管理员角色不能被修改')
        return
      }
      
      let needUpdateBasic = formData.value.username !== editingUser.value.username || formData.value.password
      let roleChanged = formData.value.role !== editingUser.value.role
      
      if (roleChanged) {
        let message = formData.value.role === 'teacher' 
          ? `确定要将用户 ${editingUser.value.username} 提升为教师吗？`
          : `确定要将用户 ${editingUser.value.username} 降为学生吗？`
        let title = formData.value.role === 'teacher' ? '提升确认' : '降级确认'
        
        await ElMessageBox.confirm(message, title, {
          confirmButtonText: formData.value.role === 'teacher' ? '确定提升' : '确定降级',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        if (formData.value.role === 'teacher') {
          await usersApi.promoteToTeacher(editingUser.value.id)
        } else {
          await usersApi.demoteToStudent(editingUser.value.id)
        }
      }
      
      if (needUpdateBasic) {
        await usersApi.update(editingUser.value.id, formData.value)
      }
      
      ElMessage.success('用户更新成功')
    } else {
      await usersApi.create(formData.value)
      ElMessage.success('用户添加成功')
    }
    closeModal()
    await loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('保存用户失败:', error)
      ElMessage.error('保存用户失败: ' + error.message)
    }
  }
}

const changePassword = async (user) => {
  if (!user || !user.id) return
  
  try {
    const { value: password } = await ElMessageBox.prompt(
      `请输入用户 ${user.username} 的新密码`,
      '修改密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'password',
        inputPlaceholder: '请输入新密码'
      }
    )
    
    if (!password) {
      ElMessage.warning('密码不能为空')
      return
    }
    
    await usersApi.changePassword(user.id, { password })
    ElMessage.success('密码修改成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('修改密码失败:', error)
      ElMessage.error('修改密码失败: ' + error.message)
    }
  }
}

const promoteUser = async (user) => {
  if (!user || !user.id) return
  
  try {
    await ElMessageBox.confirm(
      `确定要将用户 ${user.username} 提升为教师吗？`,
      '提升确认',
      {
        confirmButtonText: '确定提升',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await usersApi.promoteToTeacher(user.id)
    if (response.success) {
      ElMessage.success(response.message)
      await loadUsers()
    } else {
      ElMessage.error(response.message || '提升失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提升用户角色失败:', error)
      ElMessage.error('提升失败: ' + error.message)
    }
  }
}

const demoteUser = async (user) => {
  if (!user || !user.id) return
  
  try {
    await ElMessageBox.confirm(
      `确定要将用户 ${user.username} 降为学生吗？`,
      '降级确认',
      {
        confirmButtonText: '确定降级',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await usersApi.demoteToStudent(user.id)
    if (response.success) {
      ElMessage.success(response.message)
      await loadUsers()
    } else {
      ElMessage.error(response.message || '降级失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('降级用户角色失败:', error)
      ElMessage.error('降级失败: ' + error.message)
    }
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
  background: linear-gradient(135deg, #f0f2f5 0%, #dbeafe 30%, #f0f2f5 100%);
  position: relative;
}

.page-header {
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
  padding: 50px 24px;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -15%;
  width: 550px;
  height: 550px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  filter: blur(50px);
}

.page-header::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 450px;
  height: 450px;
  background: rgba(99, 102, 241, 0.15);
  border-radius: 50%;
  filter: blur(40px);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.header-text h1 {
  color: white;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.header-text p {
  color: rgba(255, 255, 255, 0.85);
  font-size: 16px;
  margin: 0;
}

.users-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.search-section {
  margin-bottom: 20px;
}

.search-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.1);
  transition: all 0.3s ease;
}

.search-card:hover {
  box-shadow: 0 10px 32px rgba(99, 102, 241, 0.12);
}

.search-bar {
  display: flex;
  gap: 12px;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.search-btn {
  padding: 0 24px;
}

.users-section {
  background: white;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

.users-table-wrapper {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-radius: 12px;
}

.users-table :deep(.el-table__header) {
  background: #f9fafb;
}

.users-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #6b7280;
  border-bottom: 2px solid #f3f4f6;
}

.users-table :deep(.el-table__body tr:hover) {
  background: rgba(99, 102, 241, 0.05);
}

.id-badge {
  background: #f3f4f6;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
}

.user-info-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar-mini {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
}

.username {
  font-weight: 500;
  color: #1f2937;
}

.progress-mini {
  width: 120px;
}

.mini-progress :deep(.el-progress__text) {
  font-size: 12px;
  color: #6366f1;
}

.no-progress {
  color: #9ca3af;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination {
  margin-top: 20px;
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
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-content.progress-modal {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 24px;
}

.user-form {
  padding-top: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f3f4f6;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card-mini {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.stat-card-mini .stat-label {
  display: block;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-card-mini .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.stat-card-mini .stat-value.success {
  color: #22c55e;
}

.stat-card-mini .stat-value.primary {
  color: #6366f1;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.experiment-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  max-height: 350px;
  overflow-y: auto;
}

.experiment-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
}

.experiment-card.completed {
  border-color: #22c55e;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.05) 0%, white 100%);
}

.experiment-card.in-progress {
  border-color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, white 100%);
}

.experiment-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.vuln-info-mini {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.completed {
  background: #22c55e;
}

.status-dot.pending {
  background: #d1d5db;
}

.vuln-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.experiment-card .card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.stat-row .stat-label {
  color: #6b7280;
}

.stat-row .stat-value {
  color: #1f2937;
  font-weight: 500;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .stats-summary {
    grid-template-columns: 1fr;
  }
  
  .experiment-cards {
    grid-template-columns: 1fr;
  }
}
</style>
