<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="hero-icon">🛡️</div>
        <h1>欢迎来到 Mlai-Lab</h1>
        <p class="hero-subtitle">现代化 Web 安全漏洞测试平台</p>
        <p class="hero-description">
          通过实践学习 Web 安全知识。本平台提供多种安全挑战，帮助您了解常见的 Web 漏洞。
        </p>
      </div>
    </div>

    <div class="stats-section">
      <div class="stats-container">
        <div class="stat-card">
          <div class="stat-icon total">📊</div>
          <div class="stat-content">
            <div class="stat-value">{{ totalExperiments }}</div>
            <div class="stat-label">总漏洞数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon completed">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ completedExperiments }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon in-progress">⏳</div>
          <div class="stat-content">
            <div class="stat-value">{{ inProgressExperiments }}</div>
            <div class="stat-label">进行中</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending">📝</div>
          <div class="stat-content">
            <div class="stat-value">{{ pendingExperiments }}</div>
            <div class="stat-label">未完成</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import store from '../store'

const vulnerabilityTypes = [
  { name: 'SQL注入-入门', type: 'SQL注入-入门' },
  { name: 'SQL注入-中级', type: 'SQL注入-中级' },
  { name: 'SQL注入-高级', type: 'SQL注入-高级' },
  { name: '反射型XSS', type: '反射型XSS' },
  { name: '存储型XSS', type: '存储型XSS' },
  { name: 'DOM型XSS', type: 'DOM型XSS' },
  { name: 'PHP反序列化', type: 'PHP反序列化' },
  { name: 'Python反序列化', type: 'Python反序列化' },
  { name: '文件上传', type: '文件上传' }
]

const totalExperiments = computed(() => vulnerabilityTypes.length)

const getVulnStatus = (type) => {
  if (!store.state.user) return 'pending'
  
  const record = store.state.experimentRecords.find(r => r.vulnerability_type === type)
  if (!record) return 'pending'
  
  if (record.success_count > 0) return 'completed'
  
  if (record.is_expired) return 'pending'
  
  if (record.start_time) {
    try {
      const elapsed = (Date.now() - new Date(record.start_time).getTime()) / 1000
      if (elapsed < 3600) return 'in_progress'
    } catch {}
  }
  
  return 'pending'
}

const completedExperiments = computed(() => {
  return vulnerabilityTypes.filter(v => getVulnStatus(v.type) === 'completed').length
})

const inProgressExperiments = computed(() => {
  return vulnerabilityTypes.filter(v => getVulnStatus(v.type) === 'in_progress').length
})

const pendingExperiments = computed(() => {
  return vulnerabilityTypes.filter(v => getVulnStatus(v.type) === 'pending').length
})

onMounted(() => {
  store.actions.loadExperimentRecords()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f9ff 0%, #ecfeff 50%, #f0fdf4 100%);
}

.hero-section {
  position: relative;
  padding: 5rem 2rem;
  text-align: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(ellipse at top, rgba(14, 165, 233, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
}

.hero-icon {
  font-size: 5rem;
  margin-bottom: 1.5rem;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.hero-content h1 {
  font-size: 2.75rem;
  font-weight: 700;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.75rem;
}

.hero-subtitle {
  font-size: 1.375rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.hero-description {
  font-size: 1rem;
  color: #94a3b8;
  line-height: 1.6;
}

.stats-section {
  padding: 3rem 2rem;
  background: white;
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  border: 1px solid rgba(14, 165, 233, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.total {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
}

.stat-icon.in-progress {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
}

.stat-icon.pending {
  background: linear-gradient(135deg, rgba(108, 117, 125, 0.1) 0%, rgba(73, 80, 87, 0.1) 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.25rem;
}

@media (max-width: 768px) {
  .stats-section {
    padding: 2rem 1rem;
  }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
}
</style>
