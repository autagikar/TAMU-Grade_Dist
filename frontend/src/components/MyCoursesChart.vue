<!-- Multi-line GPA trend chart for the My Courses page.
     Renders one line per saved course. The X-axis is the union of all semesters
     across every course so lines share the same time axis. Colors cycle through
     a 10-color palette starting with maroon. -->

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  // Array of { course: string, data: [{ semester, avgGpa }] }
  // One entry per saved course — provided by myCourses store's gpaSeriesByCourse computed.
  series: { type: Array, required: true },
})

const COLORS = [
  '#5c0000', '#2196f3', '#4caf50', '#ff9800', '#9c27b0',
  '#00bcd4', '#f44336', '#795548', '#607d8b', '#e91e63',
]

function semesterSortKey(sem) {
  const [term, year] = sem.split(' ')
  const termOrder = { Spring: 1, Summer: 2, Fall: 3 }
  return parseInt(year) * 10 + (termOrder[term] ?? 0)
}

// Build a sorted union of all semesters appearing in any course's data
const allSemesters = computed(() => {
  const set = new Set()
  props.series.forEach((s) => s.data.forEach((d) => set.add(d.semester)))
  return [...set].sort((a, b) => semesterSortKey(a) - semesterSortKey(b))
})

const chartData = computed(() => ({
  labels: allSemesters.value,
  datasets: props.series.map(({ course, data }, i) => {
    const color = COLORS[i % COLORS.length]
    // Build a lookup map so we can fill gaps with null for semesters missing from this course
    const map = Object.fromEntries(data.map((d) => [d.semester, d.avgGpa]))
    return {
      label: course,
      data: allSemesters.value.map((sem) => map[sem] ?? null),
      borderColor: color,
      backgroundColor: color,
      pointBackgroundColor: color,
      pointRadius: 4,
      tension: 0.3,
      fill: false,
      spanGaps: true, // draw a line through semesters where this course has no data
    }
  }),
}))

// Auto-scale Y axis: find the min and max GPA across all series, add 0.2 padding,
// and clamp between 0 and 4.3 (4.3 allows us to hide the top tick label).
const yBounds = computed(() => {
  const values = props.series.flatMap((s) => s.data.map((d) => d.avgGpa))
  if (!values.length) return { min: 0, max: 4 }
  const PADDING = 0.2
  return {
    min: Math.max(0, Math.floor((Math.min(...values) - PADDING) * 10) / 10),
    max: Math.min(4.3, Math.ceil((Math.max(...values) + PADDING) * 10) / 10),
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'nearest', intersect: false },
  plugins: {
    legend: { display: true }, // show legend since there are multiple lines
    tooltip: {
      callbacks: {
        title: () => '',
        label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}`,
      },
    },
    datalabels: { display: false },
  },
  scales: {
    y: {
      min: yBounds.value.min,
      max: yBounds.value.max,
      ticks: { callback: (v) => (v <= 4 ? +v.toFixed(2) : '') },
      title: { display: true, text: 'Average GPA' },
    },
  },
}))
</script>

<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  height: 360px;
  width: 100%;
}
</style>
