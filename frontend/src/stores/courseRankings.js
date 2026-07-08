import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDepartments, getCourseRankings } from '@/api/index.js'

export const useCourseRankingsStore = defineStore('courseRankings', () => {
  const departments = ref([])
  const selectedDepartment = ref(null)
  const rankings = ref([])
  const loading = ref(false)

  async function fetchDepartments() {
    const res = await getDepartments()
    departments.value = res.data
  }

  async function fetchRankings(department) {
    loading.value = true
    selectedDepartment.value = department
    const res = await getCourseRankings(department)
    rankings.value = res.data
    loading.value = false
  }

  function clear() {
    selectedDepartment.value = null
    rankings.value = []
  }

  return { departments, selectedDepartment, rankings, loading, fetchDepartments, fetchRankings, clear }
})
