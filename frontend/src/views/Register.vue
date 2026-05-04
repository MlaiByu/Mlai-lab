<template>
  <div class="register-container">
    <div class="register-bg"></div>
    
    <el-card class="register-card" shadow="none">
      <div class="logo-section">
        <h1>用户注册</h1>
        <p>创建您的 Mlai-Lab 账号</p>
      </div>
      
      <el-form :model="registerForm" @submit.prevent="handleRegister" class="register-form">
        <el-form-item label="用户名" label-width="80px">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
            required
          />
        </el-form-item>
        
        <el-form-item label="密码" label-width="80px">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            required
          />
        </el-form-item>
        
        <el-form-item label="确认密码" label-width="80px">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            size="large"
            required
          />
        </el-form-item>
        
        <el-form-item label="角色" label-width="80px">
          <el-select v-model="registerForm.role" size="large" placeholder="请选择角色">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            class="register-btn"
            :loading="loading"
            size="large"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-alert 
        v-if="message" 
        :type="messageType === 'success' ? 'success' : 'error'" 
        :title="message"
        show-icon
        class="message-alert"
      />
      
      <div class="login-link">
        <span>已有账号？</span>
        <el-button type="text" @click="goToLogin" class="login-btn">立即登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'student'
})

const loading = ref(false)
const message = ref('')
const messageType = ref('')

const handleRegister = async () => {
  if (registerForm.password !== registerForm.confirmPassword) {
    message.value = '两次输入的密码不一致'
    messageType.value = 'error'
    return
  }
  
  loading.value = true
  message.value = ''
  
  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: registerForm.username,
        password: registerForm.password,
        role: registerForm.role
      })
    })
    const data = await response.json()
    
    if (data.success) {
      message.value = '注册成功，请登录'
      messageType.value = 'success'
      setTimeout(() => {
        router.push('/')
      }, 2000)
    } else {
      message.value = data.message
      messageType.value = 'error'
    }
  } catch (error) {
    message.value = '注册失败，请重试'
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e8f4f8 50%, #f0fdf4 100%);
  position: relative;
  overflow: hidden;
}

.register-bg {
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #a7f3d0 0%, #67e8f9 50%, #38bdf8 100%);
  border-radius: 50%;
  opacity: 0.1;
  filter: blur(60px);
}

.register-card {
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
  margin-bottom: 2.5rem;
}

.logo-section h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.logo-section p {
  color: #94a3b8;
  font-size: 0.9rem;
}

.register-form {
  margin-bottom: 1.25rem;
}

.register-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.message-alert {
  margin-bottom: 1rem;
}

.login-link {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  color: #64748b;
  font-size: 0.95rem;
}

.login-btn {
  color: #0ea5e9;
  font-weight: 500;
}

.login-btn:hover {
  color: #0284c7;
}

:deep(.el-input__wrapper) {
  border-radius: 14px;
  background: #f8fafc;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

:deep(.el-select__wrapper) {
  border-radius: 14px;
  background: #f8fafc;
}
</style>
