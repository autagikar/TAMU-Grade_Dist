<script setup>
import { ref, watch } from 'vue'
import { searchInstructors } from '@/api/index.js'
import { useProfessorStore } from '@/stores/professor.js'

const props = defineProps({ preset: { type: String, default: null } })

const store = useProfessorStore()

const query = ref('')

watch(
  () => props.preset,
  (instructor) => {
    if (instructor) {
      query.value = instructor
      store.fetchSections(instructor)
    }
  },
  { immediate: true },
)
const suggestions = ref([])
let debounceTimer = null

async function onInput() {
  clearTimeout(debounceTimer)
  if (query.value.length < 2) {
    suggestions.value = []
    return
  }
  debounceTimer = setTimeout(async () => {
    const res = await searchInstructors(query.value)
    suggestions.value = res.data
  }, 300)
}

function selectInstructor(instructor) {
  query.value = instructor
  suggestions.value = []
  store.fetchSections(instructor, store.selectedSemester)
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
        placeholder="Search professor (e.g. Smith or J. Smith)"
        @input="onInput"
      />
      <button v-if="query" @click="clearSearch">✕</button>
    </div>

    <ul v-if="suggestions.length" class="suggestions">
      <li v-for="inst in suggestions" :key="inst" @click="selectInstructor(inst)">
        {{ inst }}
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
  border: 1px solid #ccc;
  border-radius: 6px;
  outline: none;
}

input:focus {
  border-color: #5c0000;
}

button {
  padding: 0 14px;
  background: #eee;
  border: 1px solid #ccc;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  border-top: none;
  border-radius: 0 0 6px 6px;
  list-style: none;
  margin: 0;
  padding: 0;
  z-index: 10;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
  max-height: 240px;
  overflow-y: auto;
}

.suggestions li {
  padding: 10px 14px;
  cursor: pointer;
}

.suggestions li:hover {
  background: #f5f5f5;
}
</style>
