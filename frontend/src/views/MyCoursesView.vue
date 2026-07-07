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
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="total-row">
                    <td>Overall Average</td>
                    <td class="gpa-cell">{{ store.overallAvgGpa ?? '—' }}</td>
                    <td colspan="7"></td>
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
  background: #f9f9f9;
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
  border: 2px solid #5c0000;
  border-radius: 6px;
  background: white;
  color: #5c0000;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.add-btn:hover {
  background: #5c0000;
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
  background: white;
  border: 1px solid #d9c0c0;
  border-radius: 6px;
  overflow: hidden;
}

.course-name {
  color: #5c0000;
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
  border-left: 1px solid #e8d8d8;
  color: #aaa;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 0.8rem;
  line-height: 1;
  transition: color 0.12s, background 0.12s;
}

.remove-btn:hover {
  color: #5c0000;
  background: #f0e8e8;
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

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

thead tr {
  background: #5c0000;
  color: white;
}

th, td {
  padding: 10px 14px;
  text-align: left;
  white-space: nowrap;
}

tbody tr:nth-child(even) { background: #f9f9f9; }
tbody tr:hover { background: #f0e8e8; }

tfoot .total-row {
  background: #f5f0f0;
  border-top: 2px solid #d9c0c0;
  font-weight: 700;
}

.gpa-cell {
  color: #5c0000;
  font-weight: 600;
}

.course-link {
  color: #5c0000;
  text-decoration: none;
  font-weight: 600;
}

.course-link:hover {
  text-decoration: underline;
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
  line-height: 2;
}

.hint {
  font-size: 0.95rem;
}

.link {
  color: #5c0000;
  font-weight: 600;
}
</style>
