<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-bg"></div>
      <div class="hero-content">
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
          <div class="stat-icon total"></div>
          <div class="stat-content">
            <div class="stat-value">{{ totalExperiments }}</div>
            <div class="stat-label">总漏洞数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon completed"></div>
          <div class="stat-content">
            <div class="stat-value">{{ completedExperiments }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon in-progress"></div>
          <div class="stat-content">
            <div class="stat-value">{{ inProgressExperiments }}</div>
            <div class="stat-label">进行中</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending"></div>
          <div class="stat-content">
            <div class="stat-value">{{ pendingExperiments }}</div>
            <div class="stat-label">未完成</div>
          </div>
        </div>
      </div>
    </div>

    <div class="recent-section">
      <div class="recent-container">
        <h2 class="section-title">学习动态</h2>
        <div v-if="allRecentCompletions.length > 0" class="recent-list">
          <div v-for="item in allRecentCompletions" :key="`${item.user_id}-${item.vulnerability_type}`" class="recent-item">
            <div class="recent-icon completed">🎉</div>
            <div class="recent-info">
              <div class="recent-name">
                <span class="user-name">{{ item.username }}</span>
                <span class="completed-text">完成了</span>
                <span class="exp-name">{{ item.vulnerability_type }}</span>
              </div>
              <div class="recent-time">{{ formatTime(item.completed_at) }}</div>
            </div>
            <div class="recent-badge">+1</div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">🎯</div>
          <div class="empty-text">还没有用户完成任何实验</div>
          <div class="empty-hint">成为第一个完成实验的用户吧！</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import store from '../store'
import { vulnerabilities } from '../data/vulnerabilities'
import { users as usersApi } from '../api'

const totalExperiments = computed(() => vulnerabilities.length)

const allRecentCompletions = ref([])

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

const completedExperiments = computed(() =>
  vulnerabilities.filter(v => getVulnStatus(v.name) === 'completed').length
)

const inProgressExperiments = computed(() =>
  vulnerabilities.filter(v => getVulnStatus(v.name) === 'in_progress').length
)

const pendingExperiments = computed(() =>
  vulnerabilities.filter(v => getVulnStatus(v.name) === 'pending').length
)

const formatTime = (timeStr) => {
  if (!timeStr) return '刚刚'
  
  try {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    
    return date.toLocaleDateString('zh-CN')
  } catch {
    return timeStr
  }
}

const loadRecentCompletions = async () => {
  try {
    const response = await usersApi.getRecentCompletions()
    if (response.success) {
      allRecentCompletions.value = response.data
    }
  } catch (error) {
    console.error('加载学习动态失败:', error)
  }
}

onMounted(() => {
  store.actions.loadExperimentRecords()
  loadRecentCompletions()
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

.recent-section {
  padding: 3rem 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.recent-container {
  max-width: 800px;
  margin: 0 auto;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1.5rem;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: white;
  border-radius: 12px;
  border: 1px solid rgba(34, 197, 94, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  transition: all 0.2s ease;
}

.recent-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.recent-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.recent-icon.completed {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
}

.recent-info {
  flex: 1;
}

.recent-name {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.user-name {
  color: #0ea5e9;
  font-weight: 600;
}

.completed-text {
  color: #64748b;
}

.exp-name {
  color: #22c55e;
  font-weight: 600;
}

.recent-time {
  font-size: 0.875rem;
  color: #94a3b8;
}

.recent-badge {
  padding: 0.375rem 0.75rem;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 20px;
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  background: white;
  border-radius: 16px;
  border: 1px dashed #e2e8f0;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.125rem;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.875rem;
  color: #94a3b8;
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

  .recent-section {
    padding: 2rem 1rem;
  }
}
</style>
