<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useProfessorStore } from '@/stores/professor.js'

const store = useProfessorStore()

const PAGE_SIZE = 20
const currentPage = ref(1)

watch(
  () => store.sections,
  () => { currentPage.value = 1 },
)

function semesterSortKey(sem) {
  const [term, year] = sem.split(' ')
  const termOrder = { Spring: 1, Summer: 2, Fall: 3 }
  return parseInt(year) * 10 + (termOrder[term] ?? 0)
}

const sortedSections = computed(() =>
  [...store.sections].sort(
    (a, b) => semesterSortKey(b.semester) - semesterSortKey(a.semester),
  ),
)

const totalPages = computed(() => Math.ceil(sortedSections.value.length / PAGE_SIZE))
const startIndex = computed(() => (currentPage.value - 1) * PAGE_SIZE)
const endIndex = computed(() => Math.min(startIndex.value + PAGE_SIZE, sortedSections.value.length))
const paginatedSections = computed(() => sortedSections.value.slice(startIndex.value, endIndex.value))

function prevPage() { if (currentPage.value > 1) currentPage.value-- }
function nextPage() { if (currentPage.value < totalPages.value) currentPage.value++ }
</script>

<template>
  <div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Semester</th>
            <th>Course</th>
            <th>Section</th>
            <th>GPA</th>
            <th>A</th>
            <th>B</th>
            <th>C</th>
            <th>D</th>
            <th>F</th>
            <th>Q</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in paginatedSections" :key="s.id">
            <td>{{ s.semester }}</td>
            <td>
              <RouterLink :to="`/?course=${s.course}`" class="course-link">{{ s.course }}</RouterLink>
            </td>
            <td>{{ s.section }}</td>
            <td>
              <span v-if="s.gpa === 0" class="su-badge">S/U</span>
              <span v-else>{{ s.gpa ?? '—' }}</span>
            </td>
            <td>{{ s.a }}</td>
            <td>{{ s.b }}</td>
            <td>{{ s.c }}</td>
            <td>{{ s.d }}</td>
            <td>{{ s.f }}</td>
            <td>{{ s.q }}</td>
            <td>{{ s.total }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button :disabled="currentPage === 1" @click="prevPage">&#8592;</button>
      <span class="page-info">{{ startIndex + 1 }}–{{ endIndex }} of {{ sortedSections.length }}</span>
      <button :disabled="currentPage === totalPages" @click="nextPage">&#8594;</button>
    </div>
  </div>
</template>

<style scoped>
.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  color: var(--text);
}

thead tr {
  background: var(--primary);
  color: white;
}

th, td {
  padding: 10px 12px;
  text-align: left;
  white-space: nowrap;
}

tbody tr {
  background: var(--surface);
}

tbody tr:nth-child(even) {
  background: var(--bg);
}

tbody tr:hover {
  background: color-mix(in srgb, var(--primary) 6%, var(--surface));
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.pagination button {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--text);
  transition: background 0.15s;
}

.pagination button:hover:not(:disabled) {
  border-color: var(--primary);
}

.pagination button:disabled { opacity: 0.35; cursor: default; }

.course-link {
  color: var(--primary-text);
  text-decoration: none;
  font-weight: 500;
}

.course-link:hover {
  text-decoration: underline;
}

.page-info {
  font-size: 0.9rem;
  color: var(--text-muted);
  min-width: 120px;
  text-align: center;
}

.su-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  background: color-mix(in srgb, var(--text-muted) 18%, var(--surface));
  color: var(--text-muted);
  letter-spacing: 0.03em;
}
</style>
