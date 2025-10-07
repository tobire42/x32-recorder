<template>
  <div class="app">
    <header class="header">
      <div class="container">
        <h1 class="title">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <circle cx="12" cy="12" r="3" fill="currentColor"/>
          </svg>
          X32 Recorder
        </h1>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <TemplateManager
          :templates="templates"
          :loading="loadingTemplates"
          @refresh="fetchTemplates"
          @select-template="selectTemplate"
        />

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
    </main>

    <footer class="footer">
      <div class="container">
        <p>&copy; 2025 X32 Recorder</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import RecordingControls from './components/RecordingControls.vue'
import RecordingsList from './components/RecordingsList.vue'
import TemplateManager from './components/TemplateManager.vue'
import apiService from './services/apiService'

export default {
  name: 'App',
  components: {
    RecordingControls,
    RecordingsList,
    TemplateManager
  },
  setup() {
    const audioDevices = ref([])
    const recordings = ref([])
    const templates = ref([])
    const activeRecording = ref(null)
    const selectedTemplate = ref(null)
    const isRecording = ref(false)
    const loadingRecordings = ref(true)
    const loadingTemplates = ref(false)
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
        loadingTemplates.value = true
        error.value = null
        templates.value = await apiService.getTemplates()
      } catch (err) {
        error.value = `Failed to fetch templates: ${err.message}`
      } finally {
        loadingTemplates.value = false
      }
    }

    const selectTemplate = (template) => {
      selectedTemplate.value = template
      // Scroll to recording controls
      setTimeout(() => {
        selectedTemplate.value = null // Reset after applying
      }, 100)
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
      loadingTemplates,
      error,
      fetchAudioDevices,
      fetchTemplates,
      fetchRecordings,
      selectTemplate,
      startRecording,
      stopRecording
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1.5rem 0;
}

.title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.icon {
  width: 32px;
  height: 32px;
  color: white;
}

.main {
  flex: 1;
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
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

.footer {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem 0;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .title {
    font-size: 1.5rem;
  }
  
  .icon {
    width: 28px;
    height: 28px;
  }
}
</style>
