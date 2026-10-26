<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { onMounted, computed, ref } from 'vue'

const store = useGameStore()

onMounted(() => {
  store.initFromStorage()
})

const ALL_TROPHIES = [
  {
    id: 'first-quest',
    title: 'First Quest',
    icon: '⚔️',
    rarity: 'Common',
    desc: 'Brave the arcane crucibles and complete your very first math battle.',
    lore: 'The initial step into the realm of mathematical mysteries.',
    howTo: 'Complete any quiz crucible in the Realm Map.'
  },
  {
    id: 'perfect-score',
    title: 'Flawless Victory',
    icon: '🏆',
    rarity: 'Legendary',
    desc: 'Score 100% on a battle crucible with zero arithmetic failures.',
    lore: 'An exhibition of pure, unblemished logical precision.',
    howTo: 'Answer every question in a battle correctly (100 PTS).'
  },
  {
    id: 'fraction-master',
    title: 'Fraction Master',
    icon: '🧪',
    rarity: 'Epic',
    desc: 'Unravel the mysteries of rational numbers in the Enchanted Forest.',
    lore: 'Mastery over the sacred balance of numerators and denominators.',
    howTo: 'Conquer any Fractions topic (Addition or Multiplication).'
  },
  {
    id: 'scholar',
    title: 'Scholar Knight',
    icon: '📜',
    rarity: 'Rare',
    desc: 'Demonstrate deep conceptual mastery with a score above 50%.',
    lore: 'Recognized by the Council of Axioms for disciplined study.',
    howTo: 'Score at least 50% in any battle crucible.'
  },
  {
    id: 'veteran',
    title: 'Grand Veteran',
    icon: '🛡️',
    rarity: 'Epic',
    desc: 'Complete 5 or more battle crucibles across any sacred realm.',
    lore: 'A hardened defender of the mathematical order.',
    howTo: 'Engage and finish 5 different topic challenges.'
  },
  {
    id: 'completionist',
    title: 'Master Completionist',
    icon: '🌟',
    rarity: 'Legendary',
    desc: 'Attain high mastery across 10 or more Georgia Mathematics Standards.',
    lore: 'Attuned to all frequencies of whole number, decimal, and rational law.',
    howTo: 'Master at least 10 curriculum topics.'
  }
]

const filter = ref<'all' | 'unlocked' | 'locked'>('all')

const unlockedMap = computed(() => {
  const map: Record<string, any> = {}
  for (const a of store.achievements || []) {
    map[a.id] = a
  }
  return map
})

const filteredTrophies = computed(() => {
  return ALL_TROPHIES.filter(t => {
    const isUnlocked = Boolean(unlockedMap.value[t.id])
    if (filter.value === 'unlocked') return isUnlocked
    if (filter.value === 'locked') return !isUnlocked
    return true
  })
})

const unlockedCount = computed(() => {
  return ALL_TROPHIES.filter(t => Boolean(unlockedMap.value[t.id])).length
})

const completionPct = computed(() => {
  return Math.round((unlockedCount.value / ALL_TROPHIES.length) * 100)
})

function getRarityBadgeClass(rarity: string) {
  switch (rarity) {
    case 'Legendary': return 'badge-gold'
    case 'Epic': return 'badge-violet'
    case 'Rare': return 'badge-emerald'
    default: return 'badge-common'
  }
}
</script>

<template>
  <div class="vault-page">
    <!-- Header -->
    <header class="vault-header">
      <div class="breadcrumb">
        <NuxtLink to="/" class="crumb-link">← Command Center</NuxtLink>
        <span class="sep">/</span>
        <span class="crumb-current">Vault of Glory</span>
      </div>

      <div class="header-banner quest-surface-card">
        <div class="banner-left">
          <span class="vault-crest-icon">🏆</span>
          <div>
            <span class="badge badge-gold">Hall of Arcane Honors</span>
            <h1 class="page-title font-display">Vault of Glory</h1>
            <p class="page-subtitle">Examine your earned relics, badges, and honors inscribed into eternity.</p>
          </div>
        </div>

        <div class="banner-metrics">
          <div class="metric-box">
            <span class="metric-val font-display">{{ unlockedCount }} / {{ ALL_TROPHIES.length }}</span>
            <span class="metric-lbl">Trophies Unlocked</span>
          </div>
          <div class="metric-progress-track">
            <div class="metric-progress-fill" :style="{ width: `${completionPct}%` }"></div>
          </div>
          <span class="metric-pct font-mono">{{ completionPct }}% Complete</span>
        </div>
      </div>
    </header>

    <!-- Filters -->
    <div class="filter-bar">
      <div class="filter-tabs">
        <button
          class="filter-tab"
          :class="{ active: filter === 'all' }"
          @click="filter = 'all'"
        >
          All Trophies ({{ ALL_TROPHIES.length }})
        </button>
        <button
          class="filter-tab"
          :class="{ active: filter === 'unlocked' }"
          @click="filter = 'unlocked'"
        >
          ✨ Unlocked ({{ unlockedCount }})
        </button>
        <button
          class="filter-tab"
          :class="{ active: filter === 'locked' }"
          @click="filter = 'locked'"
        >
          🔒 Locked ({{ ALL_TROPHIES.length - unlockedCount }})
        </button>
      </div>

      <NuxtLink to="/map" class="btn-earn-more font-display">
        ⚔️ Enter Battle to Unlock More
      </NuxtLink>
    </div>

    <!-- Trophies Grid -->
    <div class="trophies-grid">
      <div
        v-for="trophy in filteredTrophies"
        :key="trophy.id"
        class="trophy-card quest-surface-card"
        :class="{
          'is-unlocked': Boolean(unlockedMap[trophy.id]),
          'is-locked': !unlockedMap[trophy.id],
          [`rarity-${trophy.rarity.toLowerCase()}`]: true
        }"
      >
        <div class="trophy-ambient-glow" />

        <div class="trophy-top">
          <div class="trophy-icon-frame">
            <span class="trophy-icon">{{ trophy.icon }}</span>
            <span v-if="!unlockedMap[trophy.id]" class="lock-overlay">🔒</span>
          </div>
          <div class="trophy-title-col">
            <div class="badge-row">
              <span class="badge" :class="getRarityBadgeClass(trophy.rarity)">{{ trophy.rarity }}</span>
              <span v-if="unlockedMap[trophy.id]" class="unlocked-tag font-mono">UNLOCKED</span>
            </div>
            <h3 class="trophy-name font-display">{{ trophy.title }}</h3>
          </div>
        </div>

        <p class="trophy-desc">{{ trophy.desc }}</p>
        <p class="trophy-lore">"{{ trophy.lore }}"</p>

        <div class="trophy-footer">
          <div v-if="unlockedMap[trophy.id]" class="unlocked-details">
            <span class="sparkle">✨</span>
            <span class="unlocked-ts">Unlocked in battle</span>
          </div>
          <div v-else class="how-to-unlock">
            <span class="req-label">Requirement:</span>
            <span class="req-text">{{ trophy.howTo }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.vault-page {
  min-height: 100vh;
  padding: var(--space-xl) var(--space-lg);
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--quest-parchment-muted);
  margin-bottom: 12px;
}
.crumb-link { color: var(--quest-gold); text-decoration: none; }
.crumb-link:hover { text-decoration: underline; }
.crumb-current { color: var(--quest-parchment); font-weight: 600; }

.header-banner {
  padding: 28px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-medium);
  background: radial-gradient(circle at top right, rgba(217, 182, 111, 0.15), rgba(16, 27, 53, 0.85));
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}
.banner-left {
  display: flex;
  align-items: center;
  gap: 20px;
}
.vault-crest-icon { font-size: 54px; filter: drop-shadow(0 0 16px rgba(217, 182, 111, 0.4)); }
.page-title {
  font-size: 32px;
  color: var(--quest-gold);
  margin: 4px 0;
  text-shadow: 0 0 12px rgba(217, 182, 111, 0.4);
}
.page-subtitle { color: var(--quest-parchment-muted); margin: 0; font-size: 14px; }

.banner-metrics {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 200px;
}
.metric-val { font-size: 26px; color: var(--quest-parchment); font-weight: 800; }
.metric-lbl { font-size: 12px; color: var(--quest-parchment-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.metric-progress-track {
  width: 100%;
  height: 8px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 999px;
  overflow: hidden;
  margin: 8px 0 4px;
}
.metric-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #D9B66F, #7AE0BF);
  border-radius: 999px;
  transition: width 0.4s ease;
}
.metric-pct { font-size: 12px; color: #7AE0BF; }

/* Filter Bar */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}
.filter-tabs {
  display: flex;
  gap: 8px;
  background: rgba(16, 27, 53, 0.6);
  padding: 4px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}
.filter-tab {
  background: transparent;
  border: none;
  color: var(--quest-parchment-muted);
  font-size: 13px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-tab:hover { color: var(--quest-parchment); }
.filter-tab.active {
  background: rgba(25, 61, 101, 0.8);
  color: var(--quest-gold);
}
.btn-earn-more {
  background: linear-gradient(135deg, rgba(217, 182, 111, 0.2), rgba(25, 61, 101, 0.8));
  border: 1px solid var(--quest-gold);
  color: var(--quest-gold);
  padding: 8px 18px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  transition: all 0.2s ease;
}
.btn-earn-more:hover {
  background: var(--quest-gold);
  color: var(--quest-abyss);
  transform: translateY(-1px);
}

/* Grid */
.trophies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.trophy-card {
  padding: 24px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-medium);
  background: rgba(16, 27, 53, 0.6);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: all 0.25s ease;
}

.trophy-card.is-unlocked {
  border-color: rgba(217, 182, 111, 0.5);
  background: radial-gradient(circle at top left, rgba(217, 182, 111, 0.12), rgba(16, 27, 53, 0.75));
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.trophy-card.is-locked {
  opacity: 0.65;
  filter: grayscale(0.3);
}
.trophy-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}
.trophy-card.is-unlocked:hover {
  border-color: var(--quest-gold);
}

.trophy-top {
  display: flex;
  align-items: center;
  gap: 16px;
}
.trophy-icon-frame {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(25, 61, 101, 0.6);
  border: 2px solid var(--border-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}
.is-unlocked .trophy-icon-frame {
  border-color: var(--quest-gold);
  box-shadow: 0 0 12px rgba(217, 182, 111, 0.3);
}
.trophy-icon { font-size: 28px; }
.lock-overlay {
  position: absolute;
  bottom: -4px;
  right: -4px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.75);
  border-radius: 50%;
  padding: 2px;
}

.trophy-title-col { flex: 1; }
.badge-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.unlocked-tag {
  font-size: 10px;
  color: #7AE0BF;
  font-weight: 700;
  letter-spacing: 0.08em;
}
.trophy-name {
  font-size: 18px;
  color: var(--quest-parchment);
  margin: 0;
}

.trophy-desc {
  font-size: 14px;
  color: var(--quest-parchment);
  line-height: 1.45;
  margin: 0;
}
.trophy-lore {
  font-size: 12px;
  color: var(--quest-parchment-muted);
  font-style: italic;
  margin: 0;
}

.trophy-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
  font-size: 12px;
}
.unlocked-details {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #7AE0BF;
}
.how-to-unlock {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.req-label { color: var(--quest-gold); font-weight: 700; font-size: 11px; text-transform: uppercase; }
.req-text { color: var(--quest-parchment-muted); }

@media (max-width: 640px) {
  .vault-page {
    padding: var(--space-md) var(--space-sm);
    gap: var(--space-lg);
  }
  .header-banner {
    padding: 18px 16px;
    gap: 16px;
  }
  .banner-left {
    gap: 12px;
  }
  .page-title {
    font-size: 24px;
  }
  .trophies-grid {
    grid-template-columns: 1fr;
  }
}
</style>
