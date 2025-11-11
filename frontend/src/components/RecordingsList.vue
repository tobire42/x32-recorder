<template>
  <div class="recordings-list">
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">Recordings</h2>
        <button @click="$emit('refresh')" class="btn-icon" title="Refresh recordings">
          <RefreshIcon />
        </button>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading recordings...</p>
      </div>

      <div v-else-if="recordings.length === 0" class="empty-state">
        <AlertIcon class="empty-icon" />
        <p>No recordings yet</p>
        <p class="empty-subtitle">Start a new recording to see it here</p>
      </div>

      <div v-else class="recordings-grid">
        <div
          v-for="recording in sortedRecordings"
          :key="recording.id"
          class="recording-item"
          :class="{ active: isActive(recording.state) }"
        >
          <div class="recording-header">
            <div class="recording-title">
              <RecordIcon class="recording-icon" />
              <span class="filename">{{ recording.name }}</span>
            </div>
            <span class="state-badge" :class="getStateBadgeClass(recording.state)">
              {{ getStateLabel(recording.state) }}
            </span>
          </div>

          <div class="recording-details">
            <div class="detail-item">
              <CalendarIcon class="detail-icon" />
              <span>{{ formatDate(recording.date) }}</span>
            </div>

            <div class="detail-item">
              <MusicIcon class="detail-icon" />
              <span>{{ formatChannels(recording.channels) }}</span>
            </div>

            <div v-if="recording.duration" class="detail-item">
              <ClockIcon class="detail-icon" />
              <span>{{ recording.duration }}</span>
            </div>

            <div class="detail-item">
              <DeviceIcon class="detail-icon" />
              <span>Device {{ recording.audiodevice_index }}</span>
            </div>
          </div>

          <div v-if="recording.state === 3" class="recording-actions">
            <button @click="confirmDelete(recording.id)" class="btn btn-delete" title="Delete recording">
              <DeleteIcon />
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <h3 class="modal-title">Confirm Delete</h3>
        <p class="modal-text">Are you sure you want to delete this recording? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn btn-secondary">Cancel</button>
          <button @click="handleDelete" class="btn btn-danger">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import apiService from '../services/apiService'
import RefreshIcon from './icons/RefreshIcon.vue'
import AlertIcon from './icons/AlertIcon.vue'
import RecordIcon from './icons/RecordIcon.vue'
import CalendarIcon from './icons/CalendarIcon.vue'
import MusicIcon from './icons/MusicIcon.vue'
import ClockIcon from './icons/ClockIcon.vue'
import DeviceIcon from './icons/DeviceIcon.vue'
import DeleteIcon from './icons/DeleteIcon.vue'

export default {
  name: 'RecordingsList',
  components: {
    RefreshIcon,
    AlertIcon,
    RecordIcon,
    CalendarIcon,
    MusicIcon,
    ClockIcon,
    DeviceIcon,
    DeleteIcon
  },
  props: {
    recordings: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  setup(props, { emit }) {
    const showDeleteModal = ref(false)
    const recordingToDelete = ref(null)

    const sortedRecordings = computed(() => {
      return [...props.recordings].sort((a, b) => {
        return new Date(b.date) - new Date(a.date)
      })
    })

    const isActive = (state) => {
      return state === 0 || state === 1 || state === 2
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

    const getStateBadgeClass = (state) => {
      const classes = {
        0: 'badge-new',
        1: 'badge-recording',
        2: 'badge-stopping',
        3: 'badge-stopped'
      }
      return classes[state] || 'badge-default'
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString()
    }

    const formatChannels = (channels) => {
      if (!channels || !Array.isArray(channels)) return 'N/A'
      const displayChannels = channels.map(ch => ch + 1)
      if (displayChannels.length <= 3) {
        return `Ch ${displayChannels.join(', ')}`
      }
      return `${displayChannels.length} channels`
    }

    const confirmDelete = (id) => {
      recordingToDelete.value = id
      showDeleteModal.value = true
    }

    const cancelDelete = () => {
      showDeleteModal.value = false
      recordingToDelete.value = null
    }

    const handleDelete = async () => {
      if (!recordingToDelete.value) return

      try {
        await apiService.deleteRecording(recordingToDelete.value)
        showDeleteModal.value = false
        recordingToDelete.value = null
        emit('refresh')
      } catch (error) {
        console.error('Failed to delete recording:', error)
        alert('Failed to delete recording. Please try again.')
      }
    }

    return {
      showDeleteModal,
      sortedRecordings,
      isActive,
      getStateLabel,
      getStateBadgeClass,
      formatDate,
      formatChannels,
      confirmDelete,
      cancelDelete,
      handleDelete
    }
  }
}
</script>

<style scoped>
.recordings-list {
  margin-bottom: 2rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a202c;
}

.btn-icon {
  padding: 0.5rem;
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

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #718096;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #718096;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
  color: #cbd5e0;
}

.empty-subtitle {
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.recordings-grid {
  display: grid;
  gap: 1rem;
}

.recording-item {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.25rem;
  transition: all 0.2s;
}

.recording-item:hover {
  border-color: #cbd5e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.recording-item.active {
  border-color: #667eea;
  background: #f7faff;
}

.recording-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.recording-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.recording-icon {
  width: 16px;
  height: 16px;
  color: #667eea;
  flex-shrink: 0;
}

.filename {
  font-weight: 600;
  color: #2d3748;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.state-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  flex-shrink: 0;
}

.badge-new {
  background: #e3f2fd;
  color: #1976d2;
}

.badge-recording {
  background: #fff3e0;
  color: #f57c00;
}

.badge-stopping {
  background: #fce4ec;
  color: #c2185b;
}

.badge-stopped {
  background: #f1f5f9;
  color: #64748b;
}

.recording-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #4a5568;
}

.detail-icon {
  width: 16px;
  height: 16px;
  color: #718096;
  flex-shrink: 0;
}

.recording-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: inherit;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn-delete {
  background: #fee;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.btn-delete:hover {
  background: #fed7d7;
  border-color: #fc8181;
}

.btn-secondary {
  background: #f7fafc;
  color: #4a5568;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-title {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.modal-text {
  margin: 0 0 1.5rem 0;
  color: #4a5568;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .card {
    padding: 1.5rem;
  }

  .card-title {
    font-size: 1.25rem;
  }

  .recording-details {
    grid-template-columns: 1fr;
  }

  .recording-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
