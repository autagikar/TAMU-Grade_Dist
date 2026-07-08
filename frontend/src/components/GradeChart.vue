<!-- Grade distribution as a smooth bell curve area chart.
     Grades are ordered F → A (left to right) so a typical class peaks toward
     the right and takes on a natural bell or right-skewed curve shape.
     The fill under the curve is a semi-transparent maroon area. -->

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
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip)

const props = defineProps({
  gradeTotals: { type: Object, required: true },
  // Border color for the curve line and points (default maroon)
  color: { type: String, default: '#5c0000' },
})

const totalGraded = computed(() =>
  props.gradeTotals.f + props.gradeTotals.d + props.gradeTotals.c +
  props.gradeTotals.b + props.gradeTotals.a,
)

// Raw counts ordered F → A to match the x-axis label order
const counts = computed(() => [
  props.gradeTotals.f,
  props.gradeTotals.d,
  props.gradeTotals.c,
  props.gradeTotals.b,
  props.gradeTotals.a,
])

// Percentages ordered F → A
const percents = computed(() => {
  const t = totalGraded.value
  return counts.value.map((n) => (t ? parseFloat(((n / t) * 100).toFixed(1)) : 0))
})

const chartData = computed(() => ({
  labels: ['F', 'D', 'C', 'B', 'A'],
  datasets: [
    {
      data: percents.value,
      borderColor: props.color,
      backgroundColor: props.color + '30', // ~19% opacity fill under curve
      fill: true,
      tension: 0.4,           // smooth bezier curve
      pointRadius: 6,
      pointHoverRadius: 8,
      pointBackgroundColor: props.color,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
    },
  ],
}))

const chartOptions = computed(() => {
  const maxPct = Math.max(...percents.value, 10)
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const labels = ['F', 'D', 'C', 'B', 'A']
            const countMap = { F: props.gradeTotals.f, D: props.gradeTotals.d, C: props.gradeTotals.c, B: props.gradeTotals.b, A: props.gradeTotals.a }
            const grade = labels[ctx.dataIndex]
            return `${grade}: ${ctx.parsed.y}%  (${countMap[grade].toLocaleString()} students)`
          },
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
        // Auto-scale Y ceiling to 10% above the tallest bar so the curve
        // doesn't get clipped and small distributions aren't squished
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
    <Line v-if="totalGraded > 0" :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  height: 340px;
  width: 100%;
}
</style>
