// Pinia store for the Professor Lookup page.
// Manages fetching all sections taught by a specific instructor and computing
// summary statistics used by the professor page (avg GPA, unique courses, trend).

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getSections, getSemesters, getDepartmentRankings } from '@/api/index.js'

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
  const similarProfessors = ref([])     // up to 3 professors from the same dept with similar scores

  // --- actions ---

  // Fetches all available semesters from the API and sorts them newest-first
  // for the dropdown (e.g. Fall 2026 at the top).
  async function fetchSemesters() {
    const res = await getSemesters()
    semesters.value = res.data.sort((a, b) => semesterSortKey(b) - semesterSortKey(a))
  }

  // Fetches all sections for the given instructor (optionally filtered by semester).
  // After sections load, kicks off a background fetch for similar professors.
  async function fetchSections(instructor, semester = null) {
    loading.value = true
    selectedInstructor.value = instructor
    selectedSemester.value = semester
    similarProfessors.value = []
    const res = await getSections(null, semester, instructor)
    sections.value = res.data
    loading.value = false
    // Fetch similar professors in the background (don't block the main load)
    fetchSimilarProfessors()
  }

  // Finds up to 3 professors in the same department with the closest professor score.
  async function fetchSimilarProfessors() {
    const department = sections.value[0]?.department
    if (!department || professorScore.value === null) return
    try {
      const res = await getDepartmentRankings(department)
      const currentScore = professorScore.value
      similarProfessors.value = res.data
        .filter((p) => p.instructor !== selectedInstructor.value && p.score !== null)
        .sort((a, b) => Math.abs(a.score - currentScore) - Math.abs(b.score - currentScore))
        .slice(0, 3)
    } catch {
      similarProfessors.value = []
    }
  }

  function clearSections() {
    sections.value = []
    selectedInstructor.value = null
    selectedSemester.value = null
    similarProfessors.value = []
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

  // Professor score from 0–100 using a weighted formula:
  //   70% based on average GPA (scaled to 0–4.0)
  //   30% based on percentage of students who received an A
  // Returns null if there is not enough data to compute.
  const professorScore = computed(() => {
    if (!averageGpa.value) return null
    const totalGraded = sections.value.reduce((sum, s) => sum + s.a_to_f, 0)
    if (totalGraded === 0) return null
    const totalA = sections.value.reduce((sum, s) => sum + s.a, 0)
    const aPercent = totalA / totalGraded
    return Math.min(100, Math.round((parseFloat(averageGpa.value) / 4.0) * 70 + aPercent * 30))
  })

  // All unique course codes this professor has ever taught (sorted alphabetically),
  // displayed as clickable links on the professor page.
  const uniqueCourses = computed(() => {
    const set = new Set(sections.value.map((s) => s.course))
    return [...set].sort()
  })

  // Compares the most recent semester's GPA against the previous one to determine
  // if the professor's grades have been trending up, down, or staying flat.
  // Returns null when fewer than 2 semesters of data exist.
  const gpaTrend = computed(() => {
    const sems = gpaPerSemester.value
    if (sems.length < 2) return null
    const latest = parseFloat(sems[sems.length - 1].avgGpa)
    const prev = parseFloat(sems[sems.length - 2].avgGpa)
    const delta = latest - prev
    if (Math.abs(delta) < 0.05) return { direction: 'flat', label: '→' }
    return {
      direction: delta > 0 ? 'up' : 'down',
      label: delta > 0 ? '↑' : '↓',
      delta: (delta > 0 ? '+' : '') + delta.toFixed(2),
    }
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
    professorScore,
    gpaTrend,
    uniqueCourses,
    gpaPerSemester,
    similarProfessors,
    fetchSemesters,
    fetchSections,
    clearSections,
  }
})
