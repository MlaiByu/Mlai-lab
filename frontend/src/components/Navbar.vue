<template>
  <header class="navbar">
    <div class="navbar-container">
      <router-link to="/home" class="brand-link">
        <div class="brand-logo">🛡️</div>
        <span class="brand-text">Mlai-Lab</span>
      </router-link>

      <nav class="navbar-nav">
        <router-link to="/home" :class="['nav-link', { active: route.path === '/home' }]">
          首页
        </router-link>
        <router-link to="/vulnerabilities" :class="['nav-link', { active: route.path === '/vulnerabilities' }]">
          漏洞列表
        </router-link>
        <router-link to="/progress" :class="['nav-link', { active: route.path === '/progress' }]">
          学习进度
        </router-link>
        <router-link v-if="isTeacher" to="/users" :class="['nav-link', { active: route.path === '/users' }]">
          用户管理
        </router-link>
      </nav>

      <div class="navbar-right">
        <div v-if="isLoggedIn" class="user-menu-container">
          <button class="user-button" @click="toggleDropdown">
            <div class="user-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <span class="user-name">{{ userName }}</span>
            <svg class="menu-arrow" :class="{ rotated: dropdownVisible }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </button>
          
          <div v-show="dropdownVisible" class="dropdown-menu">
            <button class="dropdown-item" @click="handleProfile">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <span>个人资料</span>
            </button>
            <hr class="dropdown-divider"/>
            <button class="dropdown-item" @click="handleLogout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              <span>退出登录</span>
            </button>
          </div>
        </div>

        <router-link v-if="!isLoggedIn" to="/login" class="login-link">
          <button class="login-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 16H9a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-2"/>
              <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
            </svg>
            <span>登录</span>
          </button>
        </router-link>
      </div>
    </div>

    <div v-if="showProfileModal" class="modal-overlay" @click="closeProfileModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>个人资料</h3>
          <button class="modal-close" @click="closeProfileModal">×</button>
        </div>
        <div class="modal-body">
          <div class="profile-content">
            <div class="profile-avatar-large">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <div class="profile-info">
              <div class="info-item">
                <span class="label">用户名</span>
                <span class="value">{{ profileData.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">角色</span>
                <span class="value">{{ profileData.roleText }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建时间</span>
                <span class="value">{{ profileData.created_at }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeProfileModal">关闭</button>
          <button class="btn btn-primary" @click="handleChangePassword">修改密码</button>
        </div>
      </div>
    </div>

    <div v-if="showPasswordModal" class="modal-overlay" @click="closePasswordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="modal-close" @click="closePasswordModal">×</button>
        </div>
        <div class="modal-body">
          <div class="password-form">
            <div class="form-group">
              <label class="form-label">旧密码</label>
              <input type="password" v-model="passwordForm.oldPassword" class="form-input" placeholder="请输入旧密码" />
            </div>
            <div class="form-group">
              <label class="form-label">新密码</label>
              <input type="password" v-model="passwordForm.newPassword" class="form-input" placeholder="请输入新密码" />
            </div>
            <div class="form-group">
              <label class="form-label">确认密码</label>
              <input type="password" v-model="passwordForm.confirmPassword" class="form-input" placeholder="请再次输入新密码" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closePasswordModal">取消</button>
          <button class="btn btn-primary" @click="submitPasswordChange">确认修改</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import store from '../store'
import { users } from '../api'

const router = useRouter()
const route = useRoute()
const dropdownVisible = ref(false)
const showProfileModal = ref(false)
const showPasswordModal = ref(false)

const profileData = reactive({
  username: '',
  role: '',
  roleText: '',
  created_at: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const isLoggedIn = computed(() => store.getters.isLoggedIn())
const isTeacher = computed(() => store.getters.isTeacher())
const userName = computed(() => store.state.user?.username || '')
const userId = computed(() => store.state.user?.id || null)

const userRoleText = computed(() => {
  const role = store.state.user?.role
  switch(role) {
    case 'teacher': return '教师'
    case 'student': return '学生'
    case 'admin': return '管理员'
    default: return role || ''
  }
})

const toggleDropdown = () => {
  dropdownVisible.value = !dropdownVisible.value
}

const closeDropdown = () => {
  dropdownVisible.value = false
}

const handleProfile = () => {
  closeDropdown()
  loadProfile()
  showProfileModal.value = true
}

const handleLogout = () => {
  closeDropdown()
  store.actions.logout()
  router.push('/login')
}

const closeProfileModal = () => {
  showProfileModal.value = false
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  resetPasswordForm()
}

const handleChangePassword = () => {
  showProfileModal.value = false
  resetPasswordForm()
  showPasswordModal.value = true
}

const resetPasswordForm = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const loadProfile = async () => {
  if (!userId.value) return
  try {
    const response = await users.getProfile(userId.value)
    if (response.success) {
      profileData.username = response.data.username
      profileData.role = response.data.role
      profileData.roleText = userRoleText.value
      profileData.created_at = response.data.created_at || ''
    }
  } catch (error) {
    console.error('加载个人资料失败:', error)
  }
}

const submitPasswordChange = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    alert('请填写所有字段')
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    alert('密码长度不能少于6位')
    return
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  
  try {
    const response = await users.changePassword(userId.value, {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    
    if (response.success) {
      alert('密码修改成功')
      closePasswordModal()
    } else {
      alert(response.message || '密码修改失败')
    }
  } catch (error) {
    alert(error.message || '密码修改失败')
  }
}

const refreshExperimentRecords = async () => {
  await store.actions.loadExperimentRecords()
}

const handleClickOutside = (event) => {
  if (!event.target.closest('.user-menu-container')) {
    closeDropdown()
  }
}

watch(() => route.path, async () => {
  closeDropdown()
  await refreshExperimentRecords()
})

onMounted(() => {
  refreshExperimentRecords()
  router.afterEach(refreshExperimentRecords)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0;
  height: 70px;
  line-height: 70px;
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease;
}

.brand-link:hover {
  transform: translateY(-1px);
}

.brand-logo {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.navbar-nav {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 2rem;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
}

.nav-link.active {
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-menu-container {
  position: relative;
}

.user-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-button:hover {
  background: rgba(14, 165, 233, 0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-avatar svg {
  width: 18px;
  height: 18px;
}

.user-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: #334155;
}

.menu-arrow {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.menu-arrow.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 180px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
  z-index: 1001;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  font-size: 0.875rem;
  color: #334155;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
}

.dropdown-item svg {
  width: 16px;
  height: 16px;
}

.dropdown-divider {
  margin: 0.5rem 0;
  border: none;
  border-top: 1px solid #e5e7eb;
}

.login-link {
  text-decoration: none;
}

.login-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.login-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.login-button svg {
  width: 16px;
  height: 16px;
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
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 400px;
  max-width: 90%;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-secondary {
  background: #f1f5f9;
  color: #64748b;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.profile-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-avatar-large {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 1.5rem;
}

.profile-avatar-large svg {
  width: 50px;
  height: 50px;
}

.profile-info {
  width: 100%;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #64748b;
  font-size: 0.875rem;
}

.info-item .value {
  color: #1e293b;
  font-weight: 600;
  font-size: 0.875rem;
}

.password-form {
  width: 100%;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #0ea5e9;
}

.form-input::placeholder {
  color: #94a3b8;
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 1rem;
  }
  
  .navbar-nav {
    flex: none;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .nav-link {
    font-size: 0.875rem;
  }
  
  .user-name {
    display: none;
  }
  
  .brand-text {
    font-size: 1.125rem;
  }
}
</style>
