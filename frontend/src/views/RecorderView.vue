<template>
  <div class="recorder-view">
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <RecordingControls 
      :audioDevices="audioDevices"
      :isRecording="isRecording"
      :activeRecording="activeRecording"
      :templates="templates"
      :selectedTemplate="selectedTemplate"
      @start-recording="startRecording"
      @stop-recording="stopRecording"
      @refresh-devices="fetchAudioDevices"
    />

    <RecordingsList 
      :recordings="recordings"
      :loading="loadingRecordings"
      @refresh="fetchRecordings"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import RecordingControls from '../components/RecordingControls.vue'
import RecordingsList from '../components/RecordingsList.vue'
import apiService from '../services/apiService'

export default {
  name: 'RecorderView',
  components: {
    RecordingControls,
    RecordingsList
  },
  setup() {
    const audioDevices = ref([])
    const recordings = ref([])
    const templates = ref([])
    const activeRecording = ref(null)
    const selectedTemplate = ref(null)
    const isRecording = ref(false)
    const loadingRecordings = ref(true)
    const error = ref(null)
    let pollInterval = null

    const fetchAudioDevices = async () => {
      try {
        error.value = null
        audioDevices.value = await apiService.getAudioDevices()
      } catch (err) {
        error.value = `Failed to fetch audio devices: ${err.message}`
      }
    }

    const fetchTemplates = async () => {
      try {
        error.value = null
        templates.value = await apiService.getTemplates()
      } catch (err) {
        error.value = `Failed to fetch templates: ${err.message}`
      }
    }

    const fetchRecordings = async () => {
      try {
        error.value = null
        recordings.value = await apiService.getRecordings()
        
        // Check if there's an active recording
        const active = recordings.value.find(r => r.state === 0 || r.state === 1)
        if (active) {
          activeRecording.value = active
          isRecording.value = true
        } else {
          activeRecording.value = null
          isRecording.value = false
        }
      } catch (err) {
        error.value = `Failed to fetch recordings: ${err.message}`
      } finally {
        loadingRecordings.value = false
      }
    }

    const startRecording = async (recordingData) => {
      try {
        error.value = null
        const recording = await apiService.startRecording(recordingData)
        activeRecording.value = recording
        isRecording.value = true
        await fetchRecordings()
      } catch (err) {
        error.value = `Failed to start recording: ${err.message}`
      }
    }

    const stopRecording = async (recordingId) => {
      try {
        error.value = null
        await apiService.stopRecording(recordingId)
        isRecording.value = false
        activeRecording.value = null
        await fetchRecordings()
      } catch (err) {
        error.value = `Failed to stop recording: ${err.message}`
      }
    }

    const startPolling = () => {
      // Poll for updates every 2 seconds
      pollInterval = setInterval(fetchRecordings, 2000)
    }

    const stopPolling = () => {
      if (pollInterval) {
        clearInterval(pollInterval)
        pollInterval = null
      }
    }

    onMounted(() => {
      fetchAudioDevices()
      fetchTemplates()
      fetchRecordings()
      startPolling()
    })

    onUnmounted(() => {
      stopPolling()
    })

    return {
      audioDevices,
      recordings,
      templates,
      activeRecording,
      selectedTemplate,
      isRecording,
      loadingRecordings,
      error,
      fetchAudioDevices,
      fetchTemplates,
      fetchRecordings,
      startRecording,
      stopRecording
    }
  }
}
</script>

<style scoped>
.recorder-view {
  width: 100%;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}
</style>
