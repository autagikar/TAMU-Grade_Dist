<!-- Circular progress ring displaying a 0–100 score.
     The ring fills clockwise from the top as the score increases.
     Color shifts from red (low) through yellow (mid) to green (high). -->

<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: null },
  size: { type: Number, default: 72 },
})

const RADIUS = 38
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

// How much of the ring to fill based on the score
const fillLength = computed(() =>
  props.score !== null ? (props.score / 100) * CIRCUMFERENCE : 0,
)

// Gap = the unfilled portion of the ring
const gapLength = computed(() => CIRCUMFERENCE - fillLength.value)

// Red → yellow → green based on score
const color = computed(() => {
  if (props.score === null) return '#ccc'
  if (props.score < 50) {
    const t = props.score / 50
    return `rgb(220, ${Math.round(t * 180)}, 0)`
  } else {
    const t = (props.score - 50) / 50
    return `rgb(${Math.round(220 * (1 - t))}, 180, 0)`
  }
})
</script>

<template>
  <!-- SVG ring: background track + colored progress arc + score label -->
  <svg viewBox="0 0 100 100" class="ring" aria-label="`Professor score: ${score}`">
    <!-- Gray background track -->
    <circle
      cx="50" cy="50" :r="RADIUS"
      fill="none"
      stroke="#e8e8e8"
      stroke-width="10"
    />
    <!-- Colored progress arc — rotated so it starts at the top (12 o'clock) -->
    <circle
      cx="50" cy="50" :r="RADIUS"
      fill="none"
      :stroke="color"
      stroke-width="10"
      stroke-linecap="round"
      :stroke-dasharray="`${fillLength} ${gapLength}`"
      transform="rotate(-90 50 50)"
    />
    <!-- Score number in the center -->
    <text
      x="50" y="50"
      text-anchor="middle"
      dominant-baseline="central"
      class="score-text"
      :fill="color"
    >{{ score ?? '—' }}</text>
  </svg>
</template>

<style scoped>
.ring {
  width: v-bind(size + 'px');
  height: v-bind(size + 'px');
}

.score-text {
  font-size: 22px;
  font-weight: 700;
  font-family: inherit;
}
</style>
