<!-- Professor Lookup page.
     Lets users search for a professor by name and see their aggregate stats,
     a list of courses they've taught (linked to Course Search), a grade distribution
     bar chart, a GPA trend line, and a paginated section breakdown table.

     Deep-linking: navigating to /professor?instructor=J.%20Smith pre-fills the
     search and loads that professor automatically. This is used by the instructor
     links in the SectionsTable on the Course Search page. -->

<script setup>
import { onMounted, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useProfessorStore } from '@/stores/professor.js'
import InstructorSearch from '@/components/InstructorSearch.vue'
import GradeChart from '@/components/GradeChart.vue'
import GpaTrendChart from '@/components/GpaTrendChart.vue'
import ProfessorSectionsTable from '@/components/ProfessorSectionsTable.vue'
import ScoreRing from '@/components/ScoreRing.vue'
import ShareButton from '@/components/ShareButton.vue'

const route = useRoute()
const store = useProfessorStore()


// Read the instructor name from the URL query param (e.g. ?instructor=J.%20Smith).
// InstructorSearch watches this prop and triggers a fetch if it's set on mount.
const presetInstructor = computed(() =>
  route.query.instructor ? decodeURIComponent(route.query.instructor) : null,
)

onMounted(() => {
  // Load the semester list for the filter dropdown on first visit
  store.fetchSemesters()
})
</script>

<template>
  <div class="page">
    <main class="content">
      <!-- Search bar + optional semester filter -->
      <div class="controls">
        <InstructorSearch :preset="presetInstructor" />

        <select
          v-if="store.selectedInstructor"
          :value="store.selectedSemester"
          @change="store.fetchSections(store.selectedInstructor, $event.target.value || null)"
        >
          <option value="">All Semesters</option>
          <option v-for="sem in store.semesters" :key="sem" :value="sem">{{ sem }}</option>
        </select>
      </div>

      <!-- Loading spinner -->
      <p v-if="store.loading" class="status">Loading...</p>

      <!-- Results — shown once sections have been loaded -->
      <div v-else-if="store.sections.length">
        <!-- Share button -->
        <div class="share-row">
          <ShareButton />
        </div>

        <!-- Summary stats row -->
        <div class="stats">
          <div class="stat">
            <span class="stat-value">{{ store.selectedInstructor }}</span>
            <span class="stat-label">Professor</span>
          </div>
          <div class="stat">
            <div class="gpa-with-trend">
              <span class="stat-value">
                <span v-if="store.isSUOnly" class="su-label">S/U</span>
                <template v-else>{{ store.averageGpa ?? '—' }}</template>
              </span>
              <span
                v-if="store.gpaTrend"
                class="trend-arrow"
                :class="store.gpaTrend.direction"
                :title="store.gpaTrend.delta ? `${store.gpaTrend.delta} vs last semester` : 'No significant change'"
              >{{ store.gpaTrend.label }}</span>
            </div>
            <span v-if="store.gpaTrend?.delta" class="trend-delta" :class="store.gpaTrend.direction">
              {{ store.gpaTrend.delta }} vs last sem
            </span>
            <span class="stat-label">Avg GPA</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ store.totalStudents.toLocaleString() }}</span>
            <span class="stat-label">Total Students</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ store.sections.length }}</span>
            <span class="stat-label">Sections Taught</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ store.uniqueCourses.length }}</span>
            <span class="stat-label">Unique Courses</span>
          </div>
          <div class="stat score-stat">
            <ScoreRing :score="store.professorScore" />
            <span class="stat-label">Estimated Professor Score</span>
          </div>
        </div>

        <!-- Courses this professor has taught, each linking to Course Search -->
        <div class="courses-list">
          <span class="courses-label">Courses:</span>
          <RouterLink
            v-for="course in store.uniqueCourses"
            :key="course"
            :to="`/?course=${course}`"
            class="course-tag"
          >{{ course }}</RouterLink>
        </div>

        <!-- S/U notice banner -->
        <div v-if="store.isSUOnly" class="su-notice">
          All sections taught by this professor use <strong>Satisfactory / Unsatisfactory</strong> grading — no letter grades or GPA are recorded.
        </div>

        <!-- Grade Distribution bar chart -->
        <section v-if="!store.isSUOnly" class="card">
          <h2>Grade Distribution</h2>
          <GradeChart :grade-totals="store.gradeTotals" />
        </section>

        <!-- GPA Trend line chart �� only shown when there are at least 2 data points -->
        <section v-if="store.gpaPerSemester.length > 1" class="card">
          <h2>GPA Trend by Semester</h2>
          <GpaTrendChart :gpa-per-semester="store.gpaPerSemester" />
        </section>

        <!-- Paginated section breakdown table -->
        <section class="card">
          <h2>Section Breakdown</h2>
          <ProfessorSectionsTable />
        </section>

        <!-- Similar professors from the same department -->
        <section v-if="store.similarProfessors.length" class="card">
          <h2>Similar Professors</h2>
          <div class="similar-grid">
            <RouterLink
              v-for="prof in store.similarProfessors"
              :key="prof.instructor"
              :to="`/professor?instructor=${encodeURIComponent(prof.instructor)}`"
              class="similar-card"
            >
              <ScoreRing :score="prof.score" :size="56" />
              <div class="similar-info">
                <span class="similar-name">{{ prof.instructor }}</span>
                <span class="similar-gpa">GPA {{ prof.avg_gpa }}</span>
              </div>
            </RouterLink>
          </div>
        </section>
      </div>

      <!-- Shown when a search was run but returned no results -->
      <div v-else-if="store.selectedInstructor" class="status">
        No data found for {{ store.selectedInstructor }}.
      </div>

      <!-- Initial empty state before any search -->
      <div v-else class="empty">
        <p>Search for a professor above to get started.</p>
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
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px;
}

.controls {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  flex-wrap: wrap;
  margin-bottom: 32px;
}

select {
  padding: 10px 14px;
  font-size: 1rem;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  background: var(--input-bg);
  color: var(--text);
  cursor: pointer;
}

.share-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.stat {
  flex: 1;
  min-width: 100px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--primary-text);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: auto;
}

.gpa-with-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
}

.trend-arrow {
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1;
}

.trend-arrow.up   { color: #2e7d32; }
.trend-arrow.down { color: #c62828; }
.trend-arrow.flat { color: #888; }

.trend-delta {
  font-size: 0.78rem;
  font-weight: 600;
}

.trend-delta.up   { color: #2e7d32; }
.trend-delta.down { color: #c62828; }
.trend-delta.flat { color: #888; }

.similar-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.similar-card {
  flex: 1;
  min-width: 180px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  text-decoration: none;
  background: var(--surface);
  transition: background 0.15s, border-color 0.15s;
}

.similar-card:hover {
  border-color: var(--primary-text);
}

.similar-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.similar-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--primary-text);
}

.similar-gpa {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.courses-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
  align-items: center;
}

.courses-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  margin-right: 4px;
}

.course-tag {
  background: color-mix(in srgb, var(--primary) 10%, var(--surface));
  color: var(--primary-text);
  border: 1px solid color-mix(in srgb, var(--primary) 25%, var(--border));
  border-radius: 4px;
  padding: 4px 10px;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}

.course-tag:hover {
  border-color: var(--primary-text);
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

.su-label {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-muted);
}

.su-notice {
  background: color-mix(in srgb, var(--text-muted) 10%, var(--surface));
  border: 1px solid var(--border);
  border-left: 4px solid var(--text-muted);
  border-radius: 6px;
  padding: 14px 18px;
  margin-bottom: 24px;
  font-size: 0.92rem;
  color: var(--text-muted);
}
</style>
