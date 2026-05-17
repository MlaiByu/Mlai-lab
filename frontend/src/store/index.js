import { reactive } from 'vue'
import { experiment as experimentApi, container as containerApi, users as usersApi } from '../api'

const state = reactive({
  user: null,
  experimentRecords: [],
  runningContainers: [],
  isLoading: false
})

const mutations = {
  setUser: (user) => {
    state.user = user
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    } else {
      localStorage.removeItem('user')
    }
  },

  setExperimentRecords: (records) => {
    state.experimentRecords = records
  },

  setRunningContainers: (containers) => {
    state.runningContainers = containers
  },

  setLoading: (loading) => {
    state.isLoading = loading
  },

  clearAll: () => {
    state.user = null
    state.experimentRecords = []
    state.runningContainers = []
    state.isLoading = false
    localStorage.removeItem('user')
  }
}

const actions = {
  login: async (username, password, api) => {
    try {
      mutations.setLoading(true)
      const response = await api.auth.login(username, password)
      mutations.setUser(response.user)
      await actions.loadExperimentRecords()
      return response
    } catch (error) {
      throw error
    } finally {
      mutations.setLoading(false)
    }
  },

  logout: () => {
    mutations.clearAll()
  },

  loadExperimentRecords: async (retryCount = 0) => {
    if (!state.user?.id) return
    try {
      const response = await experimentApi.records(state.user.id)
      if (response.success) {
        mutations.setExperimentRecords(response.records || [])
      }
      await actions.loadRunningContainers()
      return response
    } catch (error) {
      if (retryCount < 3) {
        setTimeout(() => {
          actions.loadExperimentRecords(retryCount + 1)
        }, 500 * (retryCount + 1))
      } else {
        console.warn('加载实验记录失败（已重试3次）:', error.message)
      }
    }
  },

  loadRunningContainers: async () => {
    if (!state.user?.id) return
    try {
      const response = await containerApi.list(state.user.id)
      if (response.success) {
        mutations.setRunningContainers(response.containers || [])
      }
    } catch (error) {
      // 静默处理错误，避免在控制台刷屏和影响用户体验
      // console.warn('Failed to load running containers:', error.message)
    }
  },

  startExperiment: async (vulnerabilityId) => {
    if (!state.user?.id) return
    try {
      mutations.setLoading(true)
      const experimentResponse = await experimentApi.start(state.user.id, vulnerabilityId)
      if (!experimentResponse.success) {
        throw new Error('启动实验失败')
      }
      const containerResponse = await containerApi.create(vulnerabilityId, state.user.id, experimentResponse.sessionId)
      if (!containerResponse.success) {
        throw new Error(containerResponse.message || '创建容器失败')
      }
      return { experiment: experimentResponse, container: containerResponse }
    } catch (error) {
      throw error
    } finally {
      mutations.setLoading(false)
    }
  },

  completeExperiment: async (vulnerabilityId) => {
    if (!state.user?.id) return
    try {
      const response = await experimentApi.complete(state.user.id, vulnerabilityId)
      if (response.success) {
        await actions.loadExperimentRecords()
      }
      return response
    } catch (error) {
      throw error
    }
  },

  checkExperimentStatus: (vulnerabilityId) => {
    return state.experimentRecords.find(r => r.vulnerability_id === vulnerabilityId) || null
  },

  isExperimentCompleted: (vulnerabilityId) => {
    const record = actions.checkExperimentStatus(vulnerabilityId)
    return record?.success >= 1 || record?.success === true
  },

  refreshUserProfile: async () => {
    if (!state.user?.id) return
    try {
      const response = await usersApi.getProfile(state.user.id)
      if (response.success && response.data) {
        const userData = response.data
        const currentUser = state.user
        currentUser.score = userData.score || currentUser.score
        mutations.setUser(currentUser)
      }
    } catch (error) {
      console.warn('刷新用户信息失败:', error.message)
    }
  }
}

const store = {
  state,
  mutations,
  actions
}

const initStore = () => {
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    try {
      const user = JSON.parse(savedUser)
      mutations.setUser(user)
      setTimeout(() => {
        actions.loadExperimentRecords()
      }, 100)
    } catch (error) {
      console.error('Failed to parse saved user:', error)
      localStorage.removeItem('user')
    }
  }
}

initStore()

export default store
