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
  // Single-line mode (professor view): array of { semester, avgGpa }
  gpaPerSemester: { type: Array, default: null },
  // Multi-line mode (course view): array of { instructor, data: [{ semester, avgGpa }] }
  instructorData: { type: Array, default: null },
})

const COLORS = [
  '#5c0000', '#2196f3', '#4caf50', '#ff9800', '#9c27b0',
  '#00bcd4', '#f44336', '#795548', '#607d8b', '#e91e63',
]

// Collect all unique semesters across all instructors for the X axis
const allSemesters = computed(() => {
  if (props.gpaPerSemester) return props.gpaPerSemester.map((d) => d.semester)
  const set = new Set()
  for (const inst of props.instructorData ?? []) {
    inst.data.forEach((d) => set.add(d.semester))
  }
  return [...set]
})

const chartData = computed(() => {
  if (props.gpaPerSemester) {
    return {
      labels: allSemesters.value,
      datasets: [{
        label: 'Avg GPA',
        data: props.gpaPerSemester.map((d) => parseFloat(d.avgGpa)),
        borderColor: '#5c0000',
        backgroundColor: 'rgba(92,0,0,0.1)',
        pointBackgroundColor: '#5c0000',
        pointRadius: 5,
        tension: 0.3,
        fill: false,
      }],
    }
  }

  return {
    labels: allSemesters.value,
    datasets: (props.instructorData ?? []).map((inst, i) => {
      const color = COLORS[i % COLORS.length]
      const semMap = Object.fromEntries(inst.data.map((d) => [d.semester, parseFloat(d.avgGpa)]))
      return {
        label: inst.instructor,
        data: allSemesters.value.map((sem) => semMap[sem] ?? null),
        borderColor: color,
        backgroundColor: color,
        pointBackgroundColor: color,
        pointRadius: 4,
        tension: 0.3,
        fill: false,
        spanGaps: true,
      }
    }),
  }
})

// Compute min/max from all data points and add padding so the lines
// don't touch the edges of the chart
const yBounds = computed(() => {
  const values = []
  if (props.gpaPerSemester) {
    props.gpaPerSemester.forEach((d) => values.push(parseFloat(d.avgGpa)))
  } else {
    ;(props.instructorData ?? []).forEach((inst) =>
      inst.data.forEach((d) => values.push(parseFloat(d.avgGpa))),
    )
  }
  if (!values.length) return { min: 0, max: 4 }
  const PADDING = 0.2
  const raw_min = Math.min(...values)
  const raw_max = Math.max(...values)
  return {
    min: Math.max(0, Math.floor((raw_min - PADDING) * 10) / 10),
    max: Math.min(4.3, Math.ceil((raw_max + PADDING) * 10) / 10),
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'nearest',
    intersect: false,
  },
  plugins: {
    legend: { display: !!props.instructorData },
    tooltip: {
      callbacks: {
        title: () => '',
        label: (ctx) => ` ${ctx.dataset.label}:  ${ctx.parsed.y}`,
      },
    },
    datalabels: { display: false },
  },
  scales: {
    y: {
      min: yBounds.value.min,
      max: yBounds.value.max,
      ticks: {
        callback: (v) => (v <= 4 ? +v.toFixed(2) : ''),
      },
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
  height: 320px;
  width: 100%;
}
</style>
