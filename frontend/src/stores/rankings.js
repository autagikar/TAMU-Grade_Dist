// Pinia store for the Department Rankings page.
// Fetches the department list once on mount, then fetches professor rankings
// whenever the user picks a department from the dropdown.

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDepartments, getDepartmentRankings } from '@/api/index.js'

export const useRankingsStore = defineStore('rankings', () => {
  const departments = ref([])         // all department names for the dropdown
  const selectedDepartment = ref(null)
  const rankings = ref([])            // sorted professor ranking rows
  const loading = ref(false)

  async function fetchDepartments() {
    const res = await getDepartments()
    departments.value = res.data
  }

  async function fetchRankings(department) {
    loading.value = true
    selectedDepartment.value = department
    const res = await getDepartmentRankings(department)
    rankings.value = res.data
    loading.value = false
  }

  function clear() {
    selectedDepartment.value = null
    rankings.value = []
  }

  return { departments, selectedDepartment, rankings, loading, fetchDepartments, fetchRankings, clear }
})
