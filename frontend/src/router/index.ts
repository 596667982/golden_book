import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/practice' },
    { path: '/practice', component: () => import('@/views/PracticeEntryView.vue') },
    { path: '/exams', component: () => import('@/views/ExamsView.vue') },
    { path: '/exams/:id', component: () => import('@/views/ExamDetailView.vue') },
    { path: '/exams/:id/practice', component: () => import('@/views/PracticeView.vue') },
    { path: '/sessions', component: () => import('@/views/SessionsView.vue') },
    { path: '/sessions/:id/results', component: () => import('@/views/ResultsView.vue') },
    { path: '/settings', component: () => import('@/views/SettingsView.vue') },
  ]
})

export default router
