<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="login-header">
        <el-icon :size="48" class="login-icon"><Lock /></el-icon>
        <h1>Mlai-Lab</h1>
        <p>Web安全漏洞测试平台</p>
      </div>

      <el-form :model="loginForm" class="login-form">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名"
            autocomplete="username"
            size="large"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            autocomplete="current-password"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
        
        <div v-if="errorMessage" class="message-box error">
          <div class="message-content">
            <span class="error-icon">✕</span>
            <span class="message-text">{{ errorMessage }}</span>
          </div>
        </div>
      </el-form>

      <div class="login-footer">
        <span>还没有账号？</span>
        <router-link to="/register" class="register-link">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElCard, ElForm, ElFormItem, ElInput, ElButton, ElAlert } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import store from '../store'

const router = useRouter()

const loginForm = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(loginForm)
    })
    const data = await response.json()
    
    if (data.success) {
      let user = { 
        id: data.user.id,
        username: data.user.username,
        role: data.user.role,
        token: data.user.token,
        score: data.user.score || 0
      }
      
      try {
        const profileResponse = await fetch('/api/users/profile/' + user.id, {
          headers: {
            'Authorization': 'Bearer ' + user.token,
            'Content-Type': 'application/json'
          }
        })
        const profileData = await profileResponse.json()
        if (profileData.success && profileData.data && profileData.data.score !== undefined) {
          user.score = profileData.data.score
        }
      } catch (e) {
        console.warn('无法获取用户分数:', e)
      }
      
      localStorage.setItem('user', JSON.stringify(user))
      store.mutations.setUser(user)
      await store.actions.loadExperimentRecords()
      router.push('/home')
    } else {
      errorMessage.value = data.message
    }
  } catch (error) {
    errorMessage.value = '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 30%, #a855f7 70%, #6366f1 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-page::before {
  content: '';
  position: absolute;
  top: -30%;
  left: -20%;
  width: 600px;
  height: 600px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  filter: blur(60px);
}

.login-page::after {
  content: '';
  position: absolute;
  bottom: -30%;
  right: -20%;
  width: 500px;
  height: 500px;
  background: rgba(168, 85, 247, 0.15);
  border-radius: 50%;
  filter: blur(50px);
}

.login-card {
  width: 100%;
  max-width: 440px;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-icon {
  color: #1890ff;
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-bottom: 16px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 4px 11px;
}

.login-form :deep(.el-input__inner) {
  font-size: 15px;
}

.login-form :deep(.el-input__prefix .el-icon) {
  color: #909399;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
}

.message-box {
  margin-top: 16px;
  border-radius: 8px;
  padding: 12px 16px;
}

.message-box.error {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
}

.message-box.success {
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
}

.message-content {
  display: flex;
  align-items: center;
}

.error-icon {
  color: #ff4d4f;
  font-size: 14px;
  font-weight: bold;
  margin-right: 8px;
}

.success-icon {
  color: #52c41a;
  font-size: 14px;
  font-weight: bold;
  margin-right: 8px;
}

.message-text {
  font-size: 14px;
  color: #ff4d4f;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-link {
  color: #1890ff;
  text-decoration: none;
  margin-left: 4px;
}

.register-link:hover {
  text-decoration: underline;
}
</style>