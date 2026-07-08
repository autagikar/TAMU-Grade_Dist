import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getSections, getSemesters } from '@/api/index.js'

function semesterSortKey(sem) {
  // Converts "Spring 2024" → a number so semesters sort chronologically
  const [term, year] = sem.split(' ')
  const termOrder = { Spring: 1, Summer: 2, Fall: 3 }
  return parseInt(year) * 10 + (termOrder[term] ?? 0)
}

export const useGradesStore = defineStore('grades', () => {
  // --- state ---
  const selectedCourse = ref(null)
  const selectedSemester = ref(null)
  const selectedInstructor = ref(null)
  const sections = ref([])
  const semesters = ref([])
  const loading = ref(false)

  // --- actions ---
  async function fetchSemesters() {
    const res = await getSemesters()
    semesters.value = res.data.sort((a, b) => semesterSortKey(b) - semesterSortKey(a))
  }

  async function fetchSections(course, semester = null) {
    loading.value = true
    selectedCourse.value = course
    selectedSemester.value = semester
    selectedInstructor.value = null
    const res = await getSections(course, semester)
    sections.value = res.data
    loading.value = false
  }

  function clearSections() {
    sections.value = []
    selectedCourse.value = null
    selectedSemester.value = null
    selectedInstructor.value = null
  }

  // --- computed ---

  // All sections filtered by instructor selection
  const filteredSections = computed(() => {
    if (!selectedInstructor.value) return sections.value
    return sections.value.filter((s) => s.instructor === selectedInstructor.value)
  })

  // Sorted list of unique instructors for the current course
  const uniqueInstructors = computed(() => {
    const set = new Set(sections.value.map((s) => s.instructor).filter(Boolean))
    return [...set].sort()
  })

  // Aggregate grade counts from filtered sections
  const gradeTotals = computed(() => {
    const totals = { a: 0, b: 0, c: 0, d: 0, f: 0 }
    for (const s of filteredSections.value) {
      totals.a += s.a
      totals.b += s.b
      totals.c += s.c
      totals.d += s.d
      totals.f += s.f
    }
    return totals
  })

  // Weighted average GPA from filtered sections
  const averageGpa = computed(() => {
    const valid = filteredSections.value.filter((s) => s.gpa !== null && s.gpa > 0 && s.a_to_f > 0)
    if (!valid.length) return null
    const weighted = valid.reduce((sum, s) => sum + s.gpa * s.a_to_f, 0)
    const total = valid.reduce((sum, s) => sum + s.a_to_f, 0)
    return (weighted / total).toFixed(3)
  })

  // Total enrolled students from filtered sections
  const totalStudents = computed(() =>
    filteredSections.value.reduce((sum, s) => sum + s.total, 0),
  )

  // Average GPA per semester — always uses all sections (not instructor-filtered)
  // so the trend line reflects the full course history
  const gpaPerSemester = computed(() => {
    const map = {}
    for (const s of sections.value) {
      if (s.gpa === null || s.gpa === 0 || s.a_to_f === 0) continue
      if (!map[s.semester]) map[s.semester] = { weightedSum: 0, total: 0 }
      map[s.semester].weightedSum += s.gpa * s.a_to_f
      map[s.semester].total += s.a_to_f
    }
    return Object.entries(map)
      .map(([semester, data]) => ({
        semester,
        avgGpa: (data.weightedSum / data.total).toFixed(3),
      }))
      .sort((a, b) => semesterSortKey(a.semester) - semesterSortKey(b.semester))
  })

  // GPA trend broken down per instructor — one entry per instructor with their
  // own semester-by-semester average GPA array
  const gpaPerSemesterByInstructor = computed(() => {
    const instructorMap = {}
    for (const s of sections.value) {
      if (s.gpa === null || s.gpa === 0 || s.a_to_f === 0 || !s.instructor) continue
      if (!instructorMap[s.instructor]) instructorMap[s.instructor] = {}
      if (!instructorMap[s.instructor][s.semester])
        instructorMap[s.instructor][s.semester] = { weightedSum: 0, total: 0 }
      instructorMap[s.instructor][s.semester].weightedSum += s.gpa * s.a_to_f
      instructorMap[s.instructor][s.semester].total += s.a_to_f
    }
    return Object.entries(instructorMap)
      .map(([instructor, semData]) => ({
        instructor,
        data: Object.entries(semData)
          .map(([semester, d]) => ({
            semester,
            avgGpa: (d.weightedSum / d.total).toFixed(3),
          }))
          .sort((a, b) => semesterSortKey(a.semester) - semesterSortKey(b.semester)),
      }))
      .sort((a, b) => a.instructor.localeCompare(b.instructor))
  })

  // True when every section for this course has gpa=0 (S/U grading — no letter grades recorded)
  const isSUCourse = computed(() =>
    sections.value.length > 0 && sections.value.every((s) => s.gpa === 0),
  )

  // Course difficulty score 0–100: inverse of the professor score formula.
  // High difficulty = low GPA + high F%. Uses all sections (not instructor-filtered)
  // so the score reflects the course as a whole, not one instructor's sections.
  const courseDifficulty = computed(() => {
    const valid = sections.value.filter((s) => s.gpa !== null && s.gpa > 0 && s.a_to_f > 0)
    if (!valid.length) return null
    const totalGraded = valid.reduce((sum, s) => sum + s.a_to_f, 0)
    const weightedGpa = valid.reduce((sum, s) => sum + s.gpa * s.a_to_f, 0)
    const totalF = valid.reduce((sum, s) => sum + s.f, 0)
    const avgGpa = weightedGpa / totalGraded
    const fPercent = totalF / totalGraded
    return Math.min(100, Math.round((1 - avgGpa / 4.0) * 70 + fPercent * 30))
  })

  return {
    selectedCourse,
    selectedSemester,
    selectedInstructor,
    sections,
    semesters,
    loading,
    filteredSections,
    uniqueInstructors,
    gradeTotals,
    averageGpa,
    totalStudents,
    isSUCourse,
    courseDifficulty,
    gpaPerSemester,
    gpaPerSemesterByInstructor,
    fetchSemesters,
    fetchSections,
    clearSections,
  }
})
