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
        <!-- Summary stats row -->
        <div class="stats">
          <div class="stat">
            <span class="stat-value">{{ store.selectedInstructor }}</span>
            <span class="stat-label">Professor</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ store.averageGpa }}</span>
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

        <!-- Grade Distribution bar chart -->
        <section class="card">
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
  border: 1px solid #ccc;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.stat {
  flex: 1;
  min-width: 120px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #5c0000;
}

.stat-label {
  font-size: 0.8rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  margin-right: 4px;
}

.course-tag {
  background: #f0e8e8;
  color: #5c0000;
  border: 1px solid #d9c0c0;
  border-radius: 4px;
  padding: 4px 10px;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}

.course-tag:hover {
  background: #e0d0d0;
  border-color: #5c0000;
}

.card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.card h2 {
  margin: 0 0 20px;
  font-size: 1.1rem;
  color: #333;
}

.status {
  text-align: center;
  color: #888;
  margin-top: 48px;
}

.empty {
  text-align: center;
  color: #aaa;
  margin-top: 64px;
  font-size: 1.1rem;
}
</style>
