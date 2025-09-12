import { createRouter, createWebHistory } from 'vue-router'
import RawView from '@/views/RawView.vue'
import MonthlyView from '@/views/MonthlyView.vue'
import YearlyView from '@/views/YearlyView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/raw',
      name: 'raw',
      component: RawView,
    },
    {
      path: '/',
      name: 'monthly',
      component: MonthlyView,
    },
    {
      path: '/',
      name: 'yearly',
      component: YearlyView,
    },
  ],
})

export default router
