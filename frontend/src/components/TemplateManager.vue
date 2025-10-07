<template>
  <div class="template-manager">
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">Recording Templates</h2>
        <button @click="showCreateModal = true" class="btn btn-primary-small">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          New Template
        </button>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading templates...</p>
      </div>

      <div v-else-if="templates.length === 0" class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        <p>No templates yet</p>
        <p class="empty-subtitle">Create a template to quickly set up recordings</p>
      </div>

      <div v-else class="templates-list">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-item"
          @click="$emit('select-template', template)"
        >
          <div class="template-header">
            <div class="template-title">
              <svg class="template-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <span class="name">{{ template.name }}</span>
            </div>
            <div class="template-actions">
              <button @click.stop="editTemplate(template)" class="btn-icon-small" title="Edit">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button @click.stop="confirmDelete(template.id)" class="btn-icon-small btn-danger" title="Delete">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="template-details">
            <div class="detail-badge">
              {{ template.channel_count }} channels
            </div>
            <div v-if="template.channels && template.channels.length" class="channels-list">
              <div v-for="channel in template.channels" :key="channel.id" class="channel-tag">
                Ch {{ channel.channel_no }}: {{ channel.name }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Template Modal -->
    <div v-if="showCreateModal || editingTemplate" class="modal-overlay" @click="closeModal">
      <div class="modal modal-large" @click.stop>
        <h3 class="modal-title">{{ editingTemplate ? 'Edit Template' : 'Create Template' }}</h3>
        
        <div class="form">
          <div class="form-group">
            <label class="label">Template Name</label>
            <input
              v-model="templateForm.name"
              type="text"
              class="input"
              placeholder="e.g., Full Band Recording"
            />
          </div>

          <div class="form-group">
            <label class="label">Channels to Record</label>
            <p class="help-text" style="margin-bottom: 0.5rem;">
              Select which device channels you want to record with this template
            </p>
            <div class="channel-selector-grid">
              <div
                v-for="ch in 32"
                :key="ch"
                class="channel-chip"
                :class="{ active: selectedChannels.includes(ch) }"
                @click="toggleChannelSelection(ch)"
              >
                {{ ch }}
              </div>
            </div>
            <p class="help-text" style="margin-top: 0.5rem;">
              {{ selectedChannels.length }} channel(s) selected
            </p>
          </div>

          <div v-if="selectedChannels.length > 0" class="form-group">
            <label class="label">Channel Names</label>
            <div class="channels-config">
              <div
                v-for="ch in sortedSelectedChannels"
                :key="ch"
                class="channel-config-item"
              >
                <span class="channel-number">Ch {{ ch }}</span>
                <input
                  v-model="channelNames[ch]"
                  type="text"
                  class="input input-small"
                  :placeholder="`Channel ${ch}`"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button @click="saveTemplate" class="btn btn-primary" :disabled="!templateForm.name">
            {{ editingTemplate ? 'Update' : 'Create' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <h3 class="modal-title">Confirm Delete</h3>
        <p class="modal-text">Are you sure you want to delete this template? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn btn-secondary">Cancel</button>
          <button @click="handleDelete" class="btn btn-danger">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import apiService from '../services/apiService'

export default {
  name: 'TemplateManager',
  props: {
    templates: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh', 'select-template'],
  setup(props, { emit }) {
    const showCreateModal = ref(false)
    const showDeleteModal = ref(false)
    const editingTemplate = ref(null)
    const templateToDelete = ref(null)

    const templateForm = reactive({
      name: '',
      channel_count: 0
    })

    const selectedChannels = ref([])
    const channelNames = ref({})

    const sortedSelectedChannels = computed(() => {
      return [...selectedChannels.value].sort((a, b) => a - b)
    })

    const toggleChannelSelection = (channel) => {
      const index = selectedChannels.value.indexOf(channel)
      if (index > -1) {
        selectedChannels.value.splice(index, 1)
        // Clean up the channel config when deselected
        delete channelNames.value[channel]
      } else {
        selectedChannels.value.push(channel)
      }
    }

    const resetForm = () => {
      templateForm.name = ''
      templateForm.channel_count = 0
      selectedChannels.value = []
      channelNames.value = {}
      editingTemplate.value = null
    }

    const editTemplate = async (template) => {
      editingTemplate.value = template
      templateForm.name = template.name
      templateForm.channel_count = template.channel_count

      // Load channel details
      try {
        const channels = await apiService.getTemplateChannels(template.id)
        selectedChannels.value = []
        channelNames.value = {}

        channels.forEach(channel => {
          selectedChannels.value.push(channel.channel_no)
          channelNames.value[channel.channel_no] = channel.name
        })
      } catch (error) {
        console.error('Failed to load channel details:', error)
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      resetForm()
    }

    const saveTemplate = async () => {
      if (selectedChannels.value.length === 0) {
        alert('Please select at least one channel')
        return
      }

      try {
        let template
        
        if (editingTemplate.value) {
          // Update existing template
          template = await apiService.updateTemplate(editingTemplate.value.id, {
            name: templateForm.name,
            channel_count: selectedChannels.value.length
          })
        } else {
          // Create new template
          template = await apiService.createTemplate({
            name: templateForm.name,
            channel_count: selectedChannels.value.length
          })
        }

        // Save channel configurations
        if (editingTemplate.value) {
          // Delete existing channels and recreate (simpler than updating)
          const existingChannels = await apiService.getTemplateChannels(template.id)
          for (const channel of existingChannels) {
            await apiService.deleteTemplateChannel(channel.id)
          }
        }

        // Create channels for selected channel numbers
        for (const channelNo of sortedSelectedChannels.value) {
          await apiService.createTemplateChannel({
            template: template.url,
            channel_no: channelNo,
            name: channelNames.value[channelNo] || `Channel ${channelNo}`
          })
        }

        closeModal()
        emit('refresh')
      } catch (error) {
        console.error('Failed to save template:', error)
        alert('Failed to save template. Please try again.')
      }
    }

    const confirmDelete = (id) => {
      templateToDelete.value = id
      showDeleteModal.value = true
    }

    const cancelDelete = () => {
      showDeleteModal.value = false
      templateToDelete.value = null
    }

    const handleDelete = async () => {
      if (!templateToDelete.value) return

      try {
        await apiService.deleteTemplate(templateToDelete.value)
        showDeleteModal.value = false
        templateToDelete.value = null
        emit('refresh')
      } catch (error) {
        console.error('Failed to delete template:', error)
        alert('Failed to delete template. Please try again.')
      }
    }

    return {
      showCreateModal,
      showDeleteModal,
      editingTemplate,
      templateForm,
      selectedChannels,
      sortedSelectedChannels,
      channelNames,
      toggleChannelSelection,
      editTemplate,
      closeModal,
      saveTemplate,
      confirmDelete,
      cancelDelete,
      handleDelete
    }
  }
}
</script>

<style scoped>
.template-manager {
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

.btn-primary-small {
  padding: 0.625rem 1.25rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: inherit;
}

.btn-primary-small:hover {
  background: #5568d3;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary-small svg {
  width: 16px;
  height: 16px;
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

.templates-list {
  display: grid;
  gap: 1rem;
}

.template-item {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.25rem;
  transition: all 0.2s;
  cursor: pointer;
}

.template-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.template-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.template-icon {
  width: 18px;
  height: 18px;
  color: #667eea;
  flex-shrink: 0;
}

.name {
  font-weight: 600;
  font-size: 1.125rem;
  color: #2d3748;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon-small {
  padding: 0.5rem;
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon-small:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.btn-icon-small.btn-danger {
  border-color: #feb2b2;
  background: #fee;
}

.btn-icon-small.btn-danger:hover {
  border-color: #fc8181;
  background: #fed7d7;
}

.btn-icon-small svg {
  width: 16px;
  height: 16px;
  color: #4a5568;
}

.btn-icon-small.btn-danger svg {
  color: #c53030;
}

.template-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #edf2f7;
  color: #4a5568;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  width: fit-content;
}

.channels-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.channel-tag {
  padding: 0.375rem 0.75rem;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #4a5568;
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
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-large {
  max-width: 700px;
}

.modal-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a202c;
}

.modal-text {
  margin: 0 0 1.5rem 0;
  color: #4a5568;
  line-height: 1.6;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
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

.input {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
  font-family: inherit;
}

.input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-small {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.channel-selector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
}

.channel-chip {
  padding: 0.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  text-align: center;
  background: white;
}

.channel-chip:hover {
  border-color: #cbd5e0;
  background: #f7fafc;
}

.channel-chip.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
  transform: scale(1.05);
}

.channels-config {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
  padding: 0.5rem;
  background: #f7fafc;
  border-radius: 8px;
}

.channel-config-item {
  display: grid;
  grid-template-columns: 50px 1fr;
  align-items: center;
  gap: 0.75rem;
}

.channel-number {
  font-weight: 600;
  font-size: 0.875rem;
  color: #4a5568;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
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

@media (max-width: 768px) {
  .card {
    padding: 1.5rem;
  }

  .card-title {
    font-size: 1.25rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .channel-config-item {
    grid-template-columns: 40px 1fr;
    gap: 0.5rem;
  }

  .checkbox-label {
    grid-column: 2;
  }
}
</style>
