<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="login-bg"></div>
      
      <el-card class="login-card" shadow="none">
        <div class="logo-section">
          <div class="logo-icon">🛡️</div>
          <h1>欢迎来到 Mlai-Lab</h1>
          <p>Web安全漏洞测试平台</p>
        </div>
        
        <el-form :model="loginForm" @submit.prevent="handleLogin" class="login-form">
          <el-form-item>
            <el-input 
              v-model="loginForm.username" 
              placeholder="用户名"
              prefix-icon="User"
              size="large"
              required
            />
          </el-form-item>
          
          <el-form-item>
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="密码"
              prefix-icon="Lock"
              size="large"
              required
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-btn"
              :loading="loading"
              size="large"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-alert 
          v-if="errorMessage" 
          type="error" 
          :title="errorMessage"
          show-icon
          class="error-alert"
        />
        
        <div class="register-link">
          <span>还没有账号？</span>
          <el-button type="text" @click="goToRegister" class="register-btn">立即注册</el-button>
        </div>
        
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
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
      const user = { 
        id: data.user.id,
        username: data.user.username,
        role: data.user.role,
        token: data.user.token
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

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.login-container {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 30px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #e8f4f8 50%, #f0fdf4 100%);
  position: relative;
}

.login-bg {
  position: absolute;
  top: -30%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #38bdf8 0%, #22d3ee 50%, #14b8a6 100%);
  border-radius: 50%;
  opacity: 0.1;
  filter: blur(60px);
}

.login-card {
  position: relative;
  z-index: 1;
  border-radius: 24px;
  padding: 3rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.logo-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.logo-section h1 {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.logo-section p {
  color: #94a3b8;
  font-size: 0.9rem;
}

.login-form {
  margin-bottom: 1.25rem;
}

.login-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.error-alert {
  margin-bottom: 1rem;
}

.register-link {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  color: #64748b;
  font-size: 0.95rem;
}

.register-btn {
  color: #0ea5e9;
  font-weight: 500;
}

.register-btn:hover {
  color: #0284c7;
}



:deep(.el-input__wrapper) {
  border-radius: 14px;
  background: #f8fafc;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}
</style>
