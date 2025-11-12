<template>
  <div class="templates-view">
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <TemplateManager
      :templates="templates"
      :loading="loadingTemplates"
      @refresh="fetchTemplates"
      @select-template="selectTemplate"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TemplateManager from '../components/TemplateManager.vue'
import apiService from '../services/apiService'

export default {
  name: 'TemplatesView',
  components: {
    TemplateManager
  },
  setup() {
    const router = useRouter()
    const templates = ref([])
    const loadingTemplates = ref(false)
    const error = ref(null)

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
      // Navigate to recorder view when template is selected
      router.push('/recorder')
    }

    onMounted(() => {
      fetchTemplates()
    })

    return {
      templates,
      loadingTemplates,
      error,
      fetchTemplates,
      selectTemplate
    }
  }
}
</script>

<style scoped>
.templates-view {
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
