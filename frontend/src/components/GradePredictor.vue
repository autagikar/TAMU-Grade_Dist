<!-- Grade Predictor card.
     Shown on the Course Search page when an instructor filter is active.
     Displays a historical probability breakdown of grades for that course+instructor combo. -->

<script setup>
import { computed } from 'vue'

const props = defineProps({
  sections:   { type: Array,  required: true },
  course:     { type: String, required: true },
  instructor: { type: String, required: true },
})

const totals = computed(() => {
  const t = { a: 0, b: 0, c: 0, d: 0, f: 0, q: 0, total: 0 }
  for (const s of props.sections) {
    t.a += s.a; t.b += s.b; t.c += s.c; t.d += s.d; t.f += s.f; t.q += s.q
    t.total += s.total
  }
  return t
})

const graded = computed(() => totals.value.a + totals.value.b + totals.value.c + totals.value.d + totals.value.f)

const bars = computed(() => {
  const g = graded.value
  const t = totals.value.total
  if (!g) return []
  return [
    { label: 'A', count: totals.value.a, pct: +((totals.value.a / g) * 100).toFixed(1), color: '#2e7d32' },
    { label: 'B', count: totals.value.b, pct: +((totals.value.b / g) * 100).toFixed(1), color: '#1565c0' },
    { label: 'C', count: totals.value.c, pct: +((totals.value.c / g) * 100).toFixed(1), color: '#f57f17' },
    { label: 'D', count: totals.value.d, pct: +((totals.value.d / g) * 100).toFixed(1), color: '#e65100' },
    { label: 'F', count: totals.value.f, pct: +((totals.value.f / g) * 100).toFixed(1), color: '#b71c1c' },
    { label: 'Q-Drop', count: totals.value.q, pct: t ? +((totals.value.q / t) * 100).toFixed(1) : 0, color: '#6a1b9a' },
  ]
})

// The single most common grade outcome
const topGrade = computed(() => {
  const grade = bars.value.slice(0, 5).reduce((best, b) => b.pct > best.pct ? b : best, { pct: 0 })
  return grade.pct > 0 ? grade : null
})

const abPct = computed(() => {
  const g = graded.value
  return g ? +(((totals.value.a + totals.value.b) / g) * 100).toFixed(0) : 0
})
</script>

<template>
  <div class="predictor">
    <div class="predictor-header">
      <div class="predictor-title">Grade Predictor</div>
      <div class="predictor-sub">
        {{ course }} with {{ instructor }} — {{ totals.total.toLocaleString() }} students across {{ sections.length }} sections
      </div>
    </div>

    <div class="predictor-body">
      <p v-if="topGrade" class="summary">
        Historically, <strong>{{ abPct }}%</strong> of students earn an A or B.
        The most common grade is <strong style="color: var(--primary-text)">{{ topGrade.label }} ({{ topGrade.pct }}%)</strong>.
      </p>

      <div class="bars">
        <div v-for="bar in bars" :key="bar.label" class="bar-row">
          <span class="bar-label">{{ bar.label }}</span>
          <div class="bar-track">
            <div
              class="bar-fill"
              :style="{ width: bar.pct + '%', background: bar.color }"
            />
          </div>
          <span class="bar-pct">{{ bar.pct }}%</span>
          <span class="bar-count">({{ bar.count.toLocaleString() }})</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.predictor {
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.predictor-header {
  background: var(--primary);
  color: white;
  padding: 14px 20px;
}

.predictor-title {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.predictor-sub {
  font-size: 0.82rem;
  opacity: 0.85;
  margin-top: 2px;
}

.predictor-body {
  background: var(--surface);
  padding: 18px 20px;
}

.summary {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: 16px;
  line-height: 1.5;
}

.summary strong {
  color: var(--text);
}

.bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  width: 52px;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text);
  flex-shrink: 0;
}

.bar-track {
  flex: 1;
  height: 10px;
  background: var(--border);
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.4s ease;
}

.bar-pct {
  width: 44px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text);
  text-align: right;
  flex-shrink: 0;
}

.bar-count {
  width: 60px;
  font-size: 0.75rem;
  color: var(--text-muted);
  flex-shrink: 0;
}
</style>
