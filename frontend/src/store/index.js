import { reactive } from 'vue'
import { experiment as experimentApi, container as containerApi } from '../api'

const state = reactive({
  user: null,
  experimentRecords: [],
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

  setLoading: (loading) => {
    state.isLoading = loading
  },

  clearAll: () => {
    state.user = null
    state.experimentRecords = []
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

  loadExperimentRecords: async () => {
    if (!state.user?.id) return
    try {
      const response = await experimentApi.records(state.user.id)
      if (response.success) {
        mutations.setExperimentRecords(response.records || [])
      }
      return response
    } catch (error) {
      console.error('Failed to load experiment records:', error)
    }
  },

  startExperiment: async (vulnerabilityType) => {
    if (!state.user?.id) return
    try {
      mutations.setLoading(true)
      const experimentResponse = await experimentApi.start(state.user.id, vulnerabilityType)
      if (!experimentResponse.success) {
        throw new Error('启动实验失败')
      }
      const containerResponse = await containerApi.create(vulnerabilityType, state.user.id, experimentResponse.sessionId)
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

  completeExperiment: async (vulnerabilityType) => {
    if (!state.user?.id) return
    try {
      const response = await experimentApi.complete(state.user.id, vulnerabilityType)
      if (response.success) {
        await actions.loadExperimentRecords()
      }
      return response
    } catch (error) {
      throw error
    }
  },

  checkExperimentStatus: (vulnerabilityType) => {
    return state.experimentRecords.find(r => r.vulnerability_type === vulnerabilityType) || null
  },

  isExperimentCompleted: (vulnerabilityType) => {
    const record = actions.checkExperimentStatus(vulnerabilityType)
    return record?.success_count > 0
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
