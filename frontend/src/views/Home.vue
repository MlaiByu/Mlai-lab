<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1>欢迎回来，{{ userName }}</h1>
          <p class="hero-subtitle">继续您的网络安全学习之旅</p>
          <div class="hero-stats">
            <div class="stat-item">
              <span class="stat-num">{{ userScore }}</span>
              <span class="stat-label">总积分</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">{{ completedExperiments }}/{{ totalExperiments }}</span>
              <span class="stat-label">已完成</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">{{ streakDays }}</span>
              <span class="stat-label">连续天数</span>
            </div>
          </div>
        </div>
        <div class="hero-visual">
          <div class="floating-card card-1">
            <el-icon :size="32"><Trophy /></el-icon>
            <span>最高得分</span>
          </div>
          <div class="floating-card card-2">
            <el-icon :size="32"><Star /></el-icon>
            <span>学习中</span>
          </div>
          <div class="floating-card card-3">
            <el-icon :size="32"><Target /></el-icon>
            <span>新挑战</span>
          </div>
        </div>
      </div>
      <div class="wave-container">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 60C240 120 480 0 720 60C960 120 1200 0 1440 60V120H0V60Z" fill="white"/>
        </svg>
      </div>
    </div>

    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon-wrapper blue">
            <el-icon :size="28"><Trophy /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ userScore }}</div>
            <div class="stat-name">我的分数</div>
          </div>
          <div class="stat-decoration">
            <el-icon :size="48" class="decor-icon"><Star /></el-icon>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon-wrapper green">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ completedExperiments }}<span class="stat-total">/{{ totalExperiments }}</span></div>
            <div class="stat-name">已完成挑战</div>
          </div>
          <el-progress 
            :percentage="completionRate" 
            :show-text="false" 
            stroke-width="8"
            class="mini-progress"
          />
        </div>
        
        <div class="stat-card">
          <div class="stat-icon-wrapper purple">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ completionRate }}%</div>
            <div class="stat-name">完成率</div>
          </div>
          <div class="progress-ring">
            <svg class="ring-svg" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" fill="none" stroke="#e5e7eb" stroke-width="8"/>
              <circle 
                cx="50" cy="50" r="42" fill="none" 
                stroke="url(#progressGradient)" 
                stroke-width="8"
                :stroke-dasharray="264"
                :stroke-dashoffset="264 * (1 - completionRate / 100)"
                stroke-linecap="round"
                transform="rotate(-90 50 50)"
              />
              <defs>
                <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#6366f1"/>
                  <stop offset="100%" stop-color="#8b5cf6"/>
                </linearGradient>
              </defs>
            </svg>
            <span class="ring-text">{{ completionRate }}%</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon-wrapper orange">
            <el-icon :size="28"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ totalAttempts }}</div>
            <div class="stat-name">总尝试次数</div>
          </div>
        </div>
      </div>
    </div>

    <div class="content-section">
      <div class="content-container">
        <div class="section-card activity-card">
          <div class="card-header">
            <div class="card-title">
              <div class="title-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <h2>学习动态</h2>
            </div>
            <span class="card-subtitle">实时追踪学习进度</span>
          </div>
        <div v-if="allRecentCompletions.length > 0" class="activity-list">
          <el-timeline mode="left">
            <el-timeline-item 
              v-for="(item, index) in allRecentCompletions.slice(0, 5)" 
              :key="index"
              :color="index === 0 ? '#6366f1' : '#9ca3af'"
            >
              <div class="timeline-card">
                <div class="timeline-header">
                  <div class="user-info">
                    <div class="user-avatar-small">
                      <el-icon><User /></el-icon>
                    </div>
                    <span class="user-name">{{ item.username }}</span>
                  </div>
                  <span class="timeline-time">{{ formatTimeAgo(item.first_success) }}</span>
                </div>
                <p class="timeline-text">完成了挑战 <span class="challenge-name">{{ item.name }}</span></p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
        <div v-else class="empty-state">
          <el-empty description="暂无学习动态" />
        </div>
      </div>

      <div class="section-card quick-start-card">
        <div class="card-header">
          <div class="card-title">
            <div class="title-icon">
              <el-icon><Zap /></el-icon>
            </div>
            <h2>快速开始</h2>
          </div>
          <router-link to="/vulnerabilities" class="view-all">查看全部 →</router-link>
        </div>
        <div class="quick-start-grid">
          <div 
            v-for="vuln in recommendedVulns" 
            :key="vuln.id"
            class="quick-start-item"
            @click="$router.push('/vulnerabilities')"
          >
            <div class="quick-start-icon" :class="getDifficultyClass(vuln.difficulty)">
              <el-icon :size="22"><Warning /></el-icon>
            </div>
            <div class="quick-start-info">
              <div class="quick-start-name">{{ vuln.name }}</div>
              <div class="quick-start-meta">
                <el-tag :class="['difficulty-tag', vuln.difficulty]">
                  {{ getDifficultyText(vuln.difficulty) }}
                </el-tag>
              </div>
            </div>
            <el-icon class="quick-start-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
      </div>
    </div>

    <div class="achievements-section">
      <div class="section-header">
        <h2>成就徽章</h2>
        <span class="section-subtitle">解锁您的学习成就</span>
      </div>
      <div class="achievements-grid">
        <div 
          v-for="achievement in achievements" 
          :key="achievement.id"
          :class="['achievement-card', { unlocked: achievement.unlocked, locked: !achievement.unlocked }]"
        >
          <div class="achievement-icon">
            <component :is="achievement.icon" style="font-size: 36px;" />
          </div>
          <div class="achievement-info">
            <h3>{{ achievement.name }}</h3>
            <p>{{ achievement.description }}</p>
          </div>
          <div v-if="achievement.unlocked" class="unlock-badge">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div v-else class="lock-badge">
            <el-icon><Lock /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  Trophy, CircleCheck, TrendCharts, Clock, Star, Warning, Aim,
  ArrowRight, User, Lock
} from '@element-plus/icons-vue'
import store from '../store'
import { users as usersApi } from '../api'
import { formatTimeAgo } from '../utils/date'

const allRecentCompletions = ref([])
const vulnerabilities = ref([])

const loadVulnerabilities = async () => {
  try {
    const response = await fetch('/api/experiment/vulnerabilities')
    const data = await response.json()
    if (data.success) {
      vulnerabilities.value = data.vulnerabilities
    }
  } catch (error) {
    console.error('Failed to load vulnerabilities:', error)
  }
}

const totalExperiments = computed(() => vulnerabilities.value.length)

const getVulnStatus = (vulnId) => {
  if (!store.state.user) return 'pending'
  const record = store.state.experimentRecords.find(r => r.vulnerability_id === vulnId)
  if (!record) return 'pending'
  if (record.success >= 1 || record.success === true) return 'completed'
  return 'pending'
}

const completedExperiments = computed(() =>
  vulnerabilities.value.filter(v => getVulnStatus(v.id) === 'completed').length
)

const completionRate = computed(() => {
  if (totalExperiments.value === 0) return 0
  return Math.round((completedExperiments.value / totalExperiments.value) * 100)
})

const totalAttempts = computed(() => {
  return store.state.experimentRecords.reduce((sum, r) => sum + (r.attempt_count || 0), 0)
})

const userScore = computed(() => store.state.user?.score || 0)
const userName = computed(() => store.state.user?.username || '')

const streakDays = computed(() => {
  const records = store.state.experimentRecords
  if (!records || records.length === 0) return 0
  
  const dates = records
    .filter(r => r.first_success)
    .map(r => {
      const date = new Date(r.first_success.replace(' ', 'T'))
      return isNaN(date.getTime()) ? null : date
    })
    .filter(d => d !== null)
    .sort((a, b) => b.getTime() - a.getTime())
  
  if (dates.length === 0) return 0
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const mostRecentDate = dates[0]
  mostRecentDate.setHours(0, 0, 0, 0)
  
  const daysDiff = Math.floor((today.getTime() - mostRecentDate.getTime()) / (1000 * 60 * 60 * 24))
  
  if (daysDiff > 1) return 0
  
  let streak = 1
  for (let i = 0; i < dates.length - 1; i++) {
    const current = dates[i]
    const next = dates[i + 1]
    current.setHours(0, 0, 0, 0)
    next.setHours(0, 0, 0, 0)
    const diff = Math.floor((current.getTime() - next.getTime()) / (1000 * 60 * 60 * 24))
    if (diff === 1) {
      streak++
    } else {
      break
    }
  }
  
  return streak
})

const recommendedVulns = computed(() => {
  return vulnerabilities.value.slice(0, 4)
})

const achievements = computed(() => [
  { 
    id: 1, 
    name: '初出茅庐', 
    description: '完成第一个挑战', 
    icon: Trophy,
    unlocked: completedExperiments.value >= 1
  },
  { 
    id: 2, 
    name: '坚持不懈', 
    description: '连续学习7天', 
    icon: Clock,
    unlocked: streakDays.value >= 7
  },
  { 
    id: 3, 
    name: '学习达人', 
    description: '完成50%挑战', 
    icon: Star,
    unlocked: completionRate.value >= 50
  },
  { 
    id: 4, 
    name: '全能选手', 
    description: '完成所有挑战', 
    icon: Star,
    unlocked: completionRate.value === 100
  }
])

const getDifficultyClass = (difficulty) => {
  switch(difficulty) {
    case 'easy': return 'easy'
    case 'medium': return 'medium'
    case 'hard': return 'hard'
    default: return 'easy'
  }
}

const getDifficultyText = (difficulty) => {
  switch(difficulty) {
    case 'easy': return '简单'
    case 'medium': return '中等'
    case 'hard': return '困难'
    default: return difficulty
  }
}

const loadRecentCompletions = async (retryCount = 0) => {
  try {
    const response = await usersApi.getRecentCompletions()
    if (response.success) {
      allRecentCompletions.value = response.data
    }
  } catch (error) {
    if (retryCount < 3) {
      setTimeout(() => {
        loadRecentCompletions(retryCount + 1)
      }, 500 * (retryCount + 1))
    }
  }
}

onMounted(async () => {
  await loadVulnerabilities()
  await store.actions.loadExperimentRecords()
  setTimeout(() => {
    loadRecentCompletions()
  }, 300)
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f0f2f5;
  width: 100%;
}

.hero-section {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  padding: 60px 40px;
  min-height: 400px;
  position: relative;
  overflow: hidden;
  width: 100%;
}

.hero-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
  width: 100%;
}

.hero-text {
  flex: 1;
  padding-right: 40px;
}

.hero-text h1 {
  color: white;
  font-size: 42px;
  font-weight: 700;
  margin: 0 0 12px 0;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.hero-subtitle {
  color: rgba(255, 255, 255, 0.85);
  font-size: 18px;
  margin: 0 0 32px 0;
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 32px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 20px 32px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-item {
  text-align: center;
}

.stat-num {
  display: block;
  color: white;
  font-size: 28px;
  font-weight: 700;
}

.stat-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
}

.hero-visual {
  position: relative;
  width: 400px;
  height: 300px;
}

.floating-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #6366f1;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: float 6s ease-in-out infinite;
}

.floating-card span {
  font-size: 13px;
  font-weight: 600;
}

.card-1 {
  top: 20px;
  left: 20px;
  animation-delay: 0s;
}

.card-2 {
  top: 100px;
  right: 40px;
  animation-delay: 2s;
}

.card-3 {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.wave-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

.wave-container svg {
  width: 100%;
  height: auto;
}

.stats-section {
  padding: 40px 24px;
  margin-top: -20px;
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  width: 100%;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrapper.blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #3b82f6;
}

.stat-icon-wrapper.green {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #22c55e;
}

.stat-icon-wrapper.purple {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #8b5cf6;
}

.stat-icon-wrapper.orange {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #f59e0b;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-total {
  font-size: 20px;
  color: #9ca3af;
  font-weight: 500;
}

.stat-name {
  font-size: 13px;
  color: #6b7280;
}

.stat-decoration {
  position: absolute;
  right: -20px;
  top: -20px;
  opacity: 0.05;
}

.decor-icon {
  color: #6366f1;
}

.mini-progress {
  width: 60px;
  margin-left: auto;
}

.progress-ring {
  position: relative;
  width: 60px;
  height: 60px;
  margin-left: auto;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 600;
  color: #6366f1;
}

.content-section {
  padding: 0 24px 40px;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  float: none;
  clear: both;
}

.content-container {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 24px;
  width: 100%;
}

.section-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-title h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.card-subtitle {
  color: #9ca3af;
  font-size: 14px;
}

.view-all {
  color: #6366f1;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;
}

.view-all:hover {
  color: #4f46e5;
}

.activity-list {
  margin-top: 8px;
}

.timeline-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 8px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar-small {
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

.user-name {
  font-weight: 600;
  color: #6366f1;
  font-size: 14px;
}

.timeline-time {
  font-size: 12px;
  color: #9ca3af;
}

.timeline-text {
  font-size: 14px;
  color: #4b5563;
  margin: 0;
}

.challenge-name {
  font-weight: 600;
  color: #22c55e;
}

.empty-state {
  padding: 40px 0;
}

.quick-start-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.quick-start-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: #f9fafb;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.quick-start-item:hover {
  background: #f3f4f6;
  transform: translateX(8px);
  border-color: rgba(99, 102, 241, 0.2);
}

.quick-start-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-start-icon.easy {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #22c55e;
}

.quick-start-icon.medium {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #f59e0b;
}

.quick-start-icon.hard {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #ef4444;
}

.quick-start-info {
  flex: 1;
}

.quick-start-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 15px;
  margin-bottom: 4px;
}

.quick-start-meta {
  display: flex;
  gap: 8px;
}

.difficulty-tag {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.difficulty-tag.easy {
  background: #dcfce7;
  color: #065f46;
}

.difficulty-tag.medium {
  background: #fef3c7;
  color: #92400e;
}

.difficulty-tag.hard {
  background: #fee2e2;
  color: #991b1b;
}

.quick-start-arrow {
  color: #9ca3af;
  font-size: 20px;
}

.achievements-section {
  padding: 40px 24px;
  background: linear-gradient(135deg, #f0f2f5 0%, #e5e7eb 100%);
}

.section-header {
  max-width: 1400px;
  margin: 0 auto 32px;
  text-align: center;
}

.section-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.section-subtitle {
  color: #6b7280;
  font-size: 14px;
}

.achievements-grid {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.achievement-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  position: relative;
}

.achievement-card:hover {
  transform: translateY(-4px);
}

.achievement-card.unlocked {
  border: 2px solid #6366f1;
}

.achievement-card.locked {
  opacity: 0.6;
  filter: grayscale(50%);
}

.achievement-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
}

.achievement-card.locked .achievement-icon {
  background: #e5e7eb;
  color: #9ca3af;
}

.achievement-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.achievement-info p {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}

.unlock-badge, .lock-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.unlock-badge {
  background: #dcfce7;
  color: #22c55e;
}

.lock-badge {
  background: #f3f4f6;
  color: #9ca3af;
}

@media (max-width: 1024px) {
  .content-section > div {
    grid-template-columns: 1fr;
  }
  
  .achievements-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
    gap: 40px;
  }
  
  .hero-text h1 {
    font-size: 28px;
  }
  
  .hero-stats {
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
  }
  
  .stat-divider {
    display: none;
  }
  
  .hero-visual {
    display: none;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .achievements-grid {
    grid-template-columns: 1fr;
  }
}
</style>
