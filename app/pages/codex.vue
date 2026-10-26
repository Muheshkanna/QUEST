<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { onMounted, computed, ref } from 'vue'

const store = useGameStore()

onMounted(() => {
  store.initFromStorage()
})

const student = computed(() => store.student)
const achievements = computed(() => store.achievements)
const activities = computed(() => store.activities)
const masteries = computed(() => store.topicMasteries)

const availableTitles = [
  'Seeker Initiate',
  'Fraction Conjurer',
  'Decimal Knight',
  'Ratio Alchemist',
  'Axiom Scholar',
  'Grand Archmage'
]

function equipTitle(title: string) {
  store.student.equippedTitle = title
  store.awardXp(50, `Equipped Title: "${title}"`)
  store.persistToStorage()
}

const totalMastered = computed(() => masteries.value.filter((m: any) => m.bestScore >= 70).length)
const avgScore = computed(() => {
  if (!masteries.value.length) return 0
  const sum = masteries.value.reduce((acc: number, m: any) => acc + (m.bestScore || 0), 0)
  return Math.round(sum / masteries.value.length)
})
</script>

<template>
  <div class="codex-page">
    <!-- Header -->
    <header class="codex-header">
      <div class="breadcrumb">
        <NuxtLink to="/" class="crumb-link">← Command Center</NuxtLink>
        <span class="sep">/</span>
        <span class="crumb-current">Scholar Codex</span>
      </div>
      <div class="header-titles">
        <h1 class="page-title font-display">📜 Scholar Codex</h1>
        <p class="page-subtitle">The living chronicle of your mathematical progression, learned axioms, and astral credentials.</p>
      </div>
    </header>

    <div class="codex-grid">
      <!-- Left Column: Character Profile & Equippable Titles -->
      <div class="codex-col-profile">
        <div class="profile-card quest-surface-card">
          <div class="profile-hero">
            <div class="avatar-circle">
              <span class="avatar-emoji">{{ student.avatar || '🧙' }}</span>
              <span class="level-badge font-display">{{ student.level }}</span>
            </div>
            <h2 class="student-name font-display">{{ student.name || 'Seeker' }}</h2>
            <p class="equipped-tag">"{{ student.equippedTitle || 'Seeker Initiate' }}"</p>
            <span class="grade-pill">Grade {{ student.grade }} Scholar</span>
          </div>

          <div class="stats-ledger">
            <div class="stat-row">
              <span class="stat-lbl">Cumulative Lore</span>
              <span class="stat-num font-mono text-gold">{{ (student.totalXp || 0).toLocaleString() }} XP</span>
            </div>
            <div class="stat-row">
              <span class="stat-lbl">Astral Sun Streak</span>
              <span class="stat-num font-mono text-emerald">🔥 {{ student.streakDays || 0 }} Days</span>
            </div>
            <div class="stat-row">
              <span class="stat-lbl">Topics Conquered</span>
              <span class="stat-num font-mono">{{ totalMastered }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-lbl">Average Crucible Accuracy</span>
              <span class="stat-num font-mono text-gold">{{ avgScore }}%</span>
            </div>
          </div>

          <!-- Title Attunement -->
          <div class="titles-section">
            <h3 class="section-title font-display">🎖️ Attune Honorific</h3>
            <div class="titles-chips">
              <button
                v-for="t in availableTitles"
                :key="t"
                class="title-chip"
                :class="{ active: student.equippedTitle === t }"
                @click="equipTitle(t)"
              >
                {{ t }}
              </button>
            </div>
          </div>
        </div>

        <!-- Activity Feed -->
        <div class="activity-card quest-surface-card">
          <h3 class="card-title font-display">⚡ Recent Chronicle</h3>
          <div v-if="activities.length" class="activity-feed">
            <div v-for="act in activities" :key="act.id" class="activity-item">
              <span class="activity-bullet"></span>
              <div class="activity-text">
                <p class="activity-desc">{{ act.text }}</p>
                <div class="activity-meta">
                  <span class="xp-gain font-mono">+{{ act.xpGained }} XP</span>
                  <span class="time-stamp">{{ act.timestamp }}</span>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="empty-feed font-body">No recent actions recorded. Complete a crucible in the Realm Map!</p>
        </div>
      </div>

      <!-- Right Column: Curriculum Mastery Matrix & Knowledge Proofs -->
      <div class="codex-col-mastery">
        <div class="mastery-matrix-card quest-surface-card">
          <div class="matrix-header">
            <div>
              <span class="badge badge-gold">Georgia K-12 Standards</span>
              <h2 class="card-title font-display">Curriculum Mastery Matrix</h2>
            </div>
            <NuxtLink to="/map" class="btn-play font-display">Go to Realm Map →</NuxtLink>
          </div>

          <div v-if="masteries.length" class="mastery-list">
            <div v-for="m in masteries" :key="m.topicId" class="mastery-item">
              <div class="topic-info">
                <span class="topic-title font-display">{{ (m.topicId || '').replace(/-/g, ' ').toUpperCase() }}</span>
                <span class="topic-attempts font-mono">{{ m.attempts || 1 }} Crucible Attempts</span>
              </div>
              <div class="mastery-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: `${m.bestScore || 0}%` }"></div>
                </div>
                <span class="score-badge font-mono" :style="{ color: m.bestScore >= 70 ? '#7AE0BF' : '#D9B66F' }">
                  {{ m.bestScore || 0 }}%
                </span>
              </div>
            </div>
          </div>
          <div v-else class="empty-matrix">
            <span class="empty-icon">🗺️</span>
            <h3 class="font-display">No Crucibles Undertaken Yet</h3>
            <p>Enter the Realm Map to study mathematical lessons, complete challenges, and register your mastery proofs in this matrix.</p>
            <NuxtLink to="/map" class="btn-cta font-display">Open Realm Map</NuxtLink>
          </div>
        </div>

        <!-- Trophy Teaser -->
        <div class="trophy-teaser quest-surface-card">
          <div class="teaser-left">
            <span class="trophy-big">🏆</span>
            <div>
              <h3 class="font-display">Vault of Glory</h3>
              <p>You have unlocked <strong>{{ achievements.length }}</strong> trophies in the Hall of Honor.</p>
            </div>
          </div>
          <NuxtLink to="/vault" class="btn-vault font-display">View All Badges →</NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.codex-page {
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
  margin-bottom: 8px;
}
.crumb-link { color: var(--quest-gold); text-decoration: none; }
.crumb-link:hover { text-decoration: underline; }
.crumb-current { color: var(--quest-parchment); font-weight: 600; }

.page-title {
  font-size: 32px;
  color: var(--quest-parchment);
  margin: 0;
  text-shadow: 0 0 12px rgba(217, 182, 111, 0.3);
}
.page-subtitle {
  color: var(--quest-parchment-muted);
  margin-top: 6px;
  font-size: 15px;
}

.codex-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: var(--space-xl);
}
@media (max-width: 900px) {
  .codex-grid { grid-template-columns: 1fr; }
}

.codex-col-profile {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.profile-card, .activity-card, .mastery-matrix-card, .trophy-teaser {
  padding: 24px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-medium);
  background: rgba(16, 27, 53, 0.7);
}

.profile-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(217, 182, 111, 0.25), rgba(25, 61, 101, 0.8));
  border: 2px solid var(--quest-gold);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 12px;
}
.avatar-emoji { font-size: 40px; }
.level-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: var(--quest-gold);
  color: var(--quest-abyss);
  font-weight: 800;
  font-size: 12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--quest-abyss);
}

.student-name {
  font-size: 22px;
  color: var(--quest-gold);
  margin: 0;
}
.equipped-tag {
  color: #7AE0BF;
  font-size: 13px;
  font-style: italic;
  margin: 4px 0 8px;
}
.grade-pill {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 3px 10px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  color: var(--quest-parchment-muted);
}

.stats-ledger {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-subtle);
}
.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.stat-lbl { color: var(--quest-parchment-muted); }

.titles-section {
  padding-top: 16px;
}
.section-title {
  font-size: 14px;
  color: var(--quest-parchment);
  margin-bottom: 10px;
}
.titles-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.title-chip {
  background: rgba(25, 61, 101, 0.4);
  border: 1px solid var(--border-subtle);
  color: var(--quest-parchment-muted);
  font-size: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}
.title-chip:hover {
  border-color: var(--quest-gold);
  color: var(--quest-parchment);
}
.title-chip.active {
  background: rgba(217, 182, 111, 0.2);
  border-color: var(--quest-gold);
  color: var(--quest-gold);
  font-weight: 600;
}

/* Activity */
.card-title {
  font-size: 18px;
  color: var(--quest-gold);
  margin-bottom: 16px;
}
.activity-feed {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.activity-bullet {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--quest-gold);
  margin-top: 6px;
  flex-shrink: 0;
}
.activity-text { flex: 1; }
.activity-desc { font-size: 13px; color: var(--quest-parchment); margin: 0; }
.activity-meta { display: flex; gap: 8px; font-size: 11px; margin-top: 4px; }
.xp-gain { color: #7AE0BF; }
.time-stamp { color: var(--quest-parchment-muted); }
.empty-feed { font-size: 13px; color: var(--quest-parchment-muted); font-style: italic; }

/* Right Column */
.codex-col-mastery {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.matrix-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.btn-play {
  background: rgba(217, 182, 111, 0.15);
  border: 1px solid var(--quest-gold);
  color: var(--quest-gold);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.2s ease;
}
.btn-play:hover {
  background: var(--quest-gold);
  color: var(--quest-abyss);
}

.mastery-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.mastery-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
  background: rgba(25, 61, 101, 0.3);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}
.topic-info { display: flex; flex-direction: column; }
.topic-title { font-size: 14px; color: var(--quest-parchment); }
.topic-attempts { font-size: 11px; color: var(--quest-parchment-muted); }

.mastery-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 180px;
}
.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 999px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #D9B66F, #7AE0BF);
  border-radius: 999px;
}
.score-badge { font-size: 13px; font-weight: 700; width: 45px; text-align: right; }

.empty-matrix {
  text-align: center;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.empty-icon { font-size: 44px; }
.empty-matrix h3 { color: var(--quest-gold); margin: 0; }
.empty-matrix p { color: var(--quest-parchment-muted); max-width: 440px; font-size: 14px; }
.btn-cta {
  margin-top: 8px;
  background: linear-gradient(135deg, #D9B66F, #B8964F);
  color: var(--quest-abyss);
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  font-weight: 700;
  font-size: 14px;
}

.trophy-teaser {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.teaser-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.trophy-big { font-size: 36px; }
.trophy-teaser h3 { margin: 0 0 4px; color: var(--quest-gold); }
.trophy-teaser p { margin: 0; font-size: 13px; color: var(--quest-parchment-muted); }
.btn-vault {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border-medium);
  color: var(--quest-parchment);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  font-size: 13px;
  white-space: nowrap;
  transition: all 0.2s ease;
}
.btn-vault:hover {
  background: rgba(217, 182, 111, 0.2);
  border-color: var(--quest-gold);
  color: var(--quest-gold);
}

@media (max-width: 640px) {
  .codex-page {
    padding: var(--space-md) var(--space-sm);
    gap: var(--space-lg);
  }
  .page-title {
    font-size: 24px;
  }
  .profile-card, .activity-card, .mastery-matrix-card, .trophy-teaser {
    padding: 16px;
  }
  .trophy-teaser {
    flex-direction: column;
    align-items: flex-start;
  }
  .btn-vault {
    width: 100%;
    text-align: center;
  }
}
</style>
