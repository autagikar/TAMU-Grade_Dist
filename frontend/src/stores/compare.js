// Pinia store for the Compare Courses page.
// Uses a "slot" pattern — makeSlot() creates an independent reactive object
// with its own state and computed properties. The store exposes two slots
// (a and b) so both courses operate completely independently.

import { defineStore } from 'pinia'
import { reactive, computed } from 'vue'
import { getSections } from '@/api/index.js'

function semesterSortKey(sem) {
  const [term, year] = sem.split(' ')
  const termOrder = { Spring: 1, Summer: 2, Fall: 3 }
  return parseInt(year) * 10 + (termOrder[term] ?? 0)
}

// Creates a self-contained reactive slot for one course.
// Both slot a and slot b are created by calling this function,
// so they share the same logic but have completely separate state.
function makeSlot() {
  const state = reactive({ course: null, sections: [], loading: false })

  // Aggregate A/B/C/D/F counts for the grouped bar chart
  const gradeTotals = computed(() => {
    const t = { a: 0, b: 0, c: 0, d: 0, f: 0 }
    for (const s of state.sections) {
      t.a += s.a; t.b += s.b; t.c += s.c; t.d += s.d; t.f += s.f
    }
    return t
  })

  // Weighted average GPA across all sections for this course
  const averageGpa = computed(() => {
    const valid = state.sections.filter((s) => s.gpa !== null && s.a_to_f > 0)
    if (!valid.length) return null
    const weighted = valid.reduce((sum, s) => sum + s.gpa * s.a_to_f, 0)
    const total = valid.reduce((sum, s) => sum + s.a_to_f, 0)
    return (weighted / total).toFixed(3)
  })

  // Total students enrolled across all sections
  const totalStudents = computed(() =>
    state.sections.reduce((sum, s) => sum + s.total, 0),
  )

  // Average GPA per semester — used for the overlapping trend line chart.
  // Sorted oldest → newest so the line reads left to right.
  const gpaPerSemester = computed(() => {
    const map = {}
    for (const s of state.sections) {
      if (s.gpa === null || s.a_to_f === 0) continue
      if (!map[s.semester]) map[s.semester] = { weightedSum: 0, total: 0 }
      map[s.semester].weightedSum += s.gpa * s.a_to_f
      map[s.semester].total += s.a_to_f
    }
    return Object.entries(map)
      .map(([semester, d]) => ({ semester, avgGpa: (d.weightedSum / d.total).toFixed(3) }))
      .sort((a, b) => semesterSortKey(a.semester) - semesterSortKey(b.semester))
  })

  // Fetch all sections for the selected course and store them in this slot
  async function fetch(course) {
    state.loading = true
    state.course = course
    const res = await getSections(course)
    state.sections = res.data
    state.loading = false
  }

  function clear() {
    state.course = null
    state.sections = []
    state.loading = false
  }

  return { state, gradeTotals, averageGpa, totalStudents, gpaPerSemester, fetch, clear }
}

export const useCompareStore = defineStore('compare', () => {
  const a = makeSlot()  // Course A (maroon)
  const b = makeSlot()  // Course B (blue)
  return { a, b }
})
