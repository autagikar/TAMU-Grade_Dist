<!-- Navigation bar rendered on every page (mounted in App.vue).
     Two tabs have dropdowns (Courses, Professors); My Courses is a direct link.
     The active tab is highlighted based on the current route path. -->

<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme.js'

const route = useRoute()
const theme = useThemeStore()

// Touch devices can't hover, so tapping a tab toggles its dropdown open.
// Tracks which dropdown is open ('courses' | 'professors' | null).
const openMenu = ref(null)

function toggleMenu(name) {
  openMenu.value = openMenu.value === name ? null : name
}

// Close the open dropdown after navigating or when tapping outside the navbar
watch(() => route.path, () => (openMenu.value = null))

function handleOutsideClick(e) {
  if (!e.target.closest('.nav-group')) openMenu.value = null
}

onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))

// Mark the Courses tab as active when on any course-related page
const coursesActive = computed(() => ['/', '/compare', '/course-rankings'].includes(route.path))

// Mark the Professors tab as active when on any professor-related page
const professorsActive = computed(() => ['/professor', '/compare-professor', '/rankings'].includes(route.path))

// Mark My Courses as active when on the my-courses page
const myCoursesActive = computed(() => route.path === '/my-courses')
</script>

<template>
  <nav class="navbar">
    <!-- Courses dropdown: Course Search + Compare Courses -->
    <div class="nav-group" :class="{ active: coursesActive, open: openMenu === 'courses' }">
      <button type="button" class="nav-tab" @click="toggleMenu('courses')">Courses</button>
      <div class="dropdown">
        <RouterLink to="/" class="dropdown-link">Course Search</RouterLink>
        <RouterLink to="/compare" class="dropdown-link">Compare Courses</RouterLink>
        <RouterLink to="/course-rankings" class="dropdown-link">Course Rankings</RouterLink>
      </div>
    </div>

    <!-- Professors dropdown: Professor Lookup + Compare Professors -->
    <div class="nav-group" :class="{ active: professorsActive, open: openMenu === 'professors' }">
      <button type="button" class="nav-tab" @click="toggleMenu('professors')">Professors</button>
      <div class="dropdown">
        <RouterLink to="/professor" class="dropdown-link">Professor Lookup</RouterLink>
        <RouterLink to="/compare-professor" class="dropdown-link">Compare Professors</RouterLink>
        <RouterLink to="/rankings" class="dropdown-link">Department Rankings</RouterLink>
      </div>
    </div>

    <!-- My Courses is a single page so it's a direct link, not a dropdown -->
    <RouterLink to="/my-courses" class="nav-tab nav-direct" :class="{ active: myCoursesActive }">
      My Courses
    </RouterLink>

    <!-- Dark mode toggle pushed to the far right -->
    <button class="theme-toggle" @click="theme.toggle" :title="theme.isDark ? 'Switch to light mode' : 'Switch to dark mode'">
      {{ theme.isDark ? '☀' : '☾' }}
    </button>
  </nav>
</template>

<style scoped>
.navbar {
  background: #3a0000;
  display: flex;
  gap: 4px;
  padding: 0 40px;
  position: relative;
  z-index: 50;
  align-items: stretch;
}

.theme-toggle {
  margin-left: auto;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0 12px;
  line-height: 1;
  transition: color 0.15s;
}

.theme-toggle:hover {
  color: white;
}

/* A nav-group is the wrapper div that holds the tab label + dropdown */
.nav-group {
  position: relative;
  display: flex;
  align-items: stretch;
}

.nav-tab {
  background: transparent;
  border: none;
  font-family: inherit;
  color: rgba(255, 255, 255, 0.75);
  padding: 12px 18px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;
  user-select: none;
}

/* Show the ▾ caret only on dropdown tabs, not the direct My Courses link */
.nav-tab:not(.nav-direct)::after {
  content: '▾';
  font-size: 0.7rem;
  opacity: 0.6;
}

/* Styles for the My Courses direct RouterLink, which is also a nav-tab */
.nav-direct {
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  border-bottom: 3px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  display: flex;
  align-items: center;
}

.nav-direct:hover,
.nav-direct.active {
  color: white;
}

.nav-direct.active {
  border-bottom-color: white;
}

/* Highlight the tab label when hovered or when its route is active */
.nav-group:hover .nav-tab,
.nav-group.active .nav-tab {
  color: white;
}

.nav-group.active .nav-tab {
  border-bottom-color: white;
}

/* Dropdown panel — hidden by default, shown on hover via CSS (no JS needed) */
.dropdown {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 180px;
  background: #2a0000;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
  overflow: hidden;
  flex-direction: column;
}

/* Hover-open only on devices with a real pointer; touch devices use tap-to-toggle */
@media (hover: hover) {
  .nav-group:hover .dropdown {
    display: flex;
  }
}

.nav-group.open .dropdown {
  display: flex;
}

.dropdown-link {
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  padding: 11px 18px;
  font-size: 0.9rem;
  transition: background 0.12s, color 0.12s;
  white-space: nowrap;
}

.dropdown-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* Bold the link for the page currently being viewed */
.dropdown-link.router-link-active {
  color: white;
  background: rgba(255, 255, 255, 0.08);
  font-weight: 600;
}
</style>
