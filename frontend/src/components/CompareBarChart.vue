<!-- Grouped bar chart comparing the grade distributions of two courses or professors.
     Each grade (A–F) shows two bars side by side: one for slot A (maroon) and
     one for slot B (blue). Values are displayed as percentages of graded students. -->

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  courseA: { type: String, default: null },  // label for the first dataset (maroon)
  courseB: { type: String, default: null },  // label for the second dataset (blue)
  totalsA: { type: Object, required: true }, // { a, b, c, d, f } raw counts for A
  totalsB: { type: Object, required: true }, // { a, b, c, d, f } raw counts for B
})

// Convert raw grade counts to percentage of all graded students.
// Returns an array of 5 numbers: [A%, B%, C%, D%, F%]
function toPercents(totals) {
  const sum = totals.a + totals.b + totals.c + totals.d + totals.f
  if (!sum) return [0, 0, 0, 0, 0]
  return [totals.a, totals.b, totals.c, totals.d, totals.f].map(
    (v) => parseFloat(((v / sum) * 100).toFixed(1)),
  )
}

const chartData = computed(() => ({
  labels: ['A', 'B', 'C', 'D', 'F'],
  datasets: [
    {
      label: props.courseA ?? 'Course A',
      data: toPercents(props.totalsA),
      backgroundColor: 'rgba(92, 0, 0, 0.8)',   // maroon
    },
    {
      label: props.courseB ?? 'Course B',
      data: toPercents(props.totalsB),
      backgroundColor: 'rgba(33, 150, 243, 0.8)', // blue
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}%`,
      },
    },
    // datalabels is not used here — the grouped bars are too narrow for labels
    datalabels: { display: false },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: { callback: (v) => `${v}%` },
      title: { display: true, text: '% of Graded Students' },
    },
  },
}
</script>

<template>
  <div class="chart-container">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  height: 300px;
  width: 100%;
}
</style>
