<template>
  <div class="register-page">
    <el-card class="register-card">
      <div class="register-header">
        <el-icon :size="48" class="register-icon"><Plus /></el-icon>
        <h1>用户注册</h1>
        <p>创建您的 Mlai-Lab 账号</p>
      </div>

      <el-form :model="registerForm" class="register-form">
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名"
            size="large"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" class="register-btn" :loading="loading" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
        
        <div v-if="message" :class="['message-box', messageType]">
          <div :class="['message-content']">
            <span v-if="messageType === 'error'" class="error-icon">✕</span>
            <span v-else class="success-icon">✓</span>
            <span class="message-text">{{ message }}</span>
          </div>
        </div>
      </el-form>

      <div class="register-footer">
        <span>已有账号？</span>
        <router-link to="/" class="login-link">立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElCard, ElForm, ElFormItem, ElInput, ElButton, ElAlert } from 'element-plus'
import { Plus, User, Lock } from '@element-plus/icons-vue'

const router = useRouter()

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
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
        password: registerForm.password
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
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #10b981 0%, #34d399 30%, #6ee7b7 70%, #10b981 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.register-page::before {
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

.register-page::after {
  content: '';
  position: absolute;
  bottom: -30%;
  right: -20%;
  width: 500px;
  height: 500px;
  background: rgba(16, 185, 129, 0.15);
  border-radius: 50%;
  filter: blur(50px);
}

.register-card {
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

.register-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #10b981 0%, #34d399 50%, #6ee7b7 100%);
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-icon {
  color: #52c41a;
  margin-bottom: 16px;
}

.register-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.register-header p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.register-form {
  margin-bottom: 16px;
}

.register-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 4px 11px;
}

.register-form :deep(.el-input__inner) {
  font-size: 15px;
}

.register-form :deep(.el-input__prefix .el-icon) {
  color: #909399;
}

.register-btn {
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
  background-color: #fef0f0;
  border: 1px solid #ffccc7;
}

.message-box.success {
  background-color: #f0f9eb;
  border: 1px solid #b7eb8f;
}

.message-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}

.success-icon {
  color: #67c23a;
  font-weight: bold;
  font-size: 16px;
}

.message-text {
  font-size: 14px;
}

.message-box.error .message-text {
  color: #f56c6c;
}

.message-box.success .message-text {
  color: #67c23a;
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.login-link {
  color: #1890ff;
  text-decoration: none;
  margin-left: 4px;
}

.login-link:hover {
  text-decoration: underline;
}
</style>