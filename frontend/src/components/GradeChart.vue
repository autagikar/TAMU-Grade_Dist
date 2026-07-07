<!-- Bar chart showing the grade distribution (A/B/C/D/F) as percentages.
     Accepts a gradeTotals prop with raw counts and converts them to percentages
     for display. Each bar is labeled with its percentage using chartjs-plugin-datalabels.

     IMPORTANT: ChartDataLabels is passed as a :plugins prop directly on the <Bar>
     component rather than being registered globally via ChartJS.register(). This is
     intentional — globally registered datalabels bleeds into line charts and causes
     a "partially erased" visual artifact around data points. -->

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
import ChartDataLabels from 'chartjs-plugin-datalabels'

// Register core Chart.js modules (NOT ChartDataLabels — see note above)
ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  // Object with keys a, b, c, d, f — each is a raw student count
  gradeTotals: { type: Object, required: true },
})

// Sum of all letter grades (excludes Q, W, I, etc.)
const total = computed(
  () => props.gradeTotals.a + props.gradeTotals.b + props.gradeTotals.c + props.gradeTotals.d + props.gradeTotals.f,
)

// Convert a raw count to a percentage of total graded students
const pct = (n) => (total.value ? ((n / total.value) * 100).toFixed(1) : 0)

const rawCounts = computed(() => [
  props.gradeTotals.a,
  props.gradeTotals.b,
  props.gradeTotals.c,
  props.gradeTotals.d,
  props.gradeTotals.f,
])

const chartData = computed(() => ({
  labels: ['A', 'B', 'C', 'D', 'F'],
  datasets: [
    {
      label: 'Students',
      data: rawCounts.value.map((n) => parseFloat(pct(n))),
      backgroundColor: ['#4caf50', '#2196f3', '#ff9800', '#f44336', '#9c27b0'],
      borderRadius: 4,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        // Tooltip shows both the percentage and the raw student count
        label: (ctx) => ` ${ctx.parsed.y}%  (${rawCounts.value[ctx.dataIndex]} students)`,
      },
    },
    datalabels: {
      anchor: 'end',
      align: 'end',
      formatter: (value) => `${value}%`,
      font: { weight: 'bold', size: 13 },
      color: '#333',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: { callback: (v) => `${v}%` },
      title: { display: true, text: '% of graded students' },
    },
  },
}))
</script>

<template>
  <div class="chart-container">
    <!-- Pass ChartDataLabels as a prop so it only applies to this bar chart -->
    <Bar :data="chartData" :options="chartOptions" :plugins="[ChartDataLabels]" />
  </div>
</template>

<style scoped>
.chart-container {
  height: 340px;
  width: 100%;
}
</style>
