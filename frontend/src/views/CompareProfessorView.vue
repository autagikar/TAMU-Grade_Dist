<!-- Compare Professors page.
     Mirrors CompareView.vue but compares two professors instead of two courses.
     Each professor's slot also shows their list of taught courses as clickable tags.
     Professor A tags are maroon; Professor B tags are blue. -->

<script setup>
import { onMounted, watch } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useCompareProfessorStore } from '@/stores/compareProfessor.js'
import CompareProfessorSearch from '@/components/CompareProfessorSearch.vue'
import CompareBarChart from '@/components/CompareBarChart.vue'
import CompareTrendChart from '@/components/CompareTrendChart.vue'
import ScoreRing from '@/components/ScoreRing.vue'
import ShareButton from '@/components/ShareButton.vue'

const store = useCompareProfessorStore()
const router = useRouter()
const route = useRoute()

// Pre-fill slots from URL query params on load
onMounted(() => {
  if (route.query.a) store.a.fetch(route.query.a)
  if (route.query.b) store.b.fetch(route.query.b)
})

// Keep URL in sync so the current comparison is always shareable
watch(
  () => [store.a.state.instructor, store.b.state.instructor],
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
      <div v-if="store.a.state.instructor || store.b.state.instructor" class="share-row">
        <ShareButton />
      </div>

      <!-- Two professor search bars with a "vs" divider -->
      <div class="search-row">
        <div class="slot">
          <p class="slot-label">Professor A</p>
          <CompareProfessorSearch placeholder="Search Professor A" @select="store.a.fetch" />
        </div>
        <div class="vs">vs</div>
        <div class="slot">
          <p class="slot-label">Professor B</p>
          <CompareProfessorSearch placeholder="Search Professor B" @select="store.b.fetch" />
        </div>
      </div>

      <!-- Loading indicator -->
      <p v-if="store.a.state.loading || store.b.state.loading" class="status">Loading...</p>

      <!-- Stats panel — shown once at least one slot has data -->
      <div v-if="store.a.state.instructor || store.b.state.instructor" class="stats-row">
        <!-- Professor A stats -->
        <div class="stats-block">
          <h3 class="prof-title">{{ store.a.state.instructor ?? '—' }}</h3>
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
            <div class="stat">
              <span class="stat-value a">{{ store.a.uniqueCourses.length }}</span>
              <span class="stat-label">Courses</span>
            </div>
            <div class="stat">
              <ScoreRing :score="store.a.professorScore" :size="56" />
              <span class="stat-label">Score</span>
            </div>
          </div>
          <!-- Clickable course tags for professor A — links to Course Search -->
          <div v-if="store.a.uniqueCourses.length" class="courses-list">
            <RouterLink
              v-for="course in store.a.uniqueCourses"
              :key="course"
              :to="`/?course=${course}`"
              class="course-tag"
            >{{ course }}</RouterLink>
          </div>
        </div>

        <div class="divider" />

        <!-- Professor B stats -->
        <div class="stats-block">
          <h3 class="prof-title">{{ store.b.state.instructor ?? '—' }}</h3>
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
            <div class="stat">
              <span class="stat-value b">{{ store.b.uniqueCourses.length }}</span>
              <span class="stat-label">Courses</span>
            </div>
            <div class="stat">
              <ScoreRing :score="store.b.professorScore" :size="56" />
              <span class="stat-label">Score</span>
            </div>
          </div>
          <!-- Clickable course tags for professor B — links to Course Search (blue variant) -->
          <div v-if="store.b.uniqueCourses.length" class="courses-list">
            <RouterLink
              v-for="course in store.b.uniqueCourses"
              :key="course"
              :to="`/?course=${course}`"
              class="course-tag b"
            >{{ course }}</RouterLink>
          </div>
        </div>
      </div>

      <!-- Charts — only shown once BOTH slots have data -->
      <template v-if="store.a.state.sections.length > 0 && store.b.state.sections.length > 0">
        <section class="card">
          <h2>Grade Distribution Comparison</h2>
          <!-- courseA/courseB props accept any label string, not just course codes -->
          <CompareBarChart
            :course-a="store.a.state.instructor"
            :course-b="store.b.state.instructor"
            :totals-a="store.a.gradeTotals"
            :totals-b="store.b.gradeTotals"
          />
        </section>

        <section class="card">
          <h2>GPA Trend Comparison</h2>
          <CompareTrendChart
            :course-a="store.a.state.instructor"
            :course-b="store.b.state.instructor"
            :gpa-a="store.a.gpaPerSemester"
            :gpa-b="store.b.gpaPerSemester"
          />
        </section>
      </template>

      <!-- Initial empty state -->
      <div v-else-if="!store.a.state.instructor && !store.b.state.instructor" class="empty">
        <p>Search two professors above to compare them side by side.</p>
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

.prof-title {
  margin: 0 0 12px;
  font-size: 1.1rem;
  color: var(--text);
}

.stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.stat {
  flex: 1;
  min-width: 70px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
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

.courses-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.course-tag {
  background: color-mix(in srgb, var(--primary) 10%, var(--surface));
  color: var(--primary-text);
  border: 1px solid color-mix(in srgb, var(--primary) 25%, var(--border));
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
}

.course-tag:hover {
  border-color: var(--primary-text);
}

.course-tag.b {
  background: color-mix(in srgb, #2196f3 10%, var(--surface));
  color: #1565c0;
  border-color: color-mix(in srgb, #2196f3 30%, var(--border));
}

.course-tag.b:hover {
  border-color: #2196f3;
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
