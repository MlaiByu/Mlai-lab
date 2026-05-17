<template>
  <div class="challenges-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>漏洞挑战</h1>
          <p>选择一个漏洞类型开始挑战，提升您的安全技能</p>
        </div>
        <div class="header-stats">
          <div class="stat-box">
            <span class="stat-value">{{ completedCount }}</span>
            <span class="stat-label">已完成</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">{{ totalCount }}</span>
            <span class="stat-label">总挑战</span>
          </div>
        </div>
      </div>
    </div>

    <div class="challenges-container">
      <aside class="sidebar">
        <div class="sidebar-header">
          <el-icon :size="18"><Filter /></el-icon>
          <span>漏洞分类</span>
        </div>
        <div class="category-list">
          <div
            v-for="category in categories"
            :key="category.id"
            :class="['category-item', { active: selectedCategory === category.id }]"
            @click="selectCategory(category.id)"
          >
            <div class="category-icon-wrapper" :class="category.id">
              <component :is="getCategoryIcon(category.id)" />
            </div>
            <div class="category-info">
              <span class="category-name">{{ category.name }}</span>
              <span class="category-desc">{{ getCategoryDescriptionShort(category.id) }}</span>
            </div>
            <span class="category-count">{{ getCategoryCount(category.id) }}</span>
          </div>
        </div>
      </aside>

      <main class="main-content">
        <div class="content-header">
          <div class="header-title">
            <h2>{{ currentCategoryName }}</h2>
            <span class="category-count-badge">{{ filteredVulnerabilities.length }} 个挑战</span>
          </div>
          <p class="category-desc">{{ getCategoryDescription(selectedCategory) }}</p>
        </div>
        
        <div class="challenges-grid">
          <el-card
            v-for="vuln in filteredVulnerabilities"
            :key="vuln.id"
            :class="['challenge-card', getStatus(vuln.id)]"
            @click="openChallengeModal(vuln)"
            hover
          >
            <div class="card-inner">
              <div class="card-header">
                <div class="difficulty-tag" :class="vuln.difficulty">
                  <el-icon :size="14"><Tag /></el-icon>
                  {{ getDifficultyText(vuln.difficulty) }}
                </div>
                <div :class="['status-indicator', getStatus(vuln.id)]">
                  <el-icon v-if="getStatus(vuln.id) === 'completed'"><CircleCheck /></el-icon>
                  <el-icon v-else-if="getStatus(vuln.id) === 'in_progress'"><Loading /></el-icon>
                  <el-icon v-else><CircleClose /></el-icon>
                </div>
              </div>
              <h3 class="challenge-name">{{ vuln.name }}</h3>
              <p class="challenge-desc">{{ getVulnDescription(vuln.id) }}</p>
              <div class="card-footer">
                <span class="status-text">{{ getStatusText(vuln.id) }}</span>
                <el-icon class="arrow-icon"><ChevronRight /></el-icon>
              </div>
            </div>
          </el-card>
        </div>

        <div v-if="filteredVulnerabilities.length === 0" class="empty-state">
          <el-empty description="该分类暂无挑战" />
        </div>
      </main>
    </div>

    <el-dialog 
      v-model="showChallengeModal"
      :title="selectedChallenge?.name"
      width="700px"
      class="challenge-dialog"
    >
      <div class="modal-content">
        <div class="flag-info">
          <div class="flag-icon">
            <el-icon :size="28"><Flag /></el-icon>
          </div>
          <div class="flag-text">
            <p class="flag-title">FLAG格式</p>
            <code class="flag-format">Mlai{xxxxxx}</code>
          </div>
        </div>

        <div class="env-section">
          <div class="section-header">
            <h3>
              <el-icon><Monitor /></el-icon>
              靶场环境
            </h3>
          </div>
          
          <div v-if="showOtherContainer" class="other-container">
            <div class="warning-box">
              <div class="warning-content">
                <span class="warning-icon">⚠</span>
                <span class="warning-text">您当前已有运行中的实验: {{ showOtherContainer.vulnerability_name }}</span>
              </div>
            </div>
            <div class="env-details">
              <span>容器ID: {{ (showOtherContainer.container_id || showOtherContainer.id)?.slice(0, 12) }}...</span>
            </div>
            <el-button type="danger" class="danger-btn" @click="closeOtherContainer">
              <el-icon><TurnOff /></el-icon>
              关闭当前实验
            </el-button>
          </div>
          
          <div v-else-if="!currentContainer" class="start-section">
            <div class="start-card">
              <div class="start-icon">
                <el-icon :size="48"><VideoPlay /></el-icon>
              </div>
              <h4>准备开始挑战</h4>
              <p>点击下方按钮启动靶场环境</p>
              <el-button 
                type="primary" 
                size="large"
                :loading="isStarting"
                @click="startEnvironment"
                class="start-btn"
              >
                <el-icon><Play /></el-icon>
                启动靶场环境
              </el-button>
            </div>
          </div>
          
          <div v-else class="running-section">
            <div class="running-header">
              <div class="running-status">
                <span class="status-dot pulse"></span>
                <span class="status-text">运行中</span>
              </div>
              <span class="countdown">{{ remainingTime }}</span>
            </div>
            <div class="env-url">
              <el-icon><Link /></el-icon>
              <a :href="getTargetUrl()" target="_blank" class="url-link">{{ getTargetUrl() }}</a>
            </div>
            <div class="env-info">
              <span class="info-item">
                <el-icon><InfoFilled /></el-icon>
                容器ID: {{ (currentContainer.container_id || currentContainer.id)?.slice(0, 12) }}...
              </span>
            </div>
            <el-button type="danger" class="stop-btn" @click="stopEnvironment">
              <el-icon><Box /></el-icon>
              停止环境
            </el-button>
          </div>
        </div>

        <div class="flag-submit-section">
          <div class="section-header">
            <h3>
              <el-icon><Send /></el-icon>
              提交Flag
            </h3>
          </div>
          <div class="flag-input-group">
            <el-input 
              v-model="flagInput" 
              placeholder="请输入Flag"
              @keyup.enter="submitFlag"
              class="flag-input"
            />
            <el-button 
              type="success" 
              :loading="isSubmitting"
              @click="submitFlag"
              class="submit-btn"
            >
              <el-icon><CircleCheck /></el-icon>
              提交
            </el-button>
          </div>
        </div>

        <div v-if="flagResult" :class="['message-box', flagResult.success ? 'success' : 'error']">
          <div class="message-content">
            <span v-if="flagResult.success" class="success-icon">✓</span>
            <span v-else class="error-icon">✕</span>
            <span class="message-text">{{ flagResult.message }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  Filter, PriceTag, CircleCheck, Loading, CircleClose, ArrowRight, Flag, Monitor, 
  VideoPlay, Box, Link, Message, TurnOff, InfoFilled, DataBoard, Cpu, Lock, Goods, Upload
} from '@element-plus/icons-vue'
import store from '../store'
import { experiment as experimentApi, container as containerApi } from '../api'

const categories = ref([
  { id: 'sqli', name: 'SQL注入' },
  { id: 'xss', name: 'XSS攻击' },
  { id: 'csrf', name: 'CSRF攻击' },
  { id: 'deserialization', name: '反序列化' },
  { id: 'upload', name: '文件上传' }
])

const vulnerabilities = ref([])
const showChallengeModal = ref(false)
const selectedChallenge = ref(null)
const flagInput = ref('')
const flagResult = ref(null)
const isSubmitting = ref(false)
const isStarting = ref(false)
const currentContainer = ref(null)
const selectedCategory = ref('sqli')
const remainingTime = ref('01:00:00')
const currentSessionId = ref('')
let countdownTimer = null

const vulnDescriptions = {
  1: '学习基础的SQL注入原理和攻击方法',
  2: '进阶SQL注入技巧，包含盲注等高级技术',
  3: '复杂SQL注入场景，需要综合利用多种技巧',
  4: '反射型XSS攻击，学习如何利用浏览器执行恶意脚本',
  5: '存储型XSS攻击，持久化攻击向量',
  6: 'DOM型XSS，利用客户端JavaScript漏洞',
  7: 'PHP反序列化漏洞，学习魔术方法和漏洞利用',
  8: '文件上传漏洞，绕过各种上传限制',
  9: '基础CSRF攻击，学习跨站请求伪造原理',
  10: '高级CSRF防护绕过技术',
  11: 'Python反序列化漏洞，利用pickle模块'
}

const getVulnDescription = (vulnId) => {
  return vulnDescriptions[vulnId] || '暂无描述'
}

const getCategoryIcon = (categoryId) => {
  const icons = {
    sqli: DataBoard,
    xss: Cpu,
    csrf: Lock,
    deserialization: Goods,
    upload: Upload
  }
  return icons[categoryId] || DataBoard
}

const getCategoryCount = (categoryId) => {
  return vulnerabilities.value.filter(v => v.category === categoryId).length
}

const getCategoryDescription = (categoryId) => {
  const descriptions = {
    sqli: 'SQL注入是一种常见的Web安全漏洞，攻击者通过在输入中注入SQL语句来获取或修改数据库中的数据。掌握SQL注入技术对于理解Web安全至关重要。',
    xss: '跨站脚本攻击（XSS）允许攻击者在网页中注入恶意脚本，窃取用户信息或执行恶意操作。学习XSS有助于理解前端安全防护机制。',
    csrf: '跨站请求伪造（CSRF）攻击诱使用户在已登录的情况下执行非预期的操作。理解CSRF有助于构建更安全的Web应用。',
    deserialization: '反序列化漏洞允许攻击者通过恶意构造的序列化数据来执行任意代码。这是一种高危漏洞，需要深入理解。',
    upload: '文件上传漏洞允许攻击者上传恶意文件到服务器并执行。学习文件上传漏洞有助于理解服务器端安全防护。'
  }
  return descriptions[categoryId] || ''
}

const getCategoryDescriptionShort = (categoryId) => {
  const descriptions = {
    sqli: '数据库攻击',
    xss: '客户端攻击',
    csrf: '请求伪造',
    deserialization: '代码执行',
    upload: '文件操作'
  }
  return descriptions[categoryId] || ''
}

const loadVulnerabilities = async () => {
  try {
    const response = await fetch('/api/experiment/vulnerabilities')
    const data = await response.json()
    if (data.success) {
      vulnerabilities.value = data.vulnerabilities.map(vuln => ({
        id: vuln.id,
        name: vuln.name,
        category: vuln.category,
        difficulty: vuln.difficulty
      }))
    }
  } catch (error) {
    console.error('Failed to load vulnerabilities:', error)
  }
}

const currentCategoryName = computed(() => {
  const category = categories.value.find(c => c.id === selectedCategory.value)
  return category ? category.name : ''
})

const totalCount = computed(() => vulnerabilities.value.length)

const completedCount = computed(() => {
  return vulnerabilities.value.filter(v => getStatus(v.id) === 'completed').length
})

const filteredVulnerabilities = computed(() => {
  return vulnerabilities.value.filter(v => v.category === selectedCategory.value)
})

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
}

const getStatus = (vulnId) => {
  const userId = store.state.user?.id
  if (!userId) return 'pending'
  const record = store.state.experimentRecords.find(r => r.vulnerability_id === vulnId)
  if (record && (record.success >= 1 || record.success === true)) return 'completed'
  const hasRunningContainer = store.state.runningContainers?.some(c => c.vulnerability_id === vulnId)
  if (hasRunningContainer) return 'in_progress'
  return 'pending'
}

const getStatusText = (vulnId) => {
  const status = getStatus(vulnId)
  switch (status) {
    case 'completed': return '已完成'
    case 'in_progress': return '进行中'
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

const getTargetUrl = () => {
  if (!currentContainer.value || !currentContainer.value.host_port) return ''
  const port = currentContainer.value.host_port
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:'
  const host = window.location.hostname
  return `${protocol}//${host}:${port}`
}

const openChallengeModal = async (vuln) => {
  selectedChallenge.value = vuln
  showChallengeModal.value = true
  flagInput.value = ''
  flagResult.value = null
  currentContainer.value = null

  try {
    if (store.state.user?.id) {
      const containersResponse = await containerApi.list(store.state.user.id)
      if (containersResponse.success && containersResponse.containers.length > 0) {
        const currentVulnContainer = containersResponse.containers.find(
          c => c.vulnerability_id === vuln.id
        )
        if (currentVulnContainer) {
          currentContainer.value = currentVulnContainer
          currentSessionId.value = currentVulnContainer.session_id || ''
          if (currentVulnContainer.timeout_at) {
            const remaining = Math.max(0, Math.floor(currentVulnContainer.timeout_at - Date.now() / 1000))
            if (remaining > 0) {
              startCountdownWithRemaining(remaining)
            } else {
              await stopEnvironment()
              flagResult.value = { success: false, message: '时间已到，靶场环境已自动销毁' }
            }
          } else {
            startCountdown()
          }
          return
        }
      }
    }
  } catch (error) {
    console.log('检查容器状态失败:', error)
  }
}

const closeChallengeModal = () => {
  showChallengeModal.value = false
  selectedChallenge.value = null
  flagInput.value = ''
  flagResult.value = null
  currentContainer.value = null
  showOtherContainer.value = null
  clearCountdown()
}

const clearCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

const startCountdown = () => {
  const startTime = Date.now()
  const totalSeconds = 3600
  remainingTime.value = '01:00:00'
  clearCountdown()
  countdownTimer = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000)
    const remaining = Math.max(0, totalSeconds - elapsed)
    remainingTime.value = formatTime(remaining)
    if (remaining <= 0) {
      clearCountdown()
      stopEnvironment()
      flagResult.value = { success: false, message: '时间已到，靶场环境已自动销毁' }
    }
  }, 1000)
}

const startCountdownWithRemaining = (remainingSeconds) => {
  const startTime = Date.now()
  const totalSeconds = remainingSeconds
  remainingTime.value = formatTime(totalSeconds)
  clearCountdown()
  countdownTimer = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000)
    const remaining = Math.max(0, totalSeconds - elapsed)
    remainingTime.value = formatTime(remaining)
    if (remaining <= 0) {
      clearCountdown()
      stopEnvironment()
      flagResult.value = { success: false, message: '时间已到，靶场环境已自动销毁' }
    }
  }, 1000)
}

const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const showOtherContainer = ref(null)

const startEnvironment = async () => {
  if (!selectedChallenge.value) return
  isStarting.value = true
  try {
    if (store.state.user?.id) {
      const containersResponse = await containerApi.list(store.state.user.id)
      if (containersResponse.success && containersResponse.containers.length > 0) {
        const existingContainer = containersResponse.containers[0]
        flagResult.value = { 
          success: false, 
          message: `您当前已有一个运行中的实验（${existingContainer.vulnerability_name}）。请先关闭当前实验。` 
        }
        isStarting.value = false
        showOtherContainer.value = existingContainer
        return
      }
    }
    
    const experimentResponse = await experimentApi.start(store.state.user?.id || 0, selectedChallenge.value.id)
    if (experimentResponse.sessionId) {
      currentSessionId.value = experimentResponse.sessionId
    }
    const response = await containerApi.create(selectedChallenge.value.id, store.state.user?.id || 0, currentSessionId.value)
    if (response.container_id) {
      currentContainer.value = response
      startCountdown()
      await store.actions.loadExperimentRecords()
      await store.actions.loadRunningContainers()
      flagResult.value = null
    } else {
      flagResult.value = { success: false, message: response.message || '启动失败' }
    }
  } catch (error) {
    flagResult.value = { success: false, message: '启动失败: ' + error.message }
  } finally {
    isStarting.value = false
  }
}

const closeOtherContainer = async () => {
  if (!showOtherContainer.value) return
  try {
    await containerApi.remove(
      showOtherContainer.value.container_id || showOtherContainer.value.id,
      store.state.user?.id || 0,
      showOtherContainer.value.vulnerability_id || 0,
      showOtherContainer.value.session_id || ''
    )
    showOtherContainer.value = null
    flagResult.value = null
    await store.actions.loadRunningContainers()
  } catch (error) {
    console.error('关闭容器失败:', error)
  }
}

const stopEnvironment = async (success = false) => {
  if (!currentContainer.value) return
  clearCountdown()
  try {
    if (currentSessionId.value) {
      await experimentApi.endSession(currentSessionId.value, success, store.state.user?.id || 0, selectedChallenge.value?.id || 0)
    } else if (success) {
      await experimentApi.endSession('', success, store.state.user?.id || 0, selectedChallenge.value?.id || 0)
    }
    if (currentContainer.value.container_id) {
      await containerApi.remove(
        currentContainer.value.container_id,
        store.state.user?.id || 0,
        selectedChallenge.value?.id || 0,
        currentSessionId.value || ''
      )
    }
    currentSessionId.value = ''
    currentContainer.value = null
    await store.actions.loadExperimentRecords()
    await store.actions.loadRunningContainers()
  } catch (error) {
    console.error('停止容器失败:', error)
  }
}

const submitFlag = async () => {
  if (!flagInput.value.trim()) {
    flagResult.value = { success: false, message: '请输入Flag' }
    return
  }
  isSubmitting.value = true
  try {
    const response = await experimentApi.submit({
      user_id: store.state.user?.id || 0,
      vulnerability_id: selectedChallenge.value.id,
      flag: flagInput.value,
      session_id: currentSessionId.value
    })
    if (response.success) {
      flagResult.value = { success: true, message: 'Flag正确！挑战成功！' }
      await store.actions.loadExperimentRecords()
      await store.actions.refreshUserProfile()
      await stopEnvironment(true)
    } else {
      flagResult.value = { success: false, message: response.message || 'Flag错误' }
    }
  } catch (error) {
    flagResult.value = { success: false, message: '提交失败: ' + (error.response?.data?.message || error.message) }
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  await loadVulnerabilities()
  await store.actions.loadExperimentRecords()
})

onUnmounted(() => {
  clearCountdown()
})
</script>

<style scoped>
.challenges-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f2f5 0%, #e0e7ff 50%, #f0f2f5 100%);
  position: relative;
}

.page-header {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  padding: 50px 24px;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 600px;
  height: 600px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  filter: blur(40px);
}

.page-header::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: rgba(139, 92, 246, 0.2);
  border-radius: 50%;
  filter: blur(30px);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-box {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 16px 24px;
  border-radius: 12px;
  text-align: center;
}

.stat-box .stat-value {
  display: block;
  color: white;
  font-size: 28px;
  font-weight: 700;
}

.stat-box .stat-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.challenges-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
  display: flex;
  gap: 24px;
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  background: white;
  border-radius: 18px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.category-item::before {
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

.category-item:hover {
  transform: translateX(8px);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
}

.category-item:hover::before {
  transform: scaleY(1);
}

.category-item.active {
  border-color: #6366f1;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.18);
}

.category-item.active::before {
  transform: scaleY(1);
}

.category-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.category-icon-wrapper.sqli {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #3b82f6;
}

.category-icon-wrapper.xss {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #22c55e;
}

.category-icon-wrapper.csrf {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #f59e0b;
}

.category-icon-wrapper.deserialization {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #8b5cf6;
}

.category-icon-wrapper.upload {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #ef4444;
}

.category-info {
  flex: 1;
}

.category-name {
  display: block;
  font-weight: 600;
  color: #1f2937;
  font-size: 15px;
  margin-bottom: 2px;
}

.category-desc {
  font-size: 12px;
  color: #9ca3af;
}

.category-count {
  background: #f3f4f6;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
}

.category-item.active .category-count {
  background: rgba(99, 102, 241, 0.15);
  color: #6366f1;
}

.main-content {
  flex: 1;
}

.content-header {
  margin-bottom: 24px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.header-title h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.category-count-badge {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.category-desc {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
}

.challenges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.challenge-card {
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.challenge-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.18);
}

.challenge-card.completed {
  border-color: #22c55e;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, white 100%);
  position: relative;
}

.challenge-card.completed::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, transparent 100%);
  border-radius: 0 20px 0 50%;
}

.challenge-card.in_progress {
  border-color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, white 100%);
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 4px 20px rgba(245, 158, 11, 0.15);
  }
  50% {
    box-shadow: 0 8px 30px rgba(245, 158, 11, 0.25);
  }
}

.card-inner {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.difficulty-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 13px;
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

.status-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-indicator.completed {
  background: #dcfce7;
  color: #22c55e;
}

.status-indicator.in_progress {
  background: #fef3c7;
  color: #f59e0b;
}

.status-indicator.pending {
  background: #f3f4f6;
  color: #9ca3af;
}

.challenge-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 10px 0;
}

.challenge-desc {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.status-text {
  font-size: 13px;
  font-weight: 500;
}

.challenge-card.completed .status-text {
  color: #22c55e;
}

.challenge-card.in_progress .status-text {
  color: #f59e0b;
}

.challenge-card.pending .status-text {
  color: #9ca3af;
}

.arrow-icon {
  color: #9ca3af;
  font-size: 18px;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
}

.challenge-dialog {
  border-radius: 20px;
}

.modal-content {
  padding: 16px 0;
}

.flag-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
  margin-bottom: 24px;
  border-bottom: 1px solid #f3f4f6;
}

.flag-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.flag-title {
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 6px 0;
}

.flag-format {
  background: #f3f4f6;
  padding: 6px 16px;
  border-radius: 8px;
  color: #7c3aed;
  font-weight: 600;
}

.env-section, .flag-submit-section {
  margin-bottom: 24px;
}

.section-header {
  margin-bottom: 16px;
}

.section-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.other-container {
  background: #fef3c7;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #fde68a;
}

.env-details {
  padding: 12px 0;
  font-size: 13px;
  color: #92400e;
}

.danger-btn {
  width: 100%;
  margin-top: 8px;
}

.start-section {
  text-align: center;
}

.start-card {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 16px;
  padding: 40px;
}

.start-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 20px;
}

.start-card h4 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.start-card p {
  color: #6b7280;
  margin: 0 0 24px 0;
}

.start-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.running-section {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-radius: 16px;
  padding: 24px;
}

.running-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.running-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 10px;
  height: 10px;
  background: #22c55e;
  border-radius: 50%;
}

.status-dot.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.running-status .status-text {
  font-weight: 600;
  color: #166534;
}

.countdown {
  background: rgba(0, 0, 0, 0.1);
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: 600;
  color: #1f2937;
  font-family: monospace;
  font-size: 16px;
}

.env-url {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.url-link {
  color: #1890ff;
  text-decoration: none;
  font-weight: 500;
  word-break: break-all;
}

.env-info {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

.stop-btn {
  width: 100%;
}

.flag-input-group {
  display: flex;
  gap: 12px;
}

.flag-input {
  flex: 1;
}

.submit-btn {
  padding: 0 32px;
}

@media (max-width: 768px) {
  .challenges-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
  }
  
  .challenges-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
}

.message-box {
  margin-top: 20px;
  border-radius: 8px;
  padding: 12px 16px;
}

.message-box.error {
  background: #fef0f0;
  border: 1px solid #ffccc7;
}

.message-box.success {
  background: #f0f9eb;
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

.warning-box {
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.warning-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning-icon {
  color: #f59e0b;
  font-size: 16px;
}

.warning-text {
  font-size: 14px;
  color: #92400e;
}
</style>
