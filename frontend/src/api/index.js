const BASE_URL = '/api'

const getAuthToken = () => {
  const user = localStorage.getItem('user')
  if (user) {
    try {
      return JSON.parse(user).token
    } catch {
      return null
    }
  }
  return null
}

const fetchWithTimeout = (url, options = {}, timeout = 10000) => {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error('请求超时')), timeout)
    )
  ])
}

const request = async (url, options = {}, retryCount = 0, maxRetries = 2) => {
  const token = getAuthToken()
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    },
    credentials: 'include',
    ...options
  }

  try {
    const response = await fetchWithTimeout(`${BASE_URL}${url}`, defaultOptions)
    
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(new Error('登录已过期，请重新登录'))
      }
      
      const errorData = await response.json().catch(() => null)
      throw new Error(errorData?.message || `请求失败，状态码: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    if (error.message.includes('Failed to fetch') || error.message.includes('请求超时')) {
      if (retryCount < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 300 * (retryCount + 1)))
        return request(url, options, retryCount + 1, maxRetries)
      }
      throw new Error('网络连接失败，请检查网络')
    }
    throw error
  }
}

export const auth = {
  login: (username, password) => {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    })
  }
}

export const users = {
  list: () => {
    return request('/users/list')
  },

  getProfile: (userId) => {
    return request(`/users/profile/${userId}`)
  },

  changePassword: (userId, data) => {
    return request(`/users/change_password/${userId}`, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  promoteToTeacher: (userId) => {
    return request('/users/promote_to_teacher', {
      method: 'POST',
      body: JSON.stringify({ target_user_id: userId })
    })
  },

  demoteToStudent: (userId) => {
    return request('/users/demote_to_student', {
      method: 'POST',
      body: JSON.stringify({ target_user_id: userId })
    })
  },

  getRecentCompletions: () => {
    return request('/users/recent_completions')
  }
}

export const experiment = {
  start: (userId, vulnerabilityId) => {
    return request('/experiment/start', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, vulnerability_id: vulnerabilityId })
    })
  },

  submit: (data) => {
    return request('/experiment/submit', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  endSession: (sessionId, success = false, userId = 0, vulnerabilityId = 0) => {
    return request('/experiment/end_session', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, success, user_id: userId, vulnerability_id: vulnerabilityId })
    })
  },

  records: (userId) => {
    return request(`/experiment/records/${userId}`)
  },

  complete: (userId, vulnerabilityId) => {
    return request('/experiment/complete', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, vulnerability_id: vulnerabilityId })
    })
  }
}

export const container = {
  create: (vulnerabilityId, userId, sessionId) => {
    return request('/container/create', {
      method: 'POST',
      body: JSON.stringify({ vulnerability_id: vulnerabilityId, user_id: userId, session_id: sessionId })
    })
  },
  
  list: (userId) => {
    if (userId) {
      return request(`/container/list?user_id=${userId}`)
    }
    return request('/container/list')
  },
  
  remove: (containerId, userId, vulnerabilityId, sessionId) => {
    return request(`/container/remove/${containerId}`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, vulnerability_id: vulnerabilityId, session_id: sessionId })
    })
  }
}

export default {
  auth,
  users,
  experiment,
  container,
  request
}