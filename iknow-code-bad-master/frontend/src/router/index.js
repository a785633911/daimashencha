import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/ai-config' },
  { path: '/ai-config', component: () => import('../views/AIConfig.vue') },
  { path: '/projects', component: () => import('../views/Projects.vue') },
  { path: '/review', component: () => import('../views/Review.vue') },
  { path: '/branch-review', component: () => import('../views/BranchReview.vue') },
  { path: '/issue/:id', component: () => import('../views/IssueDetail.vue') }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
