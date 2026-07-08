<!-- Department Rankings page.
     User picks a department from a dropdown and sees every professor in that
     department ranked by their professor score. Columns are sortable by clicking
     their header. Professor names link to the Professor Lookup page. -->

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useRankingsStore } from '@/stores/rankings.js'
import ScoreRing from '@/components/ScoreRing.vue'

const store = useRankingsStore()

const sortKey = ref('score')
const sortDir = ref('desc')

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
    sortDir.value = 'desc'
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

// Medal color for top 3 rows — only applied on page 1
function rankColor(pageIndex) {
  if (currentPage.value !== 1) return '#9e9e9e'
  return ['#f5c400', '#9e9e9e', '#cd7f32'][pageIndex] ?? '#9e9e9e'
}

// Dynamic color scale based on actual score range in this department
const minScore = computed(() => {
  const vals = store.rankings.map(p => p.score).filter(v => v != null)
  return vals.length ? Math.min(...vals) : 0
})

const maxScore = computed(() => {
  const vals = store.rankings.map(p => p.score).filter(v => v != null)
  return vals.length ? Math.max(...vals) : 100
})

function scoreColor(score) {
  if (score == null) return 'var(--border)'
  const range = maxScore.value - minScore.value
  const hue = range === 0 ? 60 : ((score - minScore.value) / range) * 120
  return `hsl(${hue}, 58%, 36%)`
}
</script>

<template>
  <div class="page">
    <main class="content">
      <h1 class="title">Department Rankings</h1>
      <p class="subtitle">Professors ranked by estimated score within a department.</p>

      <!-- Department picker -->
      <select class="dept-select" @change="pickDepartment">
        <option value="">Select a department…</option>
        <option v-for="dept in store.departments" :key="dept" :value="dept">
          {{ dept }}
        </option>
      </select>

      <p v-if="store.loading" class="status">Loading...</p>

      <!-- Rankings table -->
      <template v-else-if="sorted.length">
      <p class="count">{{ sorted.length }} professors in <strong>{{ store.selectedDepartment }}</strong></p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th class="rank-col">Rank</th>
              <th>Professor</th>
              <th class="sortable" @click="setSort('score')">Score{{ arrow('score') }}</th>
              <th class="sortable" @click="setSort('avg_gpa')">Avg GPA{{ arrow('avg_gpa') }}</th>
              <th class="sortable" @click="setSort('a_percent')">A%{{ arrow('a_percent') }}</th>
              <th class="sortable" @click="setSort('total_students')">Students{{ arrow('total_students') }}</th>
              <th class="sortable" @click="setSort('sections_count')">Sections{{ arrow('sections_count') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(prof, i) in paginated" :key="prof.instructor">
              <td class="rank-col">
                <span class="rank-badge" :style="{ background: rankColor(i) }">
                  {{ startIndex + i + 1 }}
                </span>
              </td>
              <td>
                <RouterLink
                  :to="`/professor?instructor=${encodeURIComponent(prof.instructor)}`"
                  class="prof-link"
                >{{ prof.instructor }}</RouterLink>
              </td>
              <td>
                <div class="ring-cell">
                  <ScoreRing :score="prof.score" :size="48" />
                </div>
              </td>
              <td>{{ prof.avg_gpa ?? '—' }}</td>
              <td>{{ prof.a_percent }}%</td>
              <td>{{ prof.total_students.toLocaleString() }}</td>
              <td>{{ prof.sections_count }}</td>
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

      <!-- Professor heatmap -->
      <div v-if="sorted.length" class="heatmap-section">
        <h2 class="heatmap-title">Professor Heatmap</h2>
        <p class="heatmap-subtitle">Each tile is colored by professor score. Click any name to view their profile.</p>

        <div class="legend">
          <span class="legend-label">{{ minScore }} (lowest)</span>
          <div class="legend-bar" />
          <span class="legend-label">{{ maxScore }} (highest)</span>
        </div>

        <div class="heatmap">
          <RouterLink
            v-for="prof in store.rankings.slice().sort((a, b) => a.instructor.localeCompare(b.instructor))"
            :key="prof.instructor"
            :to="`/professor?instructor=${encodeURIComponent(prof.instructor)}`"
            class="heat-cell"
            :style="{ background: scoreColor(prof.score) }"
          >
            <span class="heat-name">{{ prof.instructor }}</span>
            <span class="heat-score">{{ prof.score ?? '—' }}</span>
          </RouterLink>
        </div>
      </div>

      <!-- Empty state before a department is chosen -->
      <div v-else-if="!store.selectedDepartment" class="empty">
        <p>Select a department above to see professor rankings.</p>
      </div>

      <!-- No results for chosen department -->
      <div v-else class="empty">
        <p>No ranking data available for this department.</p>
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
  max-width: 960px;
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

thead tr {
  background: var(--primary);
  color: white;
}

th {
  padding: 12px 16px;
  text-align: left;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

th.sortable {
  cursor: pointer;
  user-select: none;
}

th.sortable:hover {
  opacity: 0.8;
}

tbody tr {
  background: var(--surface);
}

tbody tr:nth-child(even) {
  background: var(--bg);
}

td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

tr:last-child td {
  border-bottom: none;
}

tbody tr:hover td {
  background: color-mix(in srgb, var(--primary) 6%, var(--surface));
}

.rank-col {
  width: 60px;
  text-align: center;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 0.78rem;
  font-weight: 700;
  color: white;
}

.prof-link {
  color: var(--primary-text);
  font-weight: 600;
  text-decoration: none;
}

.prof-link:hover {
  text-decoration: underline;
}

.ring-cell {
  display: flex;
  align-items: center;
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
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
}

.heat-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 12px 10px;
  border-radius: 6px;
  text-decoration: none;
  transition: opacity 0.15s, transform 0.1s;
}

.heat-cell:hover {
  opacity: 0.85;
  transform: scale(1.04);
}

.heat-name {
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
  text-align: center;
  line-height: 1.3;
  word-break: break-word;
}

.heat-score {
  font-size: 1rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
}

.status,
.empty {
  text-align: center;
  color: var(--text-muted);
  margin-top: 64px;
  font-size: 1.1rem;
}
</style>
