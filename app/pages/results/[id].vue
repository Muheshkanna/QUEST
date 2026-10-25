<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const store = useGameStore()
const route = useRoute()
const router = useRouter()
const topicId = route.params.id as string

const score = computed(() => store.quiz.score)
const total = computed(() => store.quiz.questions.length * 10)
const pct = computed(() => total.value ? Math.round((score.value / total.value) * 100) : 0)

const earnedBadges = computed(() =>
  store.achievements.filter((a: any) => {
    const ts = a.unlockedAt
    if (!ts) return false
    return Date.now() - new Date(ts).getTime() < 120_000 // earned in last 2 min
  })
)

const BADGE_DEFS: Record<string, { label: string; icon: string; desc: string }> = {
  'first-quest':    { label: 'First Quest',      icon: '⚔️', desc: 'Completed your first battle!' },
  'perfect-score':  { label: 'Flawless Victory', icon: '🏆', desc: 'Scored 100% on a quiz!' },
  'fraction-master':{ label: 'Fraction Master',  icon: '🧪', desc: 'Conquered a fractions topic.' },
  'scholar':        { label: 'Scholar',           icon: '📜', desc: 'Answered more than half correctly.' },
  'veteran':        { label: 'Veteran',           icon: '🛡️', desc: 'Completed 5 quizzes!' },
  'completionist':  { label: 'Completionist',     icon: '🌟', desc: 'Mastered 10+ topics!' },
}

const rankLabel = computed(() => {
  if (pct.value >= 90) return 'Grand Archmage'
  if (pct.value >= 70) return 'Scholar Knight'
  if (pct.value >= 50) return 'Apprentice'
  return 'Initiate'
})

const rankColor = computed(() => {
  if (pct.value >= 90) return '#D9B66F'
  if (pct.value >= 70) return '#7AE0BF'
  if (pct.value >= 50) return '#9C8AD6'
  return '#aaa'
})

function goMap() { router.push('/map') }
function retry() { router.push(`/quiz/${topicId}`) }
</script>

<template>
  <div class="results-page">
    <div class="results-card quest-surface-card">
      <!-- Header -->
      <div class="results-header">
        <div class="trophy-anim">🏆</div>
        <h1 class="results-title font-display">Quest Complete!</h1>
        <p class="results-subtitle">{{ topicId.replace(/-/g, ' ').replace(/^g\d-/i, '').toUpperCase() }}</p>
      </div>

      <!-- Score ring -->
      <div class="score-ring-wrap">
        <svg class="score-ring" viewBox="0 0 120 120" width="160" height="160">
          <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
          <circle
            cx="60" cy="60" r="52" fill="none"
            :stroke="rankColor" stroke-width="10"
            stroke-linecap="round"
            :stroke-dasharray="`${pct * 3.267} 326.7`"
            transform="rotate(-90 60 60)"
            style="transition: stroke-dasharray 1s ease"
          />
        </svg>
        <div class="score-center">
          <span class="score-pct font-display" :style="{ color: rankColor }">{{ pct }}%</span>
          <span class="score-raw font-mono">{{ score }}/{{ total }}</span>
        </div>
      </div>

      <!-- Rank -->
      <div class="rank-badge" :style="{ borderColor: rankColor, color: rankColor }">
        {{ rankLabel }}
      </div>

      <!-- New badges -->
      <div v-if="earnedBadges.length" class="badges-section">
        <h2 class="badges-heading font-display">New Badges Earned</h2>
        <div class="badges-row">
          <div v-for="badge in earnedBadges" :key="badge.id" class="badge-chip">
            <span class="badge-icon">{{ BADGE_DEFS[badge.id]?.icon ?? '🏅' }}</span>
            <div class="badge-info">
              <span class="badge-label font-display">{{ BADGE_DEFS[badge.id]?.label ?? badge.id }}</span>
              <span class="badge-desc">{{ BADGE_DEFS[badge.id]?.desc ?? '' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats row -->
      <div class="stats-row">
        <div class="stat-item">
          <span class="stat-val font-display">{{ store.quiz.questions.length }}</span>
          <span class="stat-label">Questions</span>
        </div>
        <div class="stat-item">
          <span class="stat-val font-display" style="color:#7AE0BF">{{ Math.round(score/10) }}</span>
          <span class="stat-label">Correct</span>
        </div>
        <div class="stat-item">
          <span class="stat-val font-display" style="color:#FF8A8A">{{ store.quiz.questions.length - Math.round(score/10) }}</span>
          <span class="stat-label">Missed</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="results-actions">
        <button class="btn-retry" @click="retry">⚔️ Try Again</button>
        <button class="btn-map" @click="goMap">🗺️ Back to Realm Map</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.results-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl) var(--space-md);
}

.results-card {
  width: 100%;
  max-width: 520px;
  padding: 40px 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
  border-radius: var(--radius-md);
}

.results-header { text-align: center; }
.trophy-anim { font-size: 52px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.08); } }
.results-title { font-size: 30px; color: var(--quest-parchment); margin-top: 8px; }
.results-subtitle { font-size: 12px; letter-spacing: 0.08em; color: var(--quest-parchment-muted); margin-top: 4px; }

/* Score ring */
.score-ring-wrap { position: relative; width: 160px; height: 160px; display: flex; align-items: center; justify-content: center; }
.score-ring { position: absolute; top: 0; left: 0; }
.score-center { display: flex; flex-direction: column; align-items: center; }
.score-pct { font-size: 36px; line-height: 1; }
.score-raw { font-size: 13px; color: var(--quest-parchment-muted); margin-top: 4px; }

/* Rank */
.rank-badge {
  padding: 6px 20px;
  border-radius: 999px;
  border: 1px solid;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.06em;
  background: rgba(255,255,255,0.04);
}

/* Badges */
.badges-section { width: 100%; }
.badges-heading { font-size: 15px; color: var(--quest-gold); margin-bottom: 12px; }
.badges-row { display: flex; flex-direction: column; gap: 10px; }
.badge-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: rgba(217,182,111,0.08);
  border: 1px solid rgba(217,182,111,0.3);
  border-radius: var(--radius-sm);
}
.badge-icon { font-size: 24px; }
.badge-info { display: flex; flex-direction: column; }
.badge-label { font-size: 14px; color: var(--quest-gold); }
.badge-desc { font-size: 12px; color: var(--quest-parchment-muted); }

/* Stats */
.stats-row { display: flex; gap: 24px; justify-content: center; width: 100%; }
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.stat-val { font-size: 28px; color: var(--quest-parchment); }
.stat-label { font-size: 12px; color: var(--quest-parchment-muted); text-transform: uppercase; letter-spacing: 0.05em; }

/* Actions */
.results-actions { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; width: 100%; }
.btn-retry {
  padding: 12px 24px;
  border: 1px solid var(--border-medium);
  background: rgba(25,61,101,0.5);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-retry:hover { border-color: var(--quest-gold); }
.btn-map {
  padding: 12px 24px;
  background: linear-gradient(135deg, #D9B66F, #B8922A);
  border: none;
  border-radius: var(--radius-sm);
  color: #0B1327;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-map:hover { opacity: 0.88; }
</style>
