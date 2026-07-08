<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  info: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

// Splits prerequisite text into plain-text and course-link segments.
// e.g. "Grade of C in CSCE 315 or CSCE 331" →
//   [{ type:'text', value:'Grade of C in ' },
//    { type:'course', display:'CSCE 315', code:'CSCE-315' }, ...]
function splitPrereqs(text) {
  if (!text) return []
  const parts = []
  const pattern = /\b([A-Z]{3,5})\s+(\d{3}[A-Z]?\w*)\b/g
  let lastIndex = 0
  let match
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: text.slice(lastIndex, match.index) })
    }
    parts.push({ type: 'course', display: match[0], code: `${match[1]}-${match[2]}` })
    lastIndex = pattern.lastIndex
  }
  if (lastIndex < text.length) {
    parts.push({ type: 'text', value: text.slice(lastIndex) })
  }
  return parts
}
</script>

<template>
  <div v-if="loading" class="info-card loading-state">
    <span class="loading-text">Loading course info...</span>
  </div>

  <div v-else-if="info" class="info-card">
    <h2 class="course-title">{{ info.title }}</h2>

    <div class="chips">
      <span v-if="info.credits != null" class="chip">
        <span class="chip-label">Credits</span>
        <span class="chip-value">{{ info.credits }}</span>
      </span>
      <span v-if="info.lecture_hours != null" class="chip">
        <span class="chip-label">Lecture Hours</span>
        <span class="chip-value">{{ info.lecture_hours }}</span>
      </span>
      <span v-if="info.lecture_hours != null || info.lab_hours != null" class="chip">
        <span class="chip-label">Lab Hours</span>
        <span class="chip-value">{{ info.lab_hours ?? 0 }}</span>
      </span>
    </div>

    <p v-if="info.description" class="description">{{ info.description }}</p>

    <div v-if="info.prerequisites" class="prereqs">
      <span class="prereqs-label">Prerequisites:</span>
      <span class="prereqs-text">
        <template v-for="(part, i) in splitPrereqs(info.prerequisites)" :key="i">
          <RouterLink
            v-if="part.type === 'course'"
            :to="`/?course=${part.code}`"
            class="prereq-link"
          >{{ part.display }}</RouterLink>
          <template v-else>{{ part.value }}</template>
        </template>
      </span>
    </div>
  </div>
</template>

<style scoped>
.info-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 24px;
}

.loading-state {
  display: flex;
  align-items: center;
  min-height: 80px;
}

.loading-text {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.course-title {
  margin: 0 0 14px;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  background: color-mix(in srgb, var(--primary) 8%, var(--surface));
  border: 1px solid color-mix(in srgb, var(--primary) 20%, var(--border));
  font-size: 0.82rem;
}

.chip-label {
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.72rem;
}

.chip-value {
  font-weight: 700;
  color: var(--primary-text);
}

.description {
  margin: 0 0 14px;
  font-size: 0.92rem;
  color: var(--text);
  line-height: 1.65;
}

.prereqs {
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.6;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.prereqs-label {
  font-weight: 600;
  color: var(--text);
  margin-right: 4px;
}

.prereqs-text {
  color: var(--text-muted);
}

.prereq-link {
  color: var(--primary-text);
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1px dotted var(--primary-text);
}

.prereq-link:hover {
  border-bottom-style: solid;
}
</style>
