<!-- Root component — rendered once for the entire app lifetime.
     Contains the shared hero banner, the NavBar, and a <RouterView>
     which swaps in whichever view the current route maps to. -->

<script setup>
import { RouterView } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
</script>

<template>
  <!-- Maroon hero header shown on every page -->
  <header class="hero">
    <div class="hero-content">
      <div>
        <h1>TAMU Grade Distribution</h1>
        <p>Search any course to see grade distributions across semesters</p>
      </div>
      <!-- Texas A&M logo served from the public/ folder (no import needed) -->
      <img src="/CMYK-TAM-Stacked-AllWhite.svg" alt="Texas A&M Logo" class="hero-logo" />
    </div>
  </header>

  <!-- Navigation bar with dropdown tabs for Courses, Professors, and My Courses -->
  <NavBar />

  <!-- RouterView renders the active page component based on the current URL -->
  <RouterView />
</template>

<style>
/* Global reset — applied to every element in the app -->
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #222;
  background: #f9f9f9;
}

/* Hero banner styles are global (not scoped) because they live in the root component */
.hero {
  background: #5c0000;
  color: white;
  padding: 28px 40px;
}

.hero-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 900px;
  margin: 0 auto;
}

.hero h1 {
  margin: 0 0 8px;
  font-size: 2rem;
}

.hero p {
  margin: 0;
  opacity: 0.85;
}

.hero-logo {
  height: 175px;
  object-fit: contain;
}
</style>
