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
/* ── CSS custom properties ── */
:root {
  --primary:      #5c0000;
  --primary-dark: #3a0000;
  --primary-text: #5c0000;   /* maroon text in light mode */
  --bg:           #f9f9f9;
  --surface:      #ffffff;
  --border:       #e0e0e0;
  --text:         #222222;
  --text-muted:   #888888;
  --input-bg:     #ffffff;
  --input-border: #cccccc;
}

:root.dark {
  --primary-text: #d4d4d4;   /* light grey replaces maroon text in dark mode */
  --bg:           #121212;
  --surface:      #1e1e1e;
  --border:       #333333;
  --text:         #e8e8e8;
  --text-muted:   #9e9e9e;
  --input-bg:     #2a2a2a;
  --input-border: #444444;
}

/* Global reset */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--text);
  background: var(--bg);
  transition: background 0.2s, color 0.2s;
}

/* Global input / select dark mode */
input, select, textarea {
  background: var(--input-bg);
  color: var(--text);
  border-color: var(--input-border);
}

/* Hero banner styles are global (not scoped) because they live in the root component */
.hero {
  background: var(--primary);
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
