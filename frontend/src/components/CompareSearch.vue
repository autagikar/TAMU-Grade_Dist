<!-- Reusable autocomplete search input for course names.
     Used on the Compare Courses page for both the Course A and Course B slots.
     Emits a 'select' event with the chosen course string when the user picks one. -->

<script setup>
import { ref, watch } from 'vue'
import { searchCourses } from '@/api/index.js'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Search course (e.g. CSCE-121)' },
})
const emit = defineEmits(['update:modelValue', 'select'])

const query = ref(props.modelValue || '')
const suggestions = ref([])
const showDropdown = ref(false)
let debounceTimer = null

// Debounce API calls — waits 250ms after the user stops typing before searching.
// This avoids sending a request for every single keystroke.
watch(query, (val) => {
  emit('update:modelValue', val)
  clearTimeout(debounceTimer)
  if (!val || val.length < 2) { suggestions.value = []; showDropdown.value = false; return }
  debounceTimer = setTimeout(async () => {
    const res = await searchCourses(val)
    suggestions.value = res.data
    showDropdown.value = res.data.length > 0
  }, 250)
})

// When the user clicks a suggestion, fill the input and notify the parent
function select(course) {
  query.value = course
  suggestions.value = []
  showDropdown.value = false
  emit('select', course)
}

// Close the dropdown after a short delay on blur so that a mousedown on a
// suggestion item still fires before the dropdown disappears.
function onBlur() {
  setTimeout(() => { showDropdown.value = false }, 150)
}
</script>

<template>
  <div class="compare-search">
    <input
      v-model="query"
      :placeholder="placeholder"
      class="search-input"
      autocomplete="off"
      @focus="showDropdown = suggestions.length > 0"
      @blur="onBlur"
    />
    <ul v-if="showDropdown" class="suggestions">
      <!-- mousedown.prevent stops the blur from firing before the click registers -->
      <li
        v-for="course in suggestions"
        :key="course"
        @mousedown.prevent="select(course)"
      >
        {{ course }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.compare-search {
  position: relative;
  flex: 1;
}

.search-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #5c0000;
}

.suggestions {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  border-radius: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 220px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.suggestions li {
  padding: 10px 14px;
  cursor: pointer;
  font-size: 0.95rem;
}

.suggestions li:hover {
  background: #f0e8e8;
  color: #5c0000;
}
</style>
