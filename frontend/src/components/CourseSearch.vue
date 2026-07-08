<script setup>
import { ref, watch } from 'vue'
import { searchCourses } from '@/api/index.js'
import { useGradesStore } from '@/stores/grades.js'

const props = defineProps({ preset: { type: String, default: null } })

const store = useGradesStore()

const query = ref('')

// When a preset course is passed in (e.g. from a URL query param), populate
// the input and trigger the search automatically
watch(
  () => props.preset,
  (course) => {
    if (course) {
      query.value = course
      store.fetchSections(course)
    }
  },
  { immediate: true },
)
const suggestions = ref([])
let debounceTimer = null

// Wait 300ms after the user stops typing before hitting the API
async function onInput() {
  clearTimeout(debounceTimer)
  if (query.value.length < 2) {
    suggestions.value = []
    return
  }
  debounceTimer = setTimeout(async () => {
    const res = await searchCourses(query.value)
    suggestions.value = res.data
  }, 300)
}

function selectCourse(course) {
  query.value = course
  suggestions.value = []
  store.fetchSections(course, store.selectedSemester)
}

function clearSearch() {
  query.value = ''
  suggestions.value = []
  store.clearSections()
}
</script>

<template>
  <div class="search-wrapper">
    <div class="search-input-row">
      <input
        v-model="query"
        type="text"
        placeholder="Search course (e.g. AERO 201 or CSCE 221)"
        @input="onInput"
      />
      <button v-if="query" @click="clearSearch">✕</button>
    </div>

    <ul v-if="suggestions.length" class="suggestions">
      <li
        v-for="course in suggestions"
        :key="course"
        @click="selectCourse(course)"
      >
        {{ course }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.search-wrapper {
  position: relative;
  width: 100%;
  max-width: 480px;
}

.search-input-row {
  display: flex;
  gap: 8px;
}

input {
  flex: 1;
  padding: 10px 14px;
  font-size: 1rem;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  outline: none;
  background: var(--input-bg);
  color: var(--text);
}

input:focus {
  border-color: var(--primary);
}

button {
  padding: 0 14px;
  background: var(--border);
  border: 1px solid var(--input-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  color: var(--text);
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: none;
  border-radius: 0 0 6px 6px;
  list-style: none;
  margin: 0;
  padding: 0;
  z-index: 10;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.suggestions li {
  padding: 10px 14px;
  cursor: pointer;
  color: var(--text);
}

.suggestions li:hover {
  background: color-mix(in srgb, var(--primary) 8%, var(--surface));
  color: var(--primary-text);
}
</style>
