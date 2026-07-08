// Pinia store for the Compare Professors page.
// Mirrors the structure of compare.js but fetches sections by instructor
// instead of by course. Each slot also exposes uniqueCourses so both professors'
// course tag lists can be displayed and linked on the compare page.

import { defineStore } from 'pinia'
import { reactive, computed } from 'vue'
import { getSections } from '@/api/index.js'

function semesterSortKey(sem) {
  const [term, year] = sem.split(' ')
  const termOrder = { Spring: 1, Summer: 2, Fall: 3 }
  return parseInt(year) * 10 + (termOrder[term] ?? 0)
}

// Creates a self-contained reactive slot for one professor.
// See compare.js for the same pattern applied to courses.
function makeSlot() {
  const state = reactive({ instructor: null, sections: [], loading: false })

  // Aggregate A/B/C/D/F counts for the grade distribution comparison chart
  const gradeTotals = computed(() => {
    const t = { a: 0, b: 0, c: 0, d: 0, f: 0 }
    for (const s of state.sections) {
      t.a += s.a; t.b += s.b; t.c += s.c; t.d += s.d; t.f += s.f
    }
    return t
  })

  // Weighted average GPA across all sections for this professor
  const averageGpa = computed(() => {
    const valid = state.sections.filter((s) => s.gpa !== null && s.gpa > 0 && s.a_to_f > 0)
    if (!valid.length) return null
    const weighted = valid.reduce((sum, s) => sum + s.gpa * s.a_to_f, 0)
    const total = valid.reduce((sum, s) => sum + s.a_to_f, 0)
    return (weighted / total).toFixed(3)
  })

  // Total students enrolled (graded + Q/W/etc.)
  const totalStudents = computed(() =>
    state.sections.reduce((sum, s) => sum + s.total, 0),
  )

  // Professor score 0–100: 70% weighted average GPA + 30% percentage of A grades
  const professorScore = computed(() => {
    if (!averageGpa.value) return null
    const totalGraded = state.sections.reduce((sum, s) => sum + s.a_to_f, 0)
    if (totalGraded === 0) return null
    const totalA = state.sections.reduce((sum, s) => sum + s.a, 0)
    const aPercent = totalA / totalGraded
    return Math.min(100, Math.round((parseFloat(averageGpa.value) / 4.0) * 70 + aPercent * 30))
  })

  // All unique courses this professor has taught, sorted alphabetically.
  // Displayed as clickable tags on the compare page linking back to Course Search.
  const uniqueCourses = computed(() => {
    const set = new Set(state.sections.map((s) => s.course))
    return [...set].sort()
  })

  // Average GPA per semester for the overlapping trend line chart
  const gpaPerSemester = computed(() => {
    const map = {}
    for (const s of state.sections) {
      if (s.gpa === null || s.gpa === 0 || s.a_to_f === 0) continue
      if (!map[s.semester]) map[s.semester] = { weightedSum: 0, total: 0 }
      map[s.semester].weightedSum += s.gpa * s.a_to_f
      map[s.semester].total += s.a_to_f
    }
    return Object.entries(map)
      .map(([semester, d]) => ({ semester, avgGpa: (d.weightedSum / d.total).toFixed(3) }))
      .sort((a, b) => semesterSortKey(a.semester) - semesterSortKey(b.semester))
  })

  // Fetch all sections taught by this instructor (all semesters, all courses)
  async function fetch(instructor) {
    state.loading = true
    state.instructor = instructor
    const res = await getSections(null, null, instructor)
    state.sections = res.data
    state.loading = false
  }

  function clear() {
    state.instructor = null
    state.sections = []
    state.loading = false
  }

  return { state, gradeTotals, averageGpa, totalStudents, professorScore, uniqueCourses, gpaPerSemester, fetch, clear }
}

export const useCompareProfessorStore = defineStore('compareProfessor', () => {
  const a = makeSlot()  // Professor A (maroon)
  const b = makeSlot()  // Professor B (blue)
  return { a, b }
})
