<template>
  <div class="recording-controls">
    <div class="card">
      <h2 class="card-title">Recording Controls</h2>
      
      <div v-if="!isRecording" class="form">
        <!-- Template Selection -->
        <div v-if="templates && templates.length > 0" class="form-group">
          <label for="template" class="label">Recording Template (Optional)</label>
          <select
            id="template"
            v-model="selectedTemplateId"
            class="select"
            @change="applyTemplate"
          >
            <option :value="null">-- No Template --</option>
            <option
              v-for="template in templates"
              :key="template.id"
              :value="template.id"
            >
              {{ template.name }} ({{ template.channel_count }} channels)
            </option>
          </select>
          <p v-if="selectedTemplateId" class="help-text">
            Template applied - you can still modify channels below
          </p>
        </div>

        <!-- Filename Input -->
        <div class="form-group">
          <label for="filename" class="label">Filename</label>
          <input
            id="filename"
            v-model="filename"
            type="text"
            class="input"
            placeholder="Leave empty for auto-generated name"
          />
        </div>

        <!-- Audio Device Selection -->
        <div class="form-group">
          <label for="audioDevice" class="label">Audio Device</label>
          <div class="device-select-wrapper">
            <select
              id="audioDevice"
              v-model="selectedDevice"
              class="select"
              :disabled="audioDevices.length === 0"
            >
              <option v-if="audioDevices.length === 0" disabled value="">
                No devices available
              </option>
              <option
                v-for="device in audioDevices"
                :key="device.index"
                :value="device.index"
              >
                {{ device.name }} ({{ device.input_channel_count }} channels)
              </option>
            </select>
            <button @click="$emit('refresh-devices')" class="btn-icon" title="Refresh devices">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Channel Selection -->
        <div class="form-group">
          <label class="label">Channels</label>
          <div class="channel-selector">
            <div 
              v-for="ch in availableChannels" 
              :key="ch"
              class="channel-chip"
              :class="{ active: selectedChannels.includes(ch) }"
              @click="toggleChannel(ch)"
            >
              {{ ch }}
            </div>
          </div>
          <p class="help-text">
            Click to select/deselect channels ({{ selectedChannels.length }} selected)
          </p>
        </div>

        <!-- Start Button -->
        <button
          @click="handleStart"
          class="btn btn-primary"
          :disabled="selectedChannels.length === 0 || selectedDevice === null"
        >
          <PlayIcon class="btn-icon-svg" />
          Start Recording
        </button>
      </div>

      <div v-else class="recording-status">
        <div class="status-indicator">
          <span class="pulse"></span>
          <span class="status-text">Recording in progress...</span>
        </div>
        
        <div class="recording-info">
          <p><strong>Filename:</strong> {{ activeRecording?.filename }}</p>
          <p><strong>Channels:</strong> {{ formatChannels(activeRecording?.channels) }}</p>
          <p><strong>State:</strong> {{ getStateLabel(activeRecording?.state) }}</p>
        </div>

        <button
          @click="handleStop"
          class="btn btn-danger"
        >
          <StopIcon class="btn-icon-svg" />
          Stop Recording
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import PlayIcon from './icons/PlayIcon.vue'
import StopIcon from './icons/StopIcon.vue'
import apiService from '../services/apiService'

export default {
  name: 'RecordingControls',
  components: {
    PlayIcon,
    StopIcon
  },
  props: {
    audioDevices: {
      type: Array,
      required: true
    },
    isRecording: {
      type: Boolean,
      required: true
    },
    activeRecording: {
      type: Object,
      default: null
    },
    templates: {
      type: Array,
      default: () => []
    },
    selectedTemplate: {
      type: Object,
      default: null
    }
  },
  emits: ['start-recording', 'stop-recording', 'refresh-devices'],
  setup(props, { emit }) {
    const filename = ref('')
    const selectedDevice = ref(null)
    const selectedChannels = ref([1, 2])
    const selectedTemplateId = ref(null)

    // Auto-select first device when devices load
    watch(() => props.audioDevices, (devices) => {
      if (devices.length > 0 && selectedDevice.value === null) {
        selectedDevice.value = devices[0].index
      }
    }, { immediate: true })

    // Watch for external template selection (from TemplateManager)
    watch(() => props.selectedTemplate, (template) => {
      if (template) {
        selectedTemplateId.value = template.id
        applyTemplate()
      }
    })

    const availableChannels = computed(() => {
      const device = props.audioDevices.find(d => d.index === selectedDevice.value)
      if (!device) return []
      return Array.from({ length: device.input_channel_count }, (_, i) => i + 1)
    })

    // Reset channel selection when device changes
    watch(selectedDevice, () => {
      // Only reset if no template is selected
      if (!selectedTemplateId.value) {
        selectedChannels.value = [1, 2]
      }
    })

    const applyTemplate = async () => {
      if (!selectedTemplateId.value) {
        selectedChannels.value = [1, 2]
        return
      }

      const template = props.templates.find(t => t.id === selectedTemplateId.value)
      if (!template) return

      try {
        // Load template channels
        const channels = await apiService.getTemplateChannels(template.id)
        console.log('Loaded template channels:', channels)
        
        // Set selected channels based on template
        const channelNumbers = channels.map(ch => ch.channel_no)
        console.log('Setting channel numbers:', channelNumbers)
        
        // Force reactivity update by creating new array
        selectedChannels.value = [...channelNumbers.sort((a, b) => a - b)]
        console.log('Selected channels updated to:', selectedChannels.value)
      } catch (error) {
        console.error('Failed to load template channels:', error)
      }
    }

    const toggleChannel = (channel) => {
      const index = selectedChannels.value.indexOf(channel)
      if (index > -1) {
        selectedChannels.value.splice(index, 1)
      } else {
        selectedChannels.value.push(channel)
        selectedChannels.value.sort((a, b) => a - b)
      }
    }

    const handleStart = () => {
      const recordingData = {
        audiodevice_index: selectedDevice.value,
        channels: selectedChannels.value
      }
      
      if (filename.value.trim()) {
        let fname = filename.value.trim()
        if (!fname.endsWith('.wav')) {
          fname += '.wav'
        }
        recordingData.filename = fname
      }

      emit('start-recording', recordingData)
      
      // Reset template selection after starting
      selectedTemplateId.value = null
    }

    const handleStop = () => {
      if (props.activeRecording) {
        emit('stop-recording', props.activeRecording.id)
      }
    }

    const formatChannels = (channels) => {
      if (!channels || !Array.isArray(channels)) return 'N/A'
      return channels.map(ch => ch + 1).join(', ')
    }

    const getStateLabel = (state) => {
      const labels = {
        0: 'New',
        1: 'Recording',
        2: 'Stopping',
        3: 'Stopped'
      }
      return labels[state] || 'Unknown'
    }

    return {
      filename,
      selectedDevice,
      selectedChannels,
      selectedTemplateId,
      availableChannels,
      applyTemplate,
      toggleChannel,
      handleStart,
      handleStop,
      formatChannels,
      getStateLabel
    }
  }
}
</script>

<style scoped>
.recording-controls {
  margin-bottom: 2rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a202c;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  font-weight: 500;
  font-size: 0.875rem;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input,
.select {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
  font-family: inherit;
}

.input:focus,
.select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.device-select-wrapper {
  display: flex;
  gap: 0.5rem;
}

.device-select-wrapper .select {
  flex: 1;
}

.btn-icon {
  padding: 0.75rem;
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.btn-icon svg {
  width: 20px;
  height: 20px;
  color: #4a5568;
}

.channel-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.channel-chip {
  padding: 0.5rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.channel-chip:hover {
  border-color: #cbd5e0;
  background: #f7fafc;
}

.channel-chip.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.help-text {
  margin: 0;
  font-size: 0.875rem;
  color: #718096;
}

.btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: inherit;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:not(:disabled):hover {
  background: #5568d3;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:not(:disabled):hover {
  background: #e53e3e;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.4);
}

.btn-icon-svg {
  width: 20px;
  height: 20px;
}

.recording-status {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #fef5e7;
  border: 2px solid #f39c12;
  border-radius: 8px;
}

.pulse {
  width: 12px;
  height: 12px;
  background: #e74c3c;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.1);
  }
}

.status-text {
  font-weight: 600;
  color: #c0392b;
}

.recording-info {
  padding: 1rem;
  background: #f7fafc;
  border-radius: 8px;
}

.recording-info p {
  margin: 0.5rem 0;
  font-size: 0.875rem;
  color: #4a5568;
}

.recording-info strong {
  color: #2d3748;
}

@media (max-width: 768px) {
  .card {
    padding: 1.5rem;
  }

  .card-title {
    font-size: 1.25rem;
  }

  .channel-selector {
    max-height: 200px;
    overflow-y: auto;
  }
}
</style>
