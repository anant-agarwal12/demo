const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const api = {
  // Get all alerts
  async getAlerts(params = {}) {
    const query = new URLSearchParams(params).toString()
    const response = await fetch(`${API_BASE}/alerts?${query}`)
    return response.json()
  },

  // Get specific alert
  async getAlert(alertId) {
    const response = await fetch(`${API_BASE}/alerts/${alertId}`)
    return response.json()
  },

  // Acknowledge alert
  async acknowledgeAlert(alertId) {
    const response = await fetch(`${API_BASE}/alerts/${alertId}/ack`, {
      method: 'POST'
    })
    return response.json()
  },

  // Send NLP command
  async sendNLPCommand(text) {
    const response = await fetch(`${API_BASE}/nlp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text })
    })
    return response.json()
  },

  // Get whitelist
  async getWhitelist() {
    const response = await fetch(`${API_BASE}/whitelist`)
    return response.json()
  },

  // Add to whitelist
  async addToWhitelist(name, images) {
    const formData = new FormData()
    formData.append('name', name)
    images.forEach(image => {
      formData.append('images', image)
    })

    const response = await fetch(`${API_BASE}/whitelist/add`, {
      method: 'POST',
      body: formData
    })
    return response.json()
  },

  // Refresh whitelist
  async refreshWhitelist() {
    const response = await fetch(`${API_BASE}/whitelist/refresh`, {
      method: 'POST'
    })
    return response.json()
  },

  // Get health status
  async getHealth() {
    const response = await fetch(`${API_BASE}/health`)
    return response.json()
  },

  // Get metrics
  async getMetrics() {
    const response = await fetch(`${API_BASE}/metrics`)
    return response.json()
  },

  // Get video feed URL
  getVideoFeedUrl() {
    return `${API_BASE}/video_feed`
  }
}
