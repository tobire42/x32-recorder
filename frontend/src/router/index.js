import { createRouter, createWebHistory } from 'vue-router'
import RecorderView from '../views/RecorderView.vue'
import TemplatesView from '../views/TemplatesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/recorder'
    },
    {
      path: '/recorder',
      name: 'recorder',
      component: RecorderView
    },
    {
      path: '/templates',
      name: 'templates',
      component: TemplatesView
    }
  ]
})

export default router
