<template>
  <el-header class="main-header">
    <div class="header-content">
      <router-link to="/home" class="logo-wrapper">
        <div class="logo">
          <div class="logo-icon">
            <el-icon :size="28"><Lock /></el-icon>
          </div>
          <span class="logo-text">Mlai-Lab</span>
        </div>
      </router-link>
      
      <el-menu 
        :default-active="currentRoute"
        class="main-menu"
        mode="horizontal"
        router
      >
        <el-menu-item index="/home">
          <el-icon :size="18"><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/learning">
          <el-icon :size="18"><Reading /></el-icon>
          <span>漏洞学习</span>
        </el-menu-item>
        <el-menu-item index="/vulnerabilities">
          <el-icon :size="18"><Warning /></el-icon>
          <span>漏洞列表</span>
        </el-menu-item>
        <el-menu-item index="/progress">
          <el-icon :size="18"><TrendCharts /></el-icon>
          <span>学习进度</span>
        </el-menu-item>
        <el-menu-item v-if="isTeacherOrAdmin" index="/users">
          <el-icon :size="18"><UserFilled /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>

      <div class="header-right">
        <el-dropdown v-if="isLoggedIn" trigger="click">
          <div class="user-menu">
            <div class="user-avatar">
              <el-icon :size="20"><User /></el-icon>
            </div>
            <span class="user-name">{{ userName }}</span>
            <el-icon :size="16" class="dropdown-arrow"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleProfile">
                <el-icon><User /></el-icon>
                <span>个人资料</span>
              </el-dropdown-item>
              <el-dropdown-item @click="handleLogout">
                <el-icon><TurnOff /></el-icon>
                <span>退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <router-link v-else to="/login" class="login-btn">
          <el-button type="primary" size="small">登录</el-button>
        </router-link>
      </div>
    </div>

    <el-dialog 
      v-model="showProfileModal" 
      title="个人资料" 
      width="450px"
    >
      <div class="profile-content">
        <div class="profile-header">
          <div class="avatar-circle">
            <el-icon :size="48"><User /></el-icon>
          </div>
          <div class="profile-info">
            <h3>{{ profileData.username }}</h3>
            <el-tag :type="getRoleTagType(profileData.role)">
              {{ getRoleText(profileData.role) }}
            </el-tag>
          </div>
        </div>
        <el-divider />
        <div class="profile-details">
          <div class="detail-row">
            <span class="detail-label">用户ID</span>
            <span class="detail-value">{{ profileData.id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">积分</span>
            <span class="detail-value highlight">{{ profileData.score || 0 }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">注册时间</span>
            <span class="detail-value">{{ formatDateTime(profileData.created_at) }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showProfileModal = false">关闭</el-button>
        <el-button v-if="isTeacherOrAdmin" type="primary" @click="showPasswordModal = true">修改密码</el-button>
      </template>
    </el-dialog>

    <el-dialog 
      v-model="showPasswordModal" 
      title="修改密码" 
      width="450px"
    >
      <el-form :model="passwordForm" label-width="100px" class="password-form">
        <el-form-item label="新密码">
          <el-input 
            v-model="passwordForm.newPassword" 
            type="password" 
            placeholder="请输入新密码" 
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input 
            v-model="passwordForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入新密码" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordModal = false">取消</el-button>
        <el-button type="primary" @click="submitPasswordChange">确认修改</el-button>
      </template>
    </el-dialog>
  </el-header>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Lock, HomeFilled, Reading, Warning, TrendCharts, UserFilled, User, ArrowDown, TurnOff } from '@element-plus/icons-vue';
import store from '../store'
import { users } from '../api'
import { formatDateTime } from '../utils/date'

const route = useRoute()
const router = useRouter()

const showProfileModal = ref(false)
const showPasswordModal = ref(false)

const profileData = reactive({
  id: '',
  username: '',
  role: '',
  score: 0,
  created_at: ''
})

const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

const isLoggedIn = computed(() => !!store.state.user)
const isTeacherOrAdmin = computed(() => {
  const role = store.state.user?.role
  return role === 'teacher' || role === 'admin'
})
const userName = computed(() => store.state.user?.username || '')
const userId = computed(() => store.state.user?.id || null)
const currentRoute = computed(() => route.path)

const getRoleTagType = (role) => {
  switch(role) {
    case 'teacher': return 'warning'
    case 'admin': return 'danger'
    case 'student': return 'success'
    default: return 'info'
  }
}

const getRoleText = (role) => {
  switch(role) {
    case 'teacher': return '教师'
    case 'student': return '学生'
    case 'admin': return '管理员'
    default: return role || ''
  }
}

const handleProfile = async () => {
  if (!userId.value) return
  try {
    const response = await users.getProfile(userId.value)
    if (response.success) {
      profileData.id = response.data.id
      profileData.username = response.data.username
      profileData.role = response.data.role
      profileData.score = response.data.score || 0
      profileData.created_at = response.data.created_at || ''
    }
  } catch (error) {
    console.error('加载个人资料失败:', error)
  }
  showProfileModal.value = true
}

const handleLogout = () => {
  store.actions.logout()
  router.push('/login')
}

const submitPasswordChange = async () => {
  if (!passwordForm.newPassword || !passwordForm.confirmPassword) {
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    return
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    return
  }
  
  try {
    const response = await users.changePassword(userId.value, {
      password: passwordForm.newPassword
    })
    
    if (response.success) {
      showPasswordModal.value = false
      showProfileModal.value = false
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  }
}
</script>

<style scoped>
.main-header {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
}

.logo-wrapper {
  text-decoration: none;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.main-menu {
  flex: 1;
  justify-content: center;
  border-bottom: none;
}

.main-menu :deep(.el-menu-item) {
  margin: 0 12px;
  padding: 0 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.main-menu :deep(.el-menu-item:hover) {
  background: rgba(99, 102, 241, 0.08);
}

.main-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  color: #6366f1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 30px;
  transition: all 0.3s ease;
}

.user-menu:hover {
  background: rgba(99, 102, 241, 0.08);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.dropdown-arrow {
  color: #9ca3af;
}

.login-btn {
  text-decoration: none;
}

.profile-content {
  padding: 16px 0;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 16px;
}

.avatar-circle {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
}

.profile-info {
  flex: 1;
}

.profile-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.profile-details {
  padding-top: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  color: #6b7280;
  font-weight: 500;
}

.detail-value {
  color: #1f2937;
  font-weight: 600;
}

.detail-value.highlight {
  color: #6366f1;
  font-size: 18px;
}

.password-form {
  padding: 8px 0;
}
</style>
