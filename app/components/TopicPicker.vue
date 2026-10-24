<script setup lang="ts">
import { ref, computed } from 'vue'
import topicsData from '~/../data/topics.json'

interface Topic {
  id: string
  grade: number
  realm: string
  title: string
  fantasy_name: string
  domain: string
  standard: string
  standard_text: string
  standard_verified: boolean
  verifier_type: string
  misconceptions: { tag: string; description: string }[]
  tier: string
  unlock_order: number
  icon: string
  island_theme: string
}

const props = defineProps<{
  currentGrade: 5 | 6
  selectedTopicId?: string
}>()

const emit = defineEmits<{
  (e: 'selectTopic', topic: Topic): void
  (e: 'update:grade', grade: 5 | 6): void
}>()

const allTopics = ref<Topic[]>(topicsData as Topic[])
const activeFilter = ref<'all' | 'Enchanted Forest' | 'Temple of Wisdom' | 'Celestial Frontier'>('all')

const gradeTopics = computed(() => {
  return allTopics.value.filter((t) => t.grade === props.currentGrade)
})

const filteredTopics = computed(() => {
  if (activeFilter.value === 'all') return gradeTopics.value
  return gradeTopics.value.filter((t) => t.realm === activeFilter.value)
})

const getRealmTheme = (realm: string) => {
  if (realm === 'Enchanted Forest') return 'emerald'
  if (realm === 'Temple of Wisdom') return 'gold'
  return 'violet'
}
</script>

<template>
  <section class="topic-picker-section" aria-labelledby="curriculum-heading">
    <!-- Header with Grade Switcher & Domain Filters -->
    <div class="picker-header">
      <div class="header-titles">
        <div class="badge-row">
          <span class="badge badge-gold">Georgia Standards Registry</span>
          <span class="badge badge-common">20 Official Topics</span>
        </div>
        <h2 id="curriculum-heading" class="picker-title font-display">
          Curriculum Islands — Grade {{ currentGrade }}
        </h2>
        <p class="picker-subtitle">
          Choose a mathematical domain to initiate targeted practice, explore worked examples, or test for misconception diagnosis.
        </p>
      </div>

      <!-- Controls: Grade Switcher + Realm Filter -->
      <div class="picker-controls">
        <div class="grade-toggle-group">
          <button
            type="button"
            class="btn-grade"
            :class="{ 'is-active': currentGrade === 5 }"
            @click="emit('update:grade', 5)"
          >
            Grade 5 (10 Topics)
          </button>
          <button
            type="button"
            class="btn-grade"
            :class="{ 'is-active': currentGrade === 6 }"
            @click="emit('update:grade', 6)"
          >
            Grade 6 (10 Topics)
          </button>
        </div>

        <div class="realm-filter-tabs">
          <button
            type="button"
            class="filter-tab"
            :class="{ 'is-active': activeFilter === 'all' }"
            @click="activeFilter = 'all'"
          >
            All Sectors ({{ gradeTopics.length }})
          </button>
          <button
            type="button"
            class="filter-tab tab-emerald"
            :class="{ 'is-active': activeFilter === 'Enchanted Forest' }"
            @click="activeFilter = 'Enchanted Forest'"
          >
            🌿 Forest ({{ gradeTopics.filter(t => t.realm === 'Enchanted Forest').length }})
          </button>
          <button
            type="button"
            class="filter-tab tab-gold"
            :class="{ 'is-active': activeFilter === 'Temple of Wisdom' }"
            @click="activeFilter = 'Temple of Wisdom'"
          >
            🏛️ Temple ({{ gradeTopics.filter(t => t.realm === 'Temple of Wisdom').length }})
          </button>
          <button
            type="button"
            class="filter-tab tab-violet"
            :class="{ 'is-active': activeFilter === 'Celestial Frontier' }"
            @click="activeFilter = 'Celestial Frontier'"
          >
            ✨ Celestial ({{ gradeTopics.filter(t => t.realm === 'Celestial Frontier').length }})
          </button>
        </div>
      </div>
    </div>

    <!-- Topics Grid -->
    <div class="topics-grid">
      <div
        v-for="topic in filteredTopics"
        :key="topic.id"
        class="topic-island-card quest-surface-card"
        :class="[
          `theme-${getRealmTheme(topic.realm)}`,
          { 'is-selected': selectedTopicId === topic.id }
        ]"
        tabindex="0"
        role="button"
        :aria-pressed="selectedTopicId === topic.id"
        @click="emit('selectTopic', topic)"
        @keydown.enter.space.prevent="emit('selectTopic', topic)"
      >
        <div class="card-accent-bar" />

        <div class="card-inner">
          <!-- Top Row: Icon + Badges -->
          <div class="card-top">
            <span class="topic-icon" role="img" :aria-label="topic.title">{{ topic.icon }}</span>
            <div class="topic-tags">
              <span v-if="topic.tier === 'flagship'" class="badge badge-gold">Flagship</span>
              <span class="badge" :class="`badge-${getRealmTheme(topic.realm)}`">{{ topic.realm }}</span>
              <span class="badge badge-common font-mono">G{{ topic.grade }}</span>
            </div>
          </div>

          <!-- Titles: Plain Math + Fantasy Lore -->
          <div class="topic-naming">
            <h3 class="plain-title font-body">{{ topic.title }}</h3>
            <span class="fantasy-title font-display">{{ topic.fantasy_name }}</span>
          </div>

          <!-- Standard Code & Domain -->
          <div class="standard-pill">
            <div class="standard-header">
              <span class="standard-code font-mono">{{ topic.standard }}</span>
              <span v-if="topic.standard_verified" class="verified-badge font-mono">✓ Georgia Verified</span>
            </div>
            <p class="standard-text">{{ topic.standard_text }}</p>
          </div>

          <!-- Island Theme & Misconceptions summary -->
          <div class="island-meta">
            <span class="island-location">📍 Island: {{ topic.island_theme }}</span>
            <span class="misconception-count font-mono">🔍 {{ topic.misconceptions.length }} Diagnosed Misconceptions</span>
          </div>

          <!-- Action Button -->
          <div class="card-action">
            <button type="button" class="btn-select-topic">
              <span>Enter Topic Island</span>
              <span aria-hidden="true">→</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.topic-picker-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  margin-top: var(--space-xl);
  margin-bottom: var(--space-2xl);
}

.picker-header {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  background: rgba(16, 27, 53, 0.65);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  padding: 24px;
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.picker-title {
  font-size: 24px;
  color: var(--quest-parchment);
}

.picker-subtitle {
  font-size: 14px;
  color: var(--quest-parchment-muted);
  max-width: 820px;
  line-height: 1.5;
}

.picker-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding-top: 14px;
  border-top: 1px solid var(--border-subtle);
}

.grade-toggle-group {
  display: flex;
  align-items: center;
  background: var(--quest-abyss);
  border: 1px solid var(--quest-gold);
  border-radius: var(--radius-sm);
  padding: 3px;
  gap: 4px;
}

.btn-grade {
  background: transparent;
  border: none;
  color: var(--quest-parchment-muted);
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.04em;
}

.btn-grade:hover {
  color: var(--quest-parchment);
}

.btn-grade.is-active {
  background: linear-gradient(135deg, #D9B66F 0%, #B89246 100%);
  color: var(--quest-midnight);
  box-shadow: 0 0 10px rgba(217, 182, 111, 0.35);
}

.realm-filter-tabs {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-tab {
  background: rgba(25, 61, 101, 0.4);
  border: 1px solid var(--border-subtle);
  color: var(--quest-parchment-muted);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  color: var(--quest-parchment);
  border-color: var(--border-medium);
}

.filter-tab.is-active {
  background: rgba(25, 61, 101, 0.85);
  border-color: var(--quest-gold);
  color: var(--quest-gold);
}

.filter-tab.tab-emerald.is-active {
  border-color: #28745B;
  color: #7AE0BF;
}

.filter-tab.tab-gold.is-active {
  border-color: var(--quest-gold);
  color: var(--quest-gold);
}

.filter-tab.tab-violet.is-active {
  border-color: #9C8AD6;
  color: #D4C9FF;
}

/* Topics Grid */
.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.topic-island-card {
  position: relative;
  overflow: hidden;
  cursor: pointer;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-medium);
  background: rgba(25, 61, 101, 0.45);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.topic-island-card:hover {
  transform: translateY(-2px);
  border-color: var(--quest-gold);
  box-shadow: 0 6px 20px rgba(5, 10, 22, 0.6);
}

.topic-island-card:focus-visible {
  outline: 2px solid var(--quest-gold);
  outline-offset: 3px;
}

.topic-island-card.is-selected {
  border-color: var(--quest-gold);
  box-shadow: 0 0 20px rgba(217, 182, 111, 0.25);
}

.card-accent-bar {
  height: 4px;
  width: 100%;
}

.theme-emerald .card-accent-bar {
  background: linear-gradient(90deg, #28745B, #7AE0BF);
}

.theme-gold .card-accent-bar {
  background: linear-gradient(90deg, #D9B66F, #FFE8B8);
}

.theme-violet .card-accent-bar {
  background: linear-gradient(90deg, #9C8AD6, #D4C9FF);
}

.card-inner {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.topic-icon {
  font-size: 26px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
}

.topic-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.topic-naming {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.plain-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--quest-parchment);
  line-height: 1.3;
}

.fantasy-title {
  font-size: 12px;
  color: var(--quest-gold);
  font-style: italic;
  letter-spacing: 0.03em;
}

.standard-pill {
  background: rgba(11, 19, 39, 0.6);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.standard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.standard-code {
  font-size: 11px;
  font-weight: 800;
  color: var(--quest-gold);
  letter-spacing: 0.05em;
}

.verified-badge {
  font-size: 10px;
  color: #7AE0BF;
}

.standard-text {
  font-size: 11px;
  color: var(--quest-parchment-muted);
  line-height: 1.4;
}

.island-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
  color: var(--quest-parchment-muted);
  flex: 1;
}

.island-location {
  color: var(--quest-parchment);
}

.misconception-count {
  color: #D4C9FF;
}

.card-action {
  margin-top: 4px;
}

.btn-select-topic {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(25, 61, 101, 0.4);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-select-topic:hover {
  background: rgba(35, 82, 136, 0.7);
  border-color: var(--quest-gold);
  color: #fff;
}

@media (max-width: 768px) {
  .picker-controls {
    flex-direction: column;
    align-items: flex-start;
  }
  .topics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
