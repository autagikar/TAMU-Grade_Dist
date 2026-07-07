<!-- Overlapping line chart showing GPA trends over time for two courses or professors.
     Slot A is drawn in maroon, slot B in blue. The X-axis uses the union of all
     semesters from both datasets so both lines share the same time axis.
     The Y-axis auto-scales to the data range with 0.2 padding on each side. -->

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
  courseA: { type: String, default: null },  // label for line A
  courseB: { type: String, default: null },  // label for line B
  gpaA: { type: Array, default: () => [] },  // [{ semester, avgGpa }] for A
  gpaB: { type: Array, default: () => [] },  // [{ semester, avgGpa }] for B
})

function semesterSortKey(sem) {
  const [term, year] = sem.split(' ')
  const termOrder = { Spring: 1, Summer: 2, Fall: 3 }
  return parseInt(year) * 10 + (termOrder[term] ?? 0)
}

// Collect every unique semester from both datasets and sort chronologically.
// Using a union means gaps in one line appear as null (spanGaps: true fills them).
const allSemesters = computed(() => {
  const set = new Set()
  props.gpaA.forEach((d) => set.add(d.semester))
  props.gpaB.forEach((d) => set.add(d.semester))
  return [...set].sort((a, b) => semesterSortKey(a) - semesterSortKey(b))
})

const chartData = computed(() => {
  // Build lookup maps for O(1) access when building the data arrays
  const mapA = Object.fromEntries(props.gpaA.map((d) => [d.semester, parseFloat(d.avgGpa)]))
  const mapB = Object.fromEntries(props.gpaB.map((d) => [d.semester, parseFloat(d.avgGpa)]))
  return {
    labels: allSemesters.value,
    datasets: [
      {
        label: props.courseA ?? 'Course A',
        data: allSemesters.value.map((sem) => mapA[sem] ?? null),
        borderColor: '#5c0000',
        backgroundColor: 'rgba(92,0,0,0.1)',
        pointBackgroundColor: '#5c0000',
        pointRadius: 4,
        tension: 0.3,
        fill: false,
        spanGaps: true, // connect across semesters where data is missing
      },
      {
        label: props.courseB ?? 'Course B',
        data: allSemesters.value.map((sem) => mapB[sem] ?? null),
        borderColor: '#2196f3',
        backgroundColor: 'rgba(33,150,243,0.1)',
        pointBackgroundColor: '#2196f3',
        pointRadius: 4,
        tension: 0.3,
        fill: false,
        spanGaps: true,
      },
    ],
  }
})

// Compute min/max across both datasets and add 0.2 padding so lines don't
// touch the chart edges. Clamp to 0–4.3 (4.3 lets us hide the top label).
const yBounds = computed(() => {
  const values = [
    ...props.gpaA.map((d) => parseFloat(d.avgGpa)),
    ...props.gpaB.map((d) => parseFloat(d.avgGpa)),
  ]
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
    legend: { display: true },
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
      // Hide the 4.3 tick label — it's only there to give padding above 4.0
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
  height: 300px;
  width: 100%;
}
</style>
