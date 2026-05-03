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

const request = async (url, options = {}) => {
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
    const response = await fetch(`${BASE_URL}${url}`, defaultOptions)
    
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
    if (error.message.includes('Failed to fetch')) {
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

  create: (data) => {
    return request('/users/create', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  update: (userId, data) => {
    return request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  },

  delete: (userId) => {
    return request(`/users/${userId}`, {
      method: 'DELETE'
    })
  },

  getProfile: (userId) => {
    return request(`/users/profile/${userId}`)
  },

  changePassword: (userId, data) => {
    return request(`/users/change_password/${userId}`, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
}

export const experiment = {
  start: (userId, vulnerabilityType) => {
    return request('/experiment/start', {
      method: 'POST',
      body: JSON.stringify({ userId, vulnerabilityType })
    })
  },

  complete: (userId, vulnerabilityType) => {
    return request('/experiment/complete', {
      method: 'POST',
      body: JSON.stringify({ userId, vulnerabilityType })
    })
  },

  records: (userId) => {
    return request(`/experiment/records?userId=${userId}`)
  },

  submit: (data) => {
    return request('/experiment/submit', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  sessions: (userId, vulnerabilityType = '') => {
    let url = `/experiment/sessions?userId=${userId}`
    if (vulnerabilityType) {
      url += `&vulnerabilityType=${encodeURIComponent(vulnerabilityType)}`
    }
    return request(url)
  },

  endSession: (sessionId, success = false) => {
    return request('/experiment/end_session', {
      method: 'POST',
      body: JSON.stringify({ sessionId, success })
    })
  }
}

export const container = {
  create: (vulnerabilityType, userId, sessionId) => {
    return request('/container/create', {
      method: 'POST',
      body: JSON.stringify({ vulnerability_type: vulnerabilityType, user_id: userId, session_id: sessionId })
    })
  },
  
  getByVuln: (vulnerabilityType, userId) => {
    return request('/container/get_by_vuln', {
      method: 'POST',
      body: JSON.stringify({ vulnerability_type: vulnerabilityType, user_id: userId })
    })
  },
  
  remove: (containerId, userId, vulnerabilityType, sessionId) => {
    return request(`/container/remove/${containerId}`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, vulnerability_type: vulnerabilityType, session_id: sessionId })
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