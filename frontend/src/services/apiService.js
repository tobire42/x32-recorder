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
}

export default apiService
