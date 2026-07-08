<!-- Compare Courses page.
     Two side-by-side search bars let the user pick two courses.
     Once both are loaded, the page shows:
       - A stats panel with avg GPA, students, and sections for each course
       - A grouped bar chart comparing A/B/C/D/F distributions
       - An overlapping GPA trend line chart
     Slot A is colored maroon, Slot B is colored blue throughout. -->

<script setup>
import { onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCompareStore } from '@/stores/compare.js'
import CompareSearch from '@/components/CompareSearch.vue'
import CompareBarChart from '@/components/CompareBarChart.vue'
import CompareTrendChart from '@/components/CompareTrendChart.vue'
import ShareButton from '@/components/ShareButton.vue'

const store = useCompareStore()
const router = useRouter()
const route = useRoute()

// Pre-fill slots from URL query params on load
onMounted(() => {
  if (route.query.a) store.a.fetch(route.query.a)
  if (route.query.b) store.b.fetch(route.query.b)
})

// Keep URL in sync as selections change so links are shareable
watch(
  () => [store.a.state.course, store.b.state.course],
  ([a, b]) => {
    const query = {}
    if (a) query.a = a
    if (b) query.b = b
    router.replace({ query: Object.keys(query).length ? query : undefined })
  },
)
</script>

<template>
  <div class="compare">
    <main class="content">
      <!-- Share button for the current comparison -->
      <div v-if="store.a.state.course || store.b.state.course" class="share-row">
        <ShareButton />
      </div>

      <!-- Two search bars with a "vs" divider between them -->
      <div class="search-row">
        <div class="slot">
          <p class="slot-label">Course A</p>
          <!-- @select fires when the user picks a course from the autocomplete -->
          <CompareSearch placeholder="Search Course A" @select="store.a.fetch" />
        </div>
        <div class="vs">vs</div>
        <div class="slot">
          <p class="slot-label">Course B</p>
          <CompareSearch placeholder="Search Course B" @select="store.b.fetch" />
        </div>
      </div>

      <!-- Loading indicator while either slot is fetching -->
      <p v-if="store.a.state.loading || store.b.state.loading" class="status">Loading...</p>

      <!-- Stats panel — shown as soon as either slot has a course name,
           even if the other is still empty -->
      <div v-if="store.a.state.course || store.b.state.course" class="stats-row">
        <!-- Course A stats -->
        <div class="stats-block">
          <h3 class="course-title">{{ store.a.state.course ?? '—' }}</h3>
          <div class="stats">
            <div class="stat">
              <span class="stat-value a">{{ store.a.averageGpa ?? '—' }}</span>
              <span class="stat-label">Avg GPA</span>
            </div>
            <div class="stat">
              <span class="stat-value a">{{ store.a.totalStudents.toLocaleString() }}</span>
              <span class="stat-label">Students</span>
            </div>
            <div class="stat">
              <span class="stat-value a">{{ store.a.state.sections.length }}</span>
              <span class="stat-label">Sections</span>
            </div>
          </div>
        </div>

        <div class="divider" />

        <!-- Course B stats -->
        <div class="stats-block">
          <h3 class="course-title">{{ store.b.state.course ?? '—' }}</h3>
          <div class="stats">
            <div class="stat">
              <span class="stat-value b">{{ store.b.averageGpa ?? '—' }}</span>
              <span class="stat-label">Avg GPA</span>
            </div>
            <div class="stat">
              <span class="stat-value b">{{ store.b.totalStudents.toLocaleString() }}</span>
              <span class="stat-label">Students</span>
            </div>
            <div class="stat">
              <span class="stat-value b">{{ store.b.state.sections.length }}</span>
              <span class="stat-label">Sections</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts — only render when BOTH slots have data loaded -->
      <template v-if="store.a.state.sections.length > 0 && store.b.state.sections.length > 0">
        <section class="card">
          <h2>Grade Distribution Comparison</h2>
          <CompareBarChart
            :course-a="store.a.state.course"
            :course-b="store.b.state.course"
            :totals-a="store.a.gradeTotals"
            :totals-b="store.b.gradeTotals"
          />
        </section>

        <section class="card">
          <h2>GPA Trend Comparison</h2>
          <CompareTrendChart
            :course-a="store.a.state.course"
            :course-b="store.b.state.course"
            :gpa-a="store.a.gpaPerSemester"
            :gpa-b="store.b.gpaPerSemester"
          />
        </section>
      </template>

      <!-- Initial empty state -->
      <div v-else-if="!store.a.state.course && !store.b.state.course" class="empty">
        <p>Search two courses above to compare them side by side.</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.compare {
  min-height: 100vh;
  background: var(--bg);
}

.content {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 24px;
}

.share-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.search-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 32px;
}

.slot {
  flex: 1;
}

.slot-label {
  margin: 0 0 6px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.vs {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-muted);
  padding-bottom: 10px;
  flex-shrink: 0;
}

.stats-row {
  display: flex;
  gap: 0;
  margin-bottom: 28px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.stats-block {
  flex: 1;
  padding: 20px 24px;
}

.divider {
  width: 1px;
  background: var(--border);
}

.course-title {
  margin: 0 0 12px;
  font-size: 1.1rem;
  color: var(--text);
}

.stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat {
  flex: 1;
  min-width: 80px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
}

.stat-value.a { color: var(--primary-text); }
.stat-value.b { color: #2196f3; }

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.card h2 {
  margin: 0 0 20px;
  font-size: 1.1rem;
  color: var(--text);
}

.status {
  text-align: center;
  color: var(--text-muted);
  margin-top: 48px;
}

.empty {
  text-align: center;
  color: var(--text-muted);
  margin-top: 64px;
  font-size: 1.1rem;
}
</style>
