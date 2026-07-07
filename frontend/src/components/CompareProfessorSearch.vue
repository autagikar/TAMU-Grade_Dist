<!-- Reusable autocomplete search input for professor/instructor names.
     Used on the Compare Professors page for both the Professor A and Professor B slots.
     Identical in structure to CompareSearch.vue but calls searchInstructors instead. -->

<script setup>
import { ref, watch } from 'vue'
import { searchInstructors } from '@/api/index.js'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Search professor (e.g. J. Smith)' },
})
const emit = defineEmits(['update:modelValue', 'select'])

const query = ref(props.modelValue || '')
const suggestions = ref([])
const showDropdown = ref(false)
let debounceTimer = null

// Debounce: wait 250ms after the user stops typing before hitting the API
watch(query, (val) => {
  emit('update:modelValue', val)
  clearTimeout(debounceTimer)
  if (!val || val.length < 2) { suggestions.value = []; showDropdown.value = false; return }
  debounceTimer = setTimeout(async () => {
    const res = await searchInstructors(val)
    suggestions.value = res.data
    showDropdown.value = res.data.length > 0
  }, 250)
})

// Fill the input, hide the dropdown, and notify the parent of the selection
function select(instructor) {
  query.value = instructor
  suggestions.value = []
  showDropdown.value = false
  emit('select', instructor)
}

// Delayed blur so mousedown on a list item fires before the dropdown closes
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
      <!-- mousedown.prevent prevents blur from stealing the click -->
      <li
        v-for="inst in suggestions"
        :key="inst"
        @mousedown.prevent="select(inst)"
      >
        {{ inst }}
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
