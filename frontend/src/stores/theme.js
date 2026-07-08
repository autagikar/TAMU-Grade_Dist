import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('tamu_theme') === 'dark')

  // Apply the class to <html> immediately on store init
  if (isDark.value) document.documentElement.classList.add('dark')

  function toggle() {
    isDark.value = !isDark.value
    document.documentElement.classList.toggle('dark', isDark.value)
    localStorage.setItem('tamu_theme', isDark.value ? 'dark' : 'light')
  }

  return { isDark, toggle }
})
