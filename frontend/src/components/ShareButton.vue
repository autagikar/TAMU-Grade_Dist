<!-- Copies the current page URL to the clipboard and briefly shows "Copied!" -->

<script setup>
import { ref } from 'vue'

const copied = ref(false)

async function share() {
  await navigator.clipboard.writeText(window.location.href)
  copied.value = true
  setTimeout(() => (copied.value = false), 2000)
}
</script>

<template>
  <button class="share-btn" @click="share">
    {{ copied ? '✓ Copied!' : '⎘ Share Link' }}
  </button>
</template>

<style scoped>
.share-btn {
  padding: 8px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text-muted);
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s, border-color 0.15s;
}

.share-btn:hover {
  color: var(--primary);
  border-color: var(--primary);
}
</style>
