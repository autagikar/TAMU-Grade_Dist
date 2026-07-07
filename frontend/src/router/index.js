// Vue Router configuration.
// Each route maps a URL path to a view component.
// Views are lazy-loaded by default in production builds (code splitting),
// but here they're imported directly since the app is small.

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ProfessorView from '@/views/ProfessorView.vue'
import CompareView from '@/views/CompareView.vue'
import CompareProfessorView from '@/views/CompareProfessorView.vue'
import MyCoursesView from '@/views/MyCoursesView.vue'

const router = createRouter({
  // createWebHistory uses the browser's History API for clean URLs (/professor
  // instead of /#/professor). Requires the dev server to serve index.html for
  // all routes — Vite does this automatically.
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',                   component: HomeView },           // Course Search
    { path: '/professor',          component: ProfessorView },      // Professor Lookup
    { path: '/compare',            component: CompareView },         // Compare Courses
    { path: '/compare-professor',  component: CompareProfessorView },// Compare Professors
    { path: '/my-courses',         component: MyCoursesView },       // My Courses
  ],
})

export default router
