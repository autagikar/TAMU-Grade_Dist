// Pinia store for the Professor Lookup page.
// Manages fetching all sections taught by a specific instructor and computing
// summary statistics used by the professor page (avg GPA, unique courses, trend).

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getSections, getSemesters } from '@/api/index.js'

// Converts a semester string like "Spring 2024" into a numeric sort key
// so semesters can be sorted chronologically (older = smaller number).
function semesterSortKey(sem) {
  const [term, year] = sem.split(' ')
  const termOrder = { Spring: 1, Summer: 2, Fall: 3 }
  return parseInt(year) * 10 + (termOrder[term] ?? 0)
}

export const useProfessorStore = defineStore('professor', () => {
  // --- state ---
  const selectedInstructor = ref(null)  // currently displayed instructor name
  const selectedSemester = ref(null)    // optional semester filter
  const sections = ref([])              // all section rows for this instructor
  const semesters = ref([])             // all semesters in the DB (for dropdown)
  const loading = ref(false)

  // --- actions ---

  // Fetches all available semesters from the API and sorts them newest-first
  // for the dropdown (e.g. Fall 2026 at the top).
  async function fetchSemesters() {
    const res = await getSemesters()
    semesters.value = res.data.sort((a, b) => semesterSortKey(b) - semesterSortKey(a))
  }

  // Fetches all sections for the given instructor (optionally filtered by semester).
  // Passing null for course tells getSections to filter by instructor only.
  async function fetchSections(instructor, semester = null) {
    loading.value = true
    selectedInstructor.value = instructor
    selectedSemester.value = semester
    const res = await getSections(null, semester, instructor)
    sections.value = res.data
    loading.value = false
  }

  function clearSections() {
    sections.value = []
    selectedInstructor.value = null
    selectedSemester.value = null
  }

  // --- computed ---

  // Aggregate A/B/C/D/F counts across all sections for the grade distribution chart.
  const gradeTotals = computed(() => {
    const totals = { a: 0, b: 0, c: 0, d: 0, f: 0 }
    for (const s of sections.value) {
      totals.a += s.a
      totals.b += s.b
      totals.c += s.c
      totals.d += s.d
      totals.f += s.f
    }
    return totals
  })

  // Weighted average GPA: each section's GPA is weighted by the number of graded
  // students (a_to_f) so larger sections have more influence on the average.
  const averageGpa = computed(() => {
    const valid = sections.value.filter((s) => s.gpa !== null && s.a_to_f > 0)
    if (!valid.length) return null
    const weighted = valid.reduce((sum, s) => sum + s.gpa * s.a_to_f, 0)
    const total = valid.reduce((sum, s) => sum + s.a_to_f, 0)
    return (weighted / total).toFixed(3)
  })

  // Total students enrolled across all sections (including non-graded like Q/W).
  const totalStudents = computed(() => sections.value.reduce((sum, s) => sum + s.total, 0))

  // All unique course codes this professor has ever taught (sorted alphabetically),
  // displayed as clickable links on the professor page.
  const uniqueCourses = computed(() => {
    const set = new Set(sections.value.map((s) => s.course))
    return [...set].sort()
  })

  // Average GPA per semester — used for the single-line GPA trend chart on the
  // professor page. Semesters are sorted oldest → newest so the line reads left to right.
  const gpaPerSemester = computed(() => {
    const map = {}
    for (const s of sections.value) {
      if (s.gpa === null || s.a_to_f === 0) continue
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

  return {
    selectedInstructor,
    selectedSemester,
    sections,
    semesters,
    loading,
    gradeTotals,
    averageGpa,
    totalStudents,
    uniqueCourses,
    gpaPerSemester,
    fetchSemesters,
    fetchSections,
    clearSections,
  }
})
