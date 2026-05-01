<template>
  <div class="progress-page">
    <div class="page-header">
      <h1>学习进度</h1>
      <p>查看您的学习进度和成就</p>
    </div>

    <div class="progress-container">
      <el-card class="stats-card">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon blue">📊</div>
            <div class="stat-info">
              <span class="stat-value">{{ totalExperiments }}</span>
              <span class="stat-label">漏洞模块总数</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon green">✅</div>
            <div class="stat-info">
              <span class="stat-value">{{ completedExperiments }}</span>
              <span class="stat-label">已完成模块</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon orange">🎯</div>
            <div class="stat-info">
              <span class="stat-value">{{ progressPercent }}%</span>
              <span class="stat-label">完成进度</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon purple">🔥</div>
            <div class="stat-info">
              <span class="stat-value">{{ totalAttempts }}</span>
              <span class="stat-label">总尝试次数</span>
            </div>
          </div>
        </div>

        <div class="progress-overview">
          <div class="progress-bar-wrap">
            <div class="progress-label">总体进度</div>
            <el-progress 
              :percentage="progressPercent" 
              :stroke-width="12"
              :show-text="true"
              stroke-color="#22c55e"
              class="main-progress"
            />
          </div>
        </div>
      </el-card>

      <el-card class="list-card">
        <h2>学习详情</h2>
        <div class="progress-list">
          <div v-for="vuln in vulnerabilities" :key="vuln.id" class="progress-item">
            <div class="progress-header">
              <div class="vuln-details">
                <span class="vuln-name">{{ vuln.name }}</span>
                <el-tag :type="getLevelTagType(vuln.level)" size="small">{{ vuln.levelText }}</el-tag>
              </div>
              <span :class="['status-badge', getStatus(vuln.type)]">
                {{ getStatusText(vuln.type) }}
              </span>
            </div>
            <div class="progress-bar-wrap">
              <el-progress 
                :percentage="getStatus(vuln.type) === 'completed' ? 100 : 0" 
                :stroke-width="8"
                :show-text="false"
                :stroke-color="getStatus(vuln.type) === 'completed' ? '#22c55e' : '#475569'"
                class="mini-progress"
              />
            </div>
            <div v-if="getRecord(vuln.type)" class="record-info">
              <span>尝试次数: {{ getRecord(vuln.type).attempt_count || 0 }}</span>
              <span>成功次数: {{ getRecord(vuln.type).success_count || 0 }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import store from '../store'

const vulnerabilities = ref([
  { name: 'SQL注入-入门', level: 'low', levelText: '入门', type: 'SQL注入-入门', id: 1 },
  { name: 'SQL注入-中级', level: 'medium', levelText: '进阶', type: 'SQL注入-中级', id: 2 },
  { name: 'SQL注入-高级', level: 'high', levelText: '专家', type: 'SQL注入-高级', id: 3 },
  { name: '反射型XSS', level: 'low', levelText: '入门', type: '反射型XSS', id: 4 },
  { name: '存储型XSS', level: 'medium', levelText: '进阶', type: '存储型XSS', id: 5 },
  { name: 'DOM型XSS', level: 'medium', levelText: '进阶', type: 'DOM型XSS', id: 6 },
  { name: 'PHP反序列化', level: 'high', levelText: '专家', type: 'PHP反序列化', id: 7 },
  { name: 'Python反序列化', level: 'high', levelText: '专家', type: 'Python反序列化', id: 8 },
  { name: '文件上传', level: 'medium', levelText: '进阶', type: '文件上传', id: 9 }
])

const totalExperiments = computed(() => vulnerabilities.value.length)

const completedExperiments = computed(() => {
  return vulnerabilities.value.filter(v => getStatus(v.type) === 'completed').length
})

const progressPercent = computed(() => {
  if (totalExperiments.value === 0) return 0
  return Math.round((completedExperiments.value / totalExperiments.value) * 100)
})

const totalAttempts = computed(() => {
  return store.state.experimentRecords.reduce((sum, r) => sum + (r.attempt_count || 0), 0)
})

const getRecord = (type) => {
  return store.state.experimentRecords.find(r => r.vulnerability_type === type)
}

const getStatus = (type) => {
  const record = getRecord(type)
  if (!record) return 'not_started'
  if (record.success_count > 0) return 'completed'
  if (record.start_time) {
    try {
      const elapsed = (Date.now() - new Date(record.start_time).getTime()) / 1000
      const isMarkedExpired = record.is_expired === 1 || record.is_expired === true
      
      if (elapsed < 3600 && !isMarkedExpired) {
        return 'in_progress'
      }
    } catch (e) {
      console.error('解析时间失败:', e)
    }
  }
  return 'not_started'
}

const getStatusText = (type) => {
  const status = getStatus(type)
  switch (status) {
    case 'not_started': return '未开始'
    case 'in_progress': return '进行中'
    case 'completed': return '已完成'
    default: return '未开始'
  }
}

const getLevelTagType = (level) => {
  switch (level) {
    case 'low': return 'success'
    case 'medium': return 'warning'
    case 'high': return 'danger'
    default: return 'info'
  }
}

onMounted(() => {
  store.actions.loadExperimentRecords()
})
</script>

<style scoped>
.progress-page {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #64748b;
}

.progress-container {
  max-width: 800px;
  margin: 0 auto;
}

.stats-card {
  margin-bottom: 1.5rem;
  border-radius: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
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

.stat-icon.blue {
  background: rgba(59, 130, 246, 0.1);
}

.stat-icon.green {
  background: rgba(34, 197, 94, 0.1);
}

.stat-icon.orange {
  background: rgba(245, 158, 11, 0.1);
}

.stat-icon.purple {
  background: rgba(139, 92, 246, 0.1);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
}

.progress-overview {
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.progress-bar-wrap {
  margin-bottom: 1rem;
}

.progress-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.main-progress {
  width: 100%;
}

.list-card {
  border-radius: 12px;
}

.list-card h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1.5rem;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-item {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 10px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.vuln-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.vuln-name {
  font-weight: 600;
  color: #1e293b;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-weight: 500;
}

.status-badge.not_started {
  background: #f1f5f9;
  color: #64748b;
}

.status-badge.in_progress {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.mini-progress {
  width: 100%;
}

.record-info {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
}
</style>