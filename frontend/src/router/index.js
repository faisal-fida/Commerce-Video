import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'VideoShowcase',
    component: () => import('../views/VideoShowcase.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router