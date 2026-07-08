<script setup>
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useGradesStore } from '@/stores/grades.js'
import { useMyCoursesStore } from '@/stores/myCourses.js'
import CourseSearch from '@/components/CourseSearch.vue'
import GradeChart from '@/components/GradeChart.vue'
import GpaTrendChart from '@/components/GpaTrendChart.vue'
import SectionsTable from '@/components/SectionsTable.vue'
import ShareButton from '@/components/ShareButton.vue'
import GradePredictor from '@/components/GradePredictor.vue'

const route = useRoute()
const store = useGradesStore()
const myCoursesStore = useMyCoursesStore()

const presetCourse = computed(() => route.query.course || null)
const isSaved = computed(() => store.selectedCourse && myCoursesStore.isSaved(store.selectedCourse))

onMounted(() => {
  store.fetchSemesters()
})
</script>

<template>
  <div class="home">
    <main class="content">
      <!-- Controls -->
      <div class="controls">
        <CourseSearch :preset="presetCourse" />

        <select
          v-if="store.selectedCourse"
          :value="store.selectedSemester"
          @change="store.fetchSections(store.selectedCourse, $event.target.value || null)"
        >
          <option value="">All Semesters</option>
          <option v-for="sem in store.semesters" :key="sem" :value="sem">{{ sem }}</option>
        </select>

        <select
          v-if="store.uniqueInstructors.length"
          :value="store.selectedInstructor"
          @change="store.selectedInstructor = $event.target.value || null"
        >
          <option value="">All Instructors</option>
          <option v-for="inst in store.uniqueInstructors" :key="inst" :value="inst">
            {{ inst }}
          </option>
        </select>
      </div>

      <!-- Loading -->
      <p v-if="store.loading" class="status">Loading...</p>

      <!-- Results -->
      <div v-else-if="store.sections.length" class="results">
        <!-- Stats row + save button -->
        <div class="stats-header">
          <div class="stats">
            <div class="stat">
              <span class="stat-value">{{ store.selectedCourse }}</span>
              <span class="stat-label">Course</span>
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
              <span class="stat-value">{{ store.filteredSections.length }}</span>
              <span class="stat-label">Sections</span>
            </div>
          </div>
          <div class="header-actions">
            <ShareButton />
            <button
              class="save-btn"
              :class="{ saved: isSaved }"
              @click="isSaved ? myCoursesStore.removeCourse(store.selectedCourse) : myCoursesStore.addCourse(store.selectedCourse)"
            >
              {{ isSaved ? '✓ Saved' : '+ Add to My Courses' }}
            </button>
          </div>
        </div>

        <!-- Grade Distribution -->
        <section class="card">
          <h2>Grade Distribution</h2>
          <GradeChart :grade-totals="store.gradeTotals" />
        </section>

        <!-- GPA Trend -->
        <section v-if="store.gpaPerSemesterByInstructor.length > 0" class="card">
          <h2>GPA Trend by Semester</h2>
          <GpaTrendChart
            v-if="store.selectedInstructor"
            :gpa-per-semester="store.gpaPerSemester"
          />
          <GpaTrendChart
            v-else
            :instructor-data="store.gpaPerSemesterByInstructor"
          />
        </section>

        <!-- Sections Table -->
        <section class="card">
          <h2>Section Breakdown</h2>
          <SectionsTable />
        </section>

        <!-- Grade Predictor — only when an instructor is selected -->
        <GradePredictor
          v-if="store.selectedInstructor && store.filteredSections.length"
          :sections="store.filteredSections"
          :course="store.selectedCourse"
          :instructor="store.selectedInstructor"
        />
      </div>

      <!-- No results -->
      <div v-else-if="store.selectedCourse" class="status">
        No data found for {{ store.selectedCourse }}.
      </div>

      <!-- Empty state -->
      <div v-else class="empty">
        <p>Search for a course above to get started.</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home {
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

.stats-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.save-btn {
  align-self: center;
  padding: 10px 18px;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 6px;
  border: 2px solid var(--primary);
  background: var(--surface);
  color: var(--primary-text);
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}

.save-btn:hover {
  background: var(--primary);
  color: white;
}

.save-btn.saved {
  background: var(--primary);
  color: white;
}

.save-btn.saved:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
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
