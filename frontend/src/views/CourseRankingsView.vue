<!-- Course Rankings page.
     User picks a department and sees all courses sorted by difficulty rating.
     Columns are sortable. Course names link to the Course Search page. -->

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useCourseRankingsStore } from '@/stores/courseRankings.js'
const store = useCourseRankingsStore()

const sortKey = ref('avg_gpa')
const sortDir = ref('asc') // ascending = lowest GPA (hardest) first

const PAGE_SIZE = 20
const currentPage = ref(1)

onMounted(() => store.fetchDepartments())

function pickDepartment(e) {
  const dept = e.target.value
  if (dept) store.fetchRankings(dept)
  else store.clear()
}

function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortKey.value = key
    sortDir.value = key === 'avg_gpa' ? 'asc' : 'desc'
  }
  currentPage.value = 1
}

const sorted = computed(() => {
  return [...store.rankings].sort((a, b) => {
    const av = a[sortKey.value] ?? -Infinity
    const bv = b[sortKey.value] ?? -Infinity
    return sortDir.value === 'desc' ? bv - av : av - bv
  })
})

// Reset to page 1 whenever the department changes
watch(() => store.rankings, () => { currentPage.value = 1 })

const totalPages = computed(() => Math.ceil(sorted.value.length / PAGE_SIZE))
const startIndex = computed(() => (currentPage.value - 1) * PAGE_SIZE)
const endIndex   = computed(() => Math.min(startIndex.value + PAGE_SIZE, sorted.value.length))
const paginated  = computed(() => sorted.value.slice(startIndex.value, endIndex.value))

function prevPage() { if (currentPage.value > 1) currentPage.value-- }
function nextPage() { if (currentPage.value < totalPages.value) currentPage.value++ }

function arrow(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'desc' ? ' ▼' : ' ▲'
}

// Dynamic color scale: the lowest GPA in the dataset maps to full red,
// the highest maps to full green. Every department gets its own range.
const minGpa = computed(() => {
  const vals = store.rankings.map(c => c.avg_gpa).filter(v => v != null)
  return vals.length ? Math.min(...vals) : 2.0
})

const maxGpa = computed(() => {
  const vals = store.rankings.map(c => c.avg_gpa).filter(v => v != null)
  return vals.length ? Math.max(...vals) : 4.0
})

function gpaColor(gpa) {
  if (gpa == null) return 'var(--border)'
  const range = maxGpa.value - minGpa.value
  const hue = range === 0 ? 60 : ((gpa - minGpa.value) / range) * 120
  return `hsl(${hue}, 58%, 36%)`
}

</script>

<template>
  <div class="page">
    <main class="content">
      <h1 class="title">Course Rankings</h1>
      <p class="subtitle">Browse all courses in a department ranked by difficulty.</p>

      <select class="dept-select" @change="pickDepartment">
        <option value="">Select a department…</option>
        <option v-for="dept in store.departments" :key="dept" :value="dept">{{ dept }}</option>
      </select>

      <p v-if="store.loading" class="status">Loading...</p>

      <template v-else-if="sorted.length">
      <p class="count">{{ sorted.length }} courses in <strong>{{ store.selectedDepartment }}</strong></p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th class="rank-col">Rank</th>
              <th>Course</th>
              <th class="sortable" @click="setSort('avg_gpa')">Avg GPA{{ arrow('avg_gpa') }}</th>
              <th class="sortable" @click="setSort('a_percent')">A%{{ arrow('a_percent') }}</th>
              <th class="sortable" @click="setSort('f_percent')">F%{{ arrow('f_percent') }}</th>
              <th class="sortable" @click="setSort('q_percent')">Q-Drop%{{ arrow('q_percent') }}</th>
              <th class="sortable" @click="setSort('total_students')">Students{{ arrow('total_students') }}</th>
              <th class="sortable" @click="setSort('sections_count')">Sections{{ arrow('sections_count') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(course, i) in paginated" :key="course.course">
              <td class="rank-col">
                <span class="rank-num">{{ startIndex + i + 1 }}</span>
              </td>
              <td>
                <RouterLink :to="`/?course=${course.course}`" class="course-link">
                  {{ course.course }}
                </RouterLink>
              </td>
              <td>{{ course.avg_gpa ?? '—' }}</td>
              <td>{{ course.a_percent }}%</td>
              <td>{{ course.f_percent }}%</td>
              <td>{{ course.q_percent }}%</td>
              <td>{{ course.total_students.toLocaleString() }}</td>
              <td>{{ course.sections_count }}</td>
            </tr>
          </tbody>
        </table>

        <div class="pagination">
          <button :disabled="currentPage === 1" @click="prevPage">&#8592;</button>
          <span class="page-info">{{ startIndex + 1 }}–{{ endIndex }} of {{ sorted.length }}</span>
          <button :disabled="currentPage === totalPages" @click="nextPage">&#8594;</button>
        </div>
      </div>
      </template>

      <!-- Heatmap grid — shown below the table once a department is loaded -->
      <div v-if="sorted.length" class="heatmap-section">
        <h2 class="heatmap-title">Difficulty Heatmap</h2>
        <p class="heatmap-subtitle">Each tile is colored by avg GPA. Click any course to explore it.</p>

        <!-- Color scale legend -->
        <div class="legend">
          <span class="legend-label">{{ minGpa.toFixed(2) }} (hardest)</span>
          <div class="legend-bar" />
          <span class="legend-label">{{ maxGpa.toFixed(2) }} (easiest)</span>
        </div>

        <div class="heatmap">
          <RouterLink
            v-for="c in store.rankings.slice().sort((a, b) => a.course.localeCompare(b.course))"
            :key="c.course"
            :to="`/?course=${c.course}`"
            class="heat-cell"
            :style="{ background: gpaColor(c.avg_gpa) }"
          >
            <span class="heat-course">{{ c.course }}</span>
            <span class="heat-gpa">{{ c.avg_gpa ?? '—' }}</span>
          </RouterLink>
        </div>
      </div>

      <div v-else-if="!store.selectedDepartment" class="empty">
        <p>Select a department above to browse courses by difficulty.</p>
      </div>

      <div v-else class="empty">
        <p>No course data available for this department.</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg);
}

.content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 24px;
}

.title {
  font-size: 1.8rem;
  color: var(--primary-text);
  margin: 0 0 4px;
}

.subtitle {
  color: var(--text-muted);
  margin: 0 0 24px;
  font-size: 0.95rem;
}

.dept-select {
  width: 100%;
  max-width: 480px;
  padding: 10px 14px;
  font-size: 1rem;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  background: var(--input-bg);
  color: var(--text);
  cursor: pointer;
  margin-bottom: 28px;
}

.count {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.table-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
  color: var(--text);
}

thead {
  background: var(--bg);
  border-bottom: 2px solid var(--border);
}

th {
  padding: 12px 16px;
  text-align: left;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  white-space: nowrap;
}

th.sortable {
  cursor: pointer;
  user-select: none;
}

th.sortable:hover {
  color: var(--primary-text);
}

td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background: color-mix(in srgb, var(--primary) 4%, var(--surface));
}

.rank-col {
  width: 56px;
  text-align: center;
}

.rank-num {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
}

.course-link {
  color: var(--primary-text);
  font-weight: 600;
  text-decoration: none;
}

.course-link:hover {
  text-decoration: underline;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 14px;
  border-top: 1px solid var(--border);
}

.pagination button {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--text);
  transition: border-color 0.15s;
}

.pagination button:hover:not(:disabled) {
  border-color: var(--primary);
}

.pagination button:disabled {
  opacity: 0.35;
  cursor: default;
}

.page-info {
  font-size: 0.9rem;
  color: var(--text-muted);
  min-width: 120px;
  text-align: center;
}

.status,
.empty {
  text-align: center;
  color: var(--text-muted);
  margin-top: 64px;
  font-size: 1.1rem;
}

.heatmap-section {
  margin-top: 40px;
}

.heatmap-title {
  font-size: 1.3rem;
  color: var(--primary-text);
  margin: 0 0 4px;
}

.heatmap-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin: 0 0 16px;
}

.legend {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.legend-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.legend-bar {
  width: 200px;
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(to right,
    hsl(0, 58%, 36%),
    hsl(60, 58%, 36%),
    hsl(120, 58%, 36%)
  );
}

.heatmap {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}

.heat-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 12px 8px;
  border-radius: 6px;
  text-decoration: none;
  transition: opacity 0.15s, transform 0.1s;
}

.heat-cell:hover {
  opacity: 0.85;
  transform: scale(1.04);
}

.heat-course {
  font-size: 0.82rem;
  font-weight: 700;
  color: white;
  text-align: center;
  line-height: 1.2;
}

.heat-gpa {
  font-size: 1rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
}
</style>
