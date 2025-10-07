import axios from 'axios'

// Configure the base URL for your Django API
const API_BASE_URL = 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const apiService = {
  // Get all audio devices
  async getAudioDevices() {
    const response = await apiClient.get('/audiodevice/')
    return response.data
  },

  // Get all recordings
  async getRecordings() {
    const response = await apiClient.get('/recordings/')
    return response.data.results
  },

  // Get a specific recording
  async getRecording(id) {
    const response = await apiClient.get(`/recordings/${id}/`)
    return response.data
  },

  // Start a new recording
  async startRecording(data) {
    const response = await apiClient.post('/recordings/start/', data)
    return response.data
  },

  // Stop a recording
  async stopRecording(id) {
    const response = await apiClient.post(`/recordings/${id}/stop/`)
    return response.data
  },

  // Delete a recording
  async deleteRecording(id) {
    const response = await apiClient.delete(`/recordings/${id}/`)
    return response.data
  },

  // Get all recording templates
  async getTemplates() {
    const response = await apiClient.get('/templates/')
    return response.data.results || response.data
  },

  // Get a specific template
  async getTemplate(id) {
    const response = await apiClient.get(`/templates/${id}/`)
    return response.data
  },

  // Create a new template
  async createTemplate(data) {
    const response = await apiClient.post('/templates/', data)
    return response.data
  },

  // Update a template
  async updateTemplate(id, data) {
    const response = await apiClient.put(`/templates/${id}/`, data)
    return response.data
  },

  // Delete a template
  async deleteTemplate(id) {
    const response = await apiClient.delete(`/templates/${id}/`)
    return response.data
  },

  // Get template channels
  async getTemplateChannels(templateId) {
    const response = await apiClient.get(`/template-channels/?template=${templateId}`)
    return response.data.results || response.data
  },

  // Create a template channel
  async createTemplateChannel(data) {
    const response = await apiClient.post('/template-channels/', data)
    return response.data
  },

  // Update a template channel
  async updateTemplateChannel(id, data) {
    const response = await apiClient.put(`/template-channels/${id}/`, data)
    return response.data
  },

  // Delete a template channel
  async deleteTemplateChannel(id) {
    const response = await apiClient.delete(`/template-channels/${id}/`)
    return response.data
  },
}

export default apiService
