<!-- Grade distribution comparison as two overlapping smooth curves.
     Slot A (maroon) and slot B (blue) are drawn on the same axes with
     semi-transparent fills so the overlap is clearly visible.
     Grades are ordered F → A left to right. -->

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps({
  courseA: { type: String, default: null },
  courseB: { type: String, default: null },
  totalsA: { type: Object, required: true },
  totalsB: { type: Object, required: true },
})

// Converts { a, b, c, d, f } counts to percentages ordered F → A
function toPercents(totals) {
  const sum = totals.f + totals.d + totals.c + totals.b + totals.a
  if (!sum) return [0, 0, 0, 0, 0]
  return [totals.f, totals.d, totals.c, totals.b, totals.a].map(
    (v) => parseFloat(((v / sum) * 100).toFixed(1)),
  )
}

const percentsA = computed(() => toPercents(props.totalsA))
const percentsB = computed(() => toPercents(props.totalsB))

const chartData = computed(() => ({
  labels: ['F', 'D', 'C', 'B', 'A'],
  datasets: [
    {
      label: props.courseA ?? 'A',
      data: percentsA.value,
      borderColor: '#5c0000',
      backgroundColor: 'rgba(92, 0, 0, 0.15)',
      fill: true,
      tension: 0.4,
      pointRadius: 5,
      pointHoverRadius: 7,
      pointBackgroundColor: '#5c0000',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
    },
    {
      label: props.courseB ?? 'B',
      data: percentsB.value,
      borderColor: '#2196f3',
      backgroundColor: 'rgba(33, 150, 243, 0.15)',
      fill: true,
      tension: 0.4,
      pointRadius: 5,
      pointHoverRadius: 7,
      pointBackgroundColor: '#2196f3',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
    },
  ],
}))

const chartOptions = computed(() => {
  const maxPct = Math.max(...percentsA.value, ...percentsB.value, 10)
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        labels: { usePointStyle: true, pointStyle: 'circle' },
      },
      tooltip: {
        callbacks: {
          label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}%`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 14, weight: '600' } },
      },
      y: {
        beginAtZero: true,
        max: Math.ceil((maxPct * 1.15) / 10) * 10,
        ticks: { callback: (v) => `${v}%` },
        grid: { color: '#f0f0f0' },
      },
    },
  }
})
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
