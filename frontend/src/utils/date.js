export const parseDatabaseTime = (timeStr) => {
  if (!timeStr) return null
  
  try {
    let date
    if (typeof timeStr === 'string') {
      const trimmed = timeStr.trim()
      if (trimmed.includes('T')) {
        date = new Date(trimmed)
      } else if (trimmed.includes(' ')) {
        const parts = trimmed.split(' ')
        if (parts.length === 2) {
          const datePart = parts[0]
          const timePart = parts[1]
          const dateStr = `${datePart}T${timePart}+08:00`
          date = new Date(dateStr)
        } else {
          date = new Date(trimmed.replace(' ', 'T'))
        }
      } else {
        date = new Date(trimmed)
      }
    } else if (typeof timeStr === 'number') {
      if (timeStr > 1e12) {
        date = new Date(timeStr)
      } else {
        date = new Date(timeStr * 1000)
      }
    } else {
      date = new Date(timeStr)
    }
    
    return isNaN(date.getTime()) ? null : date
  } catch {
    return null
  }
}

export const formatTimeAgo = (timeStr) => {
  const date = parseDatabaseTime(timeStr)
  if (!date) return '刚刚'
  
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 0) return '刚刚'
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  const weeks = Math.floor(diff / 604800000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  if (weeks < 4) return `${weeks}周前`
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

export const formatDateTime = (timeStr) => {
  const date = parseDatabaseTime(timeStr)
  if (!date) return '-'
  
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

export const formatDate = (timeStr) => {
  const date = parseDatabaseTime(timeStr)
  if (!date) return '-'
  
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}