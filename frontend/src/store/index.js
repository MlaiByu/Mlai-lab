import { reactive, computed } from 'vue'
import { experiment as experimentApi, container as containerApi } from '../api'

const state = reactive({
  user: null,
  experimentRecords: [],
  attackLogs: [],
  currentExperiment: null,
  isLoading: false,
  currentContainer: null
})

const getters = {
  isLoggedIn: () => !!state.user,
  isTeacher: () => state.user?.role === 'teacher',
  userRole: () => state.user?.role || 'guest',
  userId: () => state.user?.id || null,
  getUser: () => state.user,
  getExperimentRecords: () => state.experimentRecords,
  getAttackLogs: () => state.attackLogs,
  getCurrentExperiment: () => state.currentExperiment,
  isLoading: () => state.isLoading,
  getCurrentContainer: () => state.currentContainer,
  
  completedExperiments: computed(() => {
    return state.experimentRecords.filter(r => r.success_count > 0).length
  }),
  
  totalExperiments: 4,
  
  experimentProgress: computed(() => {
    return Math.round((getters.completedExperiments.value / getters.totalExperiments) * 100)
  })
}

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

  setAttackLogs: (logs) => {
    state.attackLogs = logs
  },

  setCurrentExperiment: (experiment) => {
    state.currentExperiment = experiment
  },

  updateRecordStatus: (vulnerabilityType, updates) => {
    const index = state.experimentRecords.findIndex(
      r => r.vulnerability_type === vulnerabilityType
    )
    if (index !== -1) {
      state.experimentRecords[index] = { ...state.experimentRecords[index], ...updates }
    }
  },

  setLoading: (loading) => {
    state.isLoading = loading
  },

  setCurrentContainer: (container) => {
    state.currentContainer = container
  },

  clearAll: () => {
    state.user = null
    state.experimentRecords = []
    state.attackLogs = []
    state.currentExperiment = null
    state.isLoading = false
    state.currentContainer = null
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

  loadAttackLogs: async () => {
    if (!state.user?.id) return
    
    try {
      const response = await experimentApi.attackLogs(state.user.id)
      if (response.success) {
        mutations.setAttackLogs(response.logs || [])
      }
      return response
    } catch (error) {
      console.error('Failed to load attack logs:', error)
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
      
      const containerResponse = await containerApi.create(vulnerabilityType)
      if (!containerResponse.success) {
        throw new Error(containerResponse.message || '创建容器失败')
      }
      
      mutations.setCurrentExperiment(vulnerabilityType)
      mutations.setCurrentContainer(containerResponse)
      
      return {
        experiment: experimentResponse,
        container: containerResponse
      }
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
    const record = state.experimentRecords.find(
      r => r.vulnerability_type === vulnerabilityType
    )
    return record || null
  },

  isExperimentCompleted: (vulnerabilityType) => {
    const record = actions.checkExperimentStatus(vulnerabilityType)
    return record?.success_count > 0
  }
}

const store = {
  state,
  getters,
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