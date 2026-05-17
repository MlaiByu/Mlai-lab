<template>
  <div class="progress-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>学习进度</h1>
          <p>查看您的学习进度和成就</p>
        </div>
      </div>
    </div>

    <div class="progress-container">
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon blue">
              <el-icon :size="28"><Grid /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ totalExperiments }}</div>
              <div class="stat-name">漏洞模块总数</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon green">
              <el-icon :size="28"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ completedExperiments }}</div>
              <div class="stat-name">已完成模块</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon purple">
              <el-icon :size="28"><Target /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ progressPercent }}%</div>
              <div class="stat-name">完成进度</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon orange">
              <el-icon :size="28"><Flame /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ totalAttempts }}</div>
              <div class="stat-name">总尝试次数</div>
            </div>
          </div>
        </div>

        <div class="progress-overview">
          <div class="overview-header">
            <span class="overview-title">总体进度</span>
            <span class="overview-percent">{{ completedExperiments }}/{{ totalExperiments }}</span>
          </div>
          <div class="progress-bar-wrapper">
            <el-progress 
              :percentage="progressPercent" 
              :stroke-width="20"
              :show-text="true"
              stroke-color="linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%)"
              class="main-progress"
            />
            <div class="progress-labels">
              <span>开始</span>
              <span>完成</span>
            </div>
          </div>
        </div>
      </div>

      <div class="detail-section">
        <div class="section-header">
          <h2>学习详情</h2>
        </div>
        
        <div class="progress-list">
          <div 
            v-for="category in categorizedVulnerabilities" 
            :key="category.name"
            class="category-section"
          >
            <div class="category-header">
              <div class="category-info">
                <div class="category-icon" :class="category.name">
                  <component :is="getCategoryIcon(category.name)" />
                </div>
                <div>
                  <span class="category-name">{{ category.name }}</span>
                  <span class="category-desc">{{ getCategoryDesc(category.name) }}</span>
                </div>
              </div>
              <div class="category-progress-info">
                <span class="category-progress-text">{{ category.completed }}/{{ category.total }}</span>
                <el-progress 
                  :percentage="Math.round((category.completed / category.total) * 100)" 
                  :stroke-width="8"
                  :show-text="false"
                  stroke-color="#6366f1"
                  class="category-progress-bar"
                />
              </div>
            </div>
            
            <div class="vuln-list">
              <div 
                v-for="vuln in category.vulnerabilities" 
                :key="vuln.id" 
                class="vuln-item"
              >
                <div class="vuln-main">
                  <div class="vuln-info">
                    <div :class="['status-dot', getStatus(vuln.id)]"></div>
                    <div class="vuln-content">
                      <span class="vuln-name">{{ vuln.name }}</span>
                      <el-tag :class="['difficulty-tag', vuln.difficulty]">
                        {{ getDifficultyText(vuln.difficulty) }}
                      </el-tag>
                    </div>
                  </div>
                  <div :class="['status-badge', getStatus(vuln.id)]">
                    <el-icon v-if="getStatus(vuln.id) === 'completed'"><CircleCheck /></el-icon>
                    <el-icon v-else-if="getStatus(vuln.id) === 'in_progress'"><Loading /></el-icon>
                    <span>{{ getStatusText(vuln.id) }}</span>
                  </div>
                </div>
                <div class="vuln-progress">
                  <el-progress 
                    :percentage="getStatus(vuln.id) === 'completed' ? 100 : getStatus(vuln.id) === 'in_progress' ? 50 : getStatus(vuln.id) === 'attempted' ? 30 : 0" 
                    :stroke-width="6"
                    :show-text="false"
                    :stroke-color="getStatus(vuln.id) === 'completed' ? '#22c55e' : getStatus(vuln.id) === 'in_progress' ? '#6366f1' : getStatus(vuln.id) === 'attempted' ? '#f59e0b' : '#e5e7eb'"
                  />
                </div>
                <div v-if="getRecord(vuln.id)" class="vuln-meta">
                  <span class="meta-item">
                    <el-icon :size="14"><Clock /></el-icon>
                    尝试 {{ getRecord(vuln.id).attempt_count || 0 }} 次
                  </span>
                  <span v-if="getRecord(vuln.id).first_success" class="meta-item success">
                    <el-icon :size="14"><Calendar /></el-icon>
                    {{ formatDateTime(getRecord(vuln.id).first_success) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Grid, CircleCheck, Aim, HotWater, Clock, Calendar, Loading, DataBoard, Cpu, Lock, Goods, Upload } from '@element-plus/icons-vue'
import store from '../store'
import { formatDateTime } from '../utils/date'

const vulnerabilities = ref([
  { name: 'SQL注入-入门', difficulty: 'easy', id: 1, category: 'sqli' },
  { name: 'SQL注入-中级', difficulty: 'medium', id: 2, category: 'sqli' },
  { name: 'SQL注入-高级', difficulty: 'hard', id: 3, category: 'sqli' },
  { name: '反射型XSS', difficulty: 'easy', id: 4, category: 'xss' },
  { name: '存储型XSS', difficulty: 'medium', id: 5, category: 'xss' },
  { name: 'DOM型XSS', difficulty: 'medium', id: 6, category: 'xss' },
  { name: 'PHP反序列化', difficulty: 'hard', id: 7, category: 'deserialization' },
  { name: '文件上传', difficulty: 'medium', id: 8, category: 'upload' },
  { name: 'CSRF-Easy', difficulty: 'easy', id: 9, category: 'csrf' },
  { name: 'CSRF-Hard', difficulty: 'hard', id: 10, category: 'csrf' },
  { name: 'Python反序列化', difficulty: 'hard', id: 11, category: 'deserialization' }
])

const categoryNames = {
  sqli: 'SQL注入',
  xss: 'XSS攻击',
  csrf: 'CSRF攻击',
  deserialization: '反序列化',
  upload: '文件上传'
}

const categoryDescs = {
  sqli: '学习SQL注入的原理和各种攻击技巧',
  xss: '掌握跨站脚本攻击的各种形式',
  csrf: '理解跨站请求伪造的原理',
  deserialization: '深入学习反序列化漏洞',
  upload: '学习文件上传漏洞的利用'
}

const getCategoryDesc = (category) => {
  return categoryDescs[category] || ''
}

const getCategoryIcon = (categoryName) => {
  const icons = {
    'SQL注入': DataBoard,
    'XSS攻击': Cpu,
    'CSRF攻击': Lock,
    '反序列化': Goods,
    '文件上传': Upload
  }
  return icons[categoryName] || DataBoard
}

const totalExperiments = computed(() => vulnerabilities.value.length)

const completedExperiments = computed(() => {
  return vulnerabilities.value.filter(v => getStatus(v.id) === 'completed').length
})

const progressPercent = computed(() => {
  if (totalExperiments.value === 0) return 0
  return Math.round((completedExperiments.value / totalExperiments.value) * 100)
})

const totalAttempts = computed(() => {
  return store.state.experimentRecords.reduce((sum, r) => sum + (r.attempt_count || 0), 0)
})

const categorizedVulnerabilities = computed(() => {
  const categories = {}
  vulnerabilities.value.forEach(vuln => {
    const categoryName = categoryNames[vuln.category] || vuln.category
    if (!categories[categoryName]) {
      categories[categoryName] = {
        name: categoryName,
        vulnerabilities: [],
        completed: 0,
        total: 0
      }
    }
    categories[categoryName].vulnerabilities.push(vuln)
    categories[categoryName].total++
    if (getStatus(vuln.id) === 'completed') {
      categories[categoryName].completed++
    }
  })
  return Object.values(categories)
})

const getRecord = (vulnId) => {
  return store.state.experimentRecords.find(r => r.vulnerability_id === vulnId)
}

const isContainerRunning = (vulnId) => {
  return store.state.runningContainers.some(c => c.vulnerability_id === vulnId)
}

const getStatus = (vulnId) => {
  const record = getRecord(vulnId)
  
  if (!record) return 'not_started'
  if (record.success >= 1 || record.success === true) return 'completed'
  if (isContainerRunning(vulnId)) return 'in_progress'
  if (record.attempt_count > 0) return 'attempted'
  return 'not_started'
}

const getStatusText = (vulnId) => {
  const status = getStatus(vulnId)
  switch (status) {
    case 'not_started': return '未开始'
    case 'attempted': return '已尝试'
    case 'in_progress': return '进行中'
    case 'completed': return '已完成'
    default: return '未开始'
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

onMounted(() => {
  store.actions.loadExperimentRecords()
})
</script>

<style scoped>
.progress-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f2f5 0%, #ede9fe 30%, #f0f2f5 100%);
  position: relative;
}

.page-header {
  background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 50%, #a855f7 100%);
  padding: 50px 24px;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: -40%;
  left: -15%;
  width: 500px;
  height: 500px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 50%;
  filter: blur(50px);
}

.page-header::after {
  content: '';
  position: absolute;
  bottom: -25%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: rgba(168, 85, 247, 0.2);
  border-radius: 50%;
  filter: blur(35px);
}

.header-content {
  max-width: 900px;
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

.progress-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px;
}

.stats-section {
  background: white;
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 22px;
  background: white;
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.15);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #3b82f6;
}

.stat-icon.green {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #22c55e;
}

.stat-icon.purple {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #8b5cf6;
}

.stat-icon.orange {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #f59e0b;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-name {
  font-size: 13px;
  color: #6b7280;
}

.progress-overview {
  padding-top: 20px;
  border-top: 1px solid #f3f4f6;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.overview-title {
  font-weight: 600;
  color: #6b7280;
}

.overview-percent {
  font-weight: 600;
  color: #6366f1;
  font-size: 16px;
}

.progress-bar-wrapper {
  position: relative;
}

.main-progress {
  margin-bottom: 8px;
}

.main-progress :deep(.el-progress__text) {
  font-weight: 700;
  font-size: 18px;
  color: #6366f1;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #9ca3af;
}

.detail-section {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.section-header {
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.category-section {
  background: #f9fafb;
  border-radius: 16px;
  padding: 20px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.category-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.category-icon.SQL注入 {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #3b82f6;
}

.category-icon.XSS攻击 {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #22c55e;
}

.category-icon.CSRF攻击 {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #f59e0b;
}

.category-icon.反序列化 {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #8b5cf6;
}

.category-icon.文件上传 {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #ef4444;
}

.category-info span.category-name {
  display: block;
  font-weight: 600;
  color: #1f2937;
  font-size: 16px;
  margin-bottom: 2px;
}

.category-info span.category-desc {
  font-size: 13px;
  color: #9ca3af;
}

.category-progress-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.category-progress-text {
  font-weight: 600;
  color: #6366f1;
}

.category-progress-bar {
  width: 100px;
}

.vuln-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.vuln-item {
  background: white;
  border-radius: 16px;
  padding: 20px;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.vuln-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.vuln-item:hover {
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.1);
  transform: translateX(4px);
}

.vuln-item:hover::before {
  transform: scaleY(1);
}

.vuln-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.vuln-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.not_started {
  background: #d1d5db;
}

.status-dot.attempted {
  background: #f59e0b;
}

.status-dot.in_progress {
  background: #6366f1;
  animation: pulse 2s infinite;
}

.status-dot.completed {
  background: #22c55e;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.vuln-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vuln-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 15px;
}

.difficulty-tag {
  padding: 4px 12px;
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

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.status-badge.not_started {
  background: #f3f4f6;
  color: #9ca3af;
}

.status-badge.attempted {
  background: #fef3c7;
  color: #f59e0b;
}

.status-badge.in_progress {
  background: #e0e7ff;
  color: #6366f1;
}

.status-badge.completed {
  background: #dcfce7;
  color: #22c55e;
}

.vuln-progress {
  margin-bottom: 12px;
}

.vuln-meta {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: #9ca3af;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item.success {
  color: #22c55e;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .category-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .category-progress-info {
    width: 100%;
    align-items: flex-start;
  }
  
  .category-progress-bar {
    width: 100%;
  }
}
</style>
