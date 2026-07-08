<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useMyCoursesStore } from '@/stores/myCourses.js'
import MyCoursesChart from '@/components/MyCoursesChart.vue'

const store = useMyCoursesStore()

onMounted(() => store.hydrate())
</script>

<template>
  <div class="page">
    <main class="content">
      <!-- Header -->
      <div class="page-header">
        <RouterLink to="/" class="add-btn">+ Add Course</RouterLink>
      </div>

      <!-- Empty state -->
      <div v-if="store.courses.length === 0" class="empty">
        <p>No courses saved yet.</p>
        <p class="hint">Click <strong>+ Add Course</strong> above to get started.</p>
      </div>

      <template v-else>
        <!-- Course chips -->
        <div class="course-list">
          <div v-for="course in store.courses" :key="course" class="course-chip">
            <RouterLink :to="`/?course=${course}`" class="course-name">{{ course }}</RouterLink>
            <button class="remove-btn" @click="store.removeCourse(course)">✕</button>
          </div>
        </div>

        <!-- Loading -->
        <p v-if="store.isLoading" class="status">Loading course data...</p>

        <template v-else-if="store.gpaSeriesByCourse.length > 0">
          <!-- GPA Trend Chart -->
          <section class="card">
            <h2>Average GPA by Semester</h2>
            <MyCoursesChart :series="store.gpaSeriesByCourse" />
          </section>

          <!-- Course Stats Table -->
          <section class="card">
            <h2>Course Summary</h2>
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Course</th>
                    <th>Avg GPA</th>
                    <th>Students</th>
                    <th>Sections</th>
                    <th>A%</th>
                    <th>B%</th>
                    <th>C%</th>
                    <th>D%</th>
                    <th>F%</th>
                    <th>Q-Drop%</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in store.courseStats" :key="row.course">
                    <td>
                      <RouterLink :to="`/?course=${row.course}`" class="course-link">
                        {{ row.course }}
                      </RouterLink>
                    </td>
                    <td class="gpa-cell">{{ row.avgGpa ?? '—' }}</td>
                    <td>{{ row.totalStudents.toLocaleString() }}</td>
                    <td>{{ row.sections }}</td>
                    <td>{{ row.aPercent !== null ? row.aPercent + '%' : '—' }}</td>
                    <td>{{ row.bPercent !== null ? row.bPercent + '%' : '—' }}</td>
                    <td>{{ row.cPercent !== null ? row.cPercent + '%' : '—' }}</td>
                    <td>{{ row.dPercent !== null ? row.dPercent + '%' : '—' }}</td>
                    <td>{{ row.fPercent !== null ? row.fPercent + '%' : '—' }}</td>
                    <td>{{ row.qPercent !== null ? row.qPercent + '%' : '—' }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="total-row">
                    <td>Overall Average</td>
                    <td class="gpa-cell">{{ store.overallAvgGpa ?? '—' }}</td>
                    <td colspan="8"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </section>
        </template>
      </template>
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

.page-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.add-btn {
  display: inline-block;
  padding: 10px 18px;
  font-size: 0.9rem;
  font-weight: 600;
  border: 2px solid var(--primary);
  border-radius: 6px;
  background: var(--surface);
  color: var(--primary-text);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.add-btn:hover {
  background: var(--primary);
  color: white;
}

.course-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 28px;
}

.course-chip {
  display: flex;
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}

.course-name {
  color: var(--primary-text);
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  padding: 7px 12px;
}

.course-name:hover {
  text-decoration: underline;
}

.remove-btn {
  background: none;
  border: none;
  border-left: 1px solid var(--border);
  color: var(--text-muted);
  padding: 7px 10px;
  cursor: pointer;
  font-size: 0.8rem;
  line-height: 1;
  transition: color 0.12s, background 0.12s;
}

.remove-btn:hover {
  color: var(--primary-text);
  background: color-mix(in srgb, var(--primary) 8%, var(--surface));
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
  padding: 10px 14px;
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

tfoot .total-row {
  background: color-mix(in srgb, var(--primary) 6%, var(--surface));
  border-top: 2px solid var(--border);
  font-weight: 700;
}

.gpa-cell {
  color: var(--primary-text);
  font-weight: 600;
}

.course-link {
  color: var(--primary-text);
  text-decoration: none;
  font-weight: 600;
}

.course-link:hover {
  text-decoration: underline;
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
  line-height: 2;
}

.hint {
  font-size: 0.95rem;
}

.link {
  color: var(--primary-text);
  font-weight: 600;
}
</style>
