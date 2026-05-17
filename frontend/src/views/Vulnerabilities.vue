<template>
  <div class="challenges-page">
    <div class="challenges-header">
      <h1>Challenges</h1>
    </div>

    <div class="challenges-container">
      <aside class="sidebar">
        <div
          v-for="category in categories"
          :key="category.id"
          :class="['category-item', { active: selectedCategory === category.id }]"
          @click="selectCategory(category.id)"
        >
          <span>{{ category.name }}</span>
        </div>
      </aside>

      <main class="main-content">
        <div class="chapter-section">
          <h2 class="chapter-title">{{ currentCategoryName }}</h2>
          <div class="challenges-grid">
            <div
              v-for="vuln in filteredVulnerabilities"
              :key="vuln.id"
              :class="['challenge-card', getStatus(vuln.id)]"
              @click="openChallengeModal(vuln)"
            >
              <span class="challenge-name">{{ vuln.name }}</span>
              <span class="challenge-status">{{ getStatusText(vuln.id) }}</span>
            </div>
          </div>
        </div>
      </main>
    </div>

    <div v-if="showChallengeModal" class="challenge-modal-overlay" @click.self="closeChallengeModal">
      <div class="challenge-modal">
        <button class="modal-close-btn" @click="closeChallengeModal">×</button>

        <div class="modal-body">
          <h2 class="challenge-title">{{ selectedChallenge?.name }}</h2>

          <div class="challenge-description">
            <p>本系列题目FLAG格式固定为Mlai{xxxxxx}</p>
          </div>

          <div class="target-info">
            <h3>靶场信息</h3>
            <div v-if="showOtherContainer" class="other-container">
              <div class="status-indicator">
                <span class="status-dot running"></span>
                <span>已有实验运行中</span>
              </div>
              <div class="env-details">
                <p>实验: {{ showOtherContainer.vulnerability_name }}</p>
                <p>容器ID: {{ (showOtherContainer.container_id || showOtherContainer.id)?.slice(0, 12) }}...</p>
              </div>
              <button class="btn-stop-env" @click="closeOtherContainer">关闭当前实验</button>
            </div>
            <div v-else-if="!currentContainer" class="start-environment">
              <button
                class="btn-start-env"
                @click="startEnvironment"
                :disabled="isStarting"
              >
                {{ isStarting ? '启动中...' : '启动靶场环境' }}
              </button>
            </div>
            <div v-else class="env-status">
              <div class="status-indicator">
                <span class="status-dot running"></span>
                <span>靶场环境运行中</span>
                <span class="countdown">{{ remainingTime }}</span>
              </div>
              <div class="env-details">
                <p>容器ID: {{ (currentContainer.container_id || currentContainer.id)?.slice(0, 12) }}...</p>
                <p>访问地址: <a :href="getTargetUrl()" target="_blank">
                  {{ getTargetUrl() }}
                </a></p>
              </div>
              <button class="btn-stop-env" @click="stopEnvironment">停止靶场环境</button>
            </div>
          </div>

          <div class="flag-submit">
            <input
              type="text"
              v-model="flagInput"
              placeholder="Flag"
              class="flag-input"
            />
            <button class="btn-submit" @click="submitFlag" :disabled="isSubmitting">
              {{ isSubmitting ? '提交中...' : 'Submit' }}
            </button>
          </div>

          <div v-if="flagResult" class="flag-result" :class="flagResult.success ? 'success' : 'error'">
            {{ flagResult.message }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
let containerRefreshTimer = null

const loadVulnerabilities = async () => {
  try {
    const response = await fetch('/api/experiment/vulnerabilities')
    const data = await response.json()
    if (data.success) {
      vulnerabilities.value = data.vulnerabilities.map(vuln => ({
        id: vuln.id,
        name: vuln.name,
        category: vuln.category
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

const filteredVulnerabilities = computed(() => {
  return vulnerabilities.value.filter(v => v.category === selectedCategory.value)
})

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
}

const getStatus = (vulnId) => {
  const userId = store.state.user?.id
  if (!userId) return 'pending'

  // 检查是否有运行中的容器
  const hasRunningContainer = store.state.runningContainers?.some(c => c.vulnerability_id === vulnId)
  if (hasRunningContainer) return 'in_progress'

  const record = store.state.experimentRecords.find(r => r.vulnerability_id === vulnId)
  if (!record) return 'pending'
  if (record.success) return 'completed'
  return 'pending'
}

const getStatusText = (vulnId) => {
  const status = getStatus(vulnId)
  switch (status) {
    case 'completed': return '已完成'
    case 'in_progress': return '进行中'
    default: return '未完成'
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
    // 首先检查用户是否有运行中的容器
    if (store.state.user?.id) {
      const containersResponse = await containerApi.list(store.state.user.id)
      if (containersResponse.success && containersResponse.containers.length > 0) {
        // 检查是否是当前漏洞的容器
        const currentVulnContainer = containersResponse.containers.find(
          c => c.vulnerability_id === vuln.id
        )
        if (currentVulnContainer) {
          currentContainer.value = currentVulnContainer
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

const startEnvironment = async () => {
  if (!selectedChallenge.value) return
  isStarting.value = true
  try {
    // 首先检查用户是否有运行中的容器
    if (store.state.user?.id) {
      const containersResponse = await containerApi.list(store.state.user.id)
      if (containersResponse.success && containersResponse.containers.length > 0) {
        // 用户有运行中的容器，询问是否要关闭
        const existingContainer = containersResponse.containers[0]
        flagResult.value = { 
          success: false, 
          message: `您当前已有一个运行中的实验（${existingContainer.vulnerability_name}）。请先关闭当前实验。` 
        }
        isStarting.value = false
        
        // 显示已有的容器信息
        showOtherContainer.value = existingContainer
        return
      }
    }
    
    // 没有运行中的容器，正常启动
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

const showOtherContainer = ref(null)

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

const stopEnvironment = async () => {
  if (!currentContainer.value) return
  clearCountdown()
  try {
    if (currentSessionId.value) {
      await experimentApi.endSession(currentSessionId.value, false)
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
      await stopEnvironment()
    } else {
      flagResult.value = { success: false, message: response.message || 'Flag错误' }
    }
  } catch (error) {
    flagResult.value = { success: false, message: '提交失败: ' + (error.response?.data?.message || error.message) }
  } finally {
    isSubmitting.value = false
  }
}

let isMounted = false

onMounted(async () => {
  isMounted = true
  await loadVulnerabilities()
  await store.actions.loadExperimentRecords()
  // 每5秒刷新一次容器状态
  containerRefreshTimer = setInterval(async () => {
    if (isMounted && store.state.user?.id) {
      try {
        await store.actions.loadRunningContainers()
      } catch (error) {
        console.error('刷新容器状态失败:', error)
      }
    }
  }, 5000)
})

onUnmounted(() => {
  isMounted = false
  clearCountdown()
  if (containerRefreshTimer) {
    clearInterval(containerRefreshTimer)
    containerRefreshTimer = null
  }
})
</script>

<style scoped>
.challenges-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 20px;
}

.challenges-header h1 {
  color: #fff;
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 30px;
  text-shadow: 0 0 20px rgba(0, 123, 255, 0.5);
}

.challenges-container {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.sidebar {
  width: 200px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 15px;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  color: #b0b0b0;
  transition: all 0.3s ease;
}

.category-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.category-item.active {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: #fff;
}

.main-content {
  flex: 1;
}

.chapter-title {
  color: #fff;
  font-size: 1.5rem;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.challenges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.challenge-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.challenge-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 123, 255, 0.2);
  border-color: rgba(0, 123, 255, 0.3);
}

.challenge-card.in_progress {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(255, 193, 7, 0.1) 100%);
  border-color: rgba(255, 193, 7, 0.5);
}

.challenge-card.in_progress .challenge-name {
  color: #ffc107;
}

.challenge-card.completed {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.2) 0%, rgba(40, 167, 69, 0.1) 100%);
  border-color: rgba(40, 167, 69, 0.5);
}

.challenge-card.completed .challenge-name {
  color: #28a745;
}

.challenge-card.completed .challenge-status {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.challenge-card.in_progress .challenge-status {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.challenge-card.pending .challenge-status {
  background: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.challenge-name {
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 8px;
  display: block;
}

.challenge-status {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 8px;
}

.challenge-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.challenge-modal {
  background: #1e1e2e;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  font-size: 1.5rem;
  cursor: pointer;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
  z-index: 10;
}

.modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 25px;
}

.challenge-title {
  color: #fff;
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.challenge-description {
  color: #b0b0b0;
  line-height: 1.6;
  margin-bottom: 25px;
  text-align: left;
}

.challenge-description p {
  margin-bottom: 10px;
}

.target-info {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.target-info h3 {
  color: #fff;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.btn-start-env {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: #fff;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.btn-start-env:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 123, 255, 0.4);
}

.btn-start-env:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.other-container {
  text-align: left;
}

.env-status {
  text-align: left;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.running {
  background: #28a745;
  box-shadow: 0 0 10px #28a745;
}

.status-indicator span:nth-child(2) {
  color: #28a745;
  font-weight: 600;
}

.countdown {
  margin-left: auto;
  color: #ffc107;
  font-weight: 600;
  font-size: 1rem;
  padding: 5px 10px;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 6px;
}

.env-details {
  color: #b0b0b0;
  margin-bottom: 15px;
}

.env-details p {
  margin-bottom: 5px;
}

.env-details a {
  color: #007bff;
  text-decoration: none;
}

.env-details a:hover {
  text-decoration: underline;
}

.btn-stop-env {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
  border: 1px solid rgba(220, 53, 69, 0.5);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-stop-env:hover {
  background: rgba(220, 53, 69, 0.3);
}

.flag-submit {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.flag-input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 1rem;
}

.flag-input::placeholder {
  color: #666;
}

.btn-submit {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: #fff;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(40, 167, 69, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.flag-result {
  padding: 15px;
  border-radius: 8px;
  font-weight: 600;
}

.flag-result.success {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
  border: 1px solid rgba(40, 167, 69, 0.3);
}

.flag-result.error {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
  border: 1px solid rgba(220, 53, 69, 0.3);
}
</style>
