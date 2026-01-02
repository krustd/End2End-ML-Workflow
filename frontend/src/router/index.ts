import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'workflow',
      component: () => import('../views/WorkflowView.vue'),
    },
    {
      path: '/models',
      name: 'models',
      component: () => import('../views/ModelView.vue'),
    },
    {
      path: '/instructions',
      name: 'instructions',
      component: () => import('../views/InstructionsView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
    },
  ],
})

export default router
