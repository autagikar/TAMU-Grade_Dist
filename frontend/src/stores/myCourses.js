import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getSections } from '@/api/index.js'

const STORAGE_KEY = 'tamu_my_courses'

function semesterSortKey(sem) {
  const [term, year] = sem.split(' ')
  const termOrder = { Spring: 1, Summer: 2, Fall: 3 }
  return parseInt(year) * 10 + (termOrder[term] ?? 0)
}

export const useMyCoursesStore = defineStore('myCourses', () => {
  // Ordered list of course names, persisted to localStorage
  const courses = ref(JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]'))

  // Map of course name → { sections, loading }
  const courseData = ref({})

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(courses.value))
  }

  function isSaved(course) {
    return courses.value.includes(course)
  }

  async function addCourse(course) {
    if (isSaved(course)) return
    courses.value.push(course)
    persist()
    await loadCourse(course)
  }

  function removeCourse(course) {
    courses.value = courses.value.filter((c) => c !== course)
    delete courseData.value[course]
    persist()
  }

  async function loadCourse(course) {
    if (courseData.value[course]) return
    courseData.value[course] = { sections: [], loading: true }
    const res = await getSections(course)
    courseData.value[course] = { sections: res.data, loading: false }
  }

  // On store init, hydrate data for any courses already in localStorage
  async function hydrate() {
    for (const course of courses.value) {
      await loadCourse(course)
    }
  }

  // One GPA-per-semester series per course — used for the multi-line chart
  const gpaSeriesByCourse = computed(() => {
    return courses.value
      .filter((c) => courseData.value[c] && !courseData.value[c].loading)
      .map((course) => {
        const sections = courseData.value[course].sections
        const map = {}
        for (const s of sections) {
          if (s.gpa === null || s.a_to_f === 0) continue
          if (!map[s.semester]) map[s.semester] = { weightedSum: 0, total: 0 }
          map[s.semester].weightedSum += s.gpa * s.a_to_f
          map[s.semester].total += s.a_to_f
        }
        const data = Object.entries(map)
          .map(([semester, d]) => ({ semester, avgGpa: parseFloat((d.weightedSum / d.total).toFixed(3)) }))
          .sort((a, b) => semesterSortKey(a.semester) - semesterSortKey(b.semester))
        return { course, data }
      })
  })

  const isLoading = computed(() =>
    Object.values(courseData.value).some((d) => d.loading),
  )

  // Per-course summary stats for the table
  const courseStats = computed(() => {
    return courses.value
      .filter((c) => courseData.value[c] && !courseData.value[c].loading)
      .map((course) => {
        const sections = courseData.value[course].sections
        const valid = sections.filter((s) => s.gpa !== null && s.a_to_f > 0)
        const weightedGpa = valid.length
          ? valid.reduce((sum, s) => sum + s.gpa * s.a_to_f, 0) / valid.reduce((sum, s) => sum + s.a_to_f, 0)
          : null
        const totalStudents = sections.reduce((sum, s) => sum + s.total, 0)
        const grades = sections.reduce(
          (acc, s) => { acc.a += s.a; acc.b += s.b; acc.c += s.c; acc.d += s.d; acc.f += s.f; return acc },
          { a: 0, b: 0, c: 0, d: 0, f: 0 },
        )
        const gradedTotal = grades.a + grades.b + grades.c + grades.d + grades.f
        return {
          course,
          avgGpa: weightedGpa !== null ? +weightedGpa.toFixed(3) : null,
          totalStudents,
          sections: sections.length,
          aPercent: gradedTotal ? +((grades.a / gradedTotal) * 100).toFixed(1) : null,
          bPercent: gradedTotal ? +((grades.b / gradedTotal) * 100).toFixed(1) : null,
          cPercent: gradedTotal ? +((grades.c / gradedTotal) * 100).toFixed(1) : null,
          dPercent: gradedTotal ? +((grades.d / gradedTotal) * 100).toFixed(1) : null,
          fPercent: gradedTotal ? +((grades.f / gradedTotal) * 100).toFixed(1) : null,
        }
      })
  })

  // Overall average GPA across all saved courses (weighted by students)
  const overallAvgGpa = computed(() => {
    let weightedSum = 0
    let totalStudents = 0
    for (const c of courses.value) {
      const data = courseData.value[c]
      if (!data || data.loading) continue
      for (const s of data.sections) {
        if (s.gpa === null || s.a_to_f === 0) continue
        weightedSum += s.gpa * s.a_to_f
        totalStudents += s.a_to_f
      }
    }
    return totalStudents ? +(weightedSum / totalStudents).toFixed(3) : null
  })

  return { courses, courseData, isSaved, addCourse, removeCourse, hydrate, gpaSeriesByCourse, courseStats, overallAvgGpa, isLoading }
})
