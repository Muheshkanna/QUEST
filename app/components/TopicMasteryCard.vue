<script setup lang="ts">
import type { TopicMastery } from '~/types/quest'

const props = defineProps<{
  masteries: TopicMastery[]
}>()

const getTierBadge = (tier: string) => {
  switch (tier) {
    case 'Paragon': return 'badge-gold'
    case 'Master': return 'badge-emerald'
    case 'Adept': return 'badge-violet'
    default: return 'badge-common'
  }
}
</script>

<template>
  <div class="mastery-card quest-surface-card">
    <div class="card-header">
      <div class="header-titles">
        <span class="badge badge-emerald">Discipline Proficiency</span>
        <h3 class="card-title font-display">Topic Mastery Matrix</h3>
      </div>
      <span class="mastery-count font-mono">{{ masteries.length }} Disciplines</span>
    </div>

    <div class="mastery-list">
      <div v-for="item in masteries" :key="item.id" class="mastery-row">
        <div class="mastery-meta">
          <div class="meta-top">
            <span class="topic-name font-body">{{ item.name }}</span>
            <span class="badge" :class="getTierBadge(item.tier)">{{ item.tier }}</span>
          </div>
          <div class="meta-bottom">
            <span class="spark-count">✨ {{ item.sparkCount }} Glyphs Attuned</span>
            <span class="percent-val font-mono">{{ item.masteryLevel }}%</span>
          </div>
        </div>

        <div class="progress-bar-wrap" role="progressbar" :aria-valuenow="item.masteryLevel" :aria-valuemin="0" :aria-valuemax="100">
          <div 
            class="progress-fill-bar" 
            :style="{ 
              width: `${item.masteryLevel}%`,
              background: item.masteryLevel > 80 ? 'linear-gradient(90deg, #28745B, #7AE0BF)' : 'linear-gradient(90deg, #9C8AD6, #D9B66F)'
            }" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mastery-card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  background: rgba(25, 61, 101, 0.45);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-size: 17px;
  color: var(--quest-parchment);
}

.mastery-count {
  font-size: 11px;
  color: var(--quest-parchment-muted);
}

.mastery-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mastery-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: rgba(11, 19, 39, 0.4);
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.mastery-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.topic-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--quest-parchment);
}

.meta-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: var(--quest-parchment-muted);
}

.percent-val {
  font-weight: 700;
  color: var(--quest-gold);
}

.progress-bar-wrap {
  height: 6px;
  background: var(--quest-abyss);
  border-radius: var(--radius-full);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
}

.progress-fill-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}
</style>
