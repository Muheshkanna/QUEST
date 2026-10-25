<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const store = useGameStore()
const router = useRouter()

const showOnboarding = ref(false)
const nickname = ref('')
const chosenGrade = ref<5 | 6>(5)

onMounted(() => {
  store.initFromStorage()
  // Show onboarding only for brand-new players (no name set)
  if (!store.student?.name) {
    showOnboarding.value = true
  }
})

function startAdventure() {
  if (!nickname.value.trim()) return
  store.student.name = nickname.value.trim()
  store.student.grade = chosenGrade.value
  store.persistToStorage()
  showOnboarding.value = false
  router.push('/map')
}

const xpPct = computed(() => {
  const cur = store.student?.currentXp ?? 0
  const next = store.student?.xpToNextLevel ?? 1000
  return Math.min(100, Math.round((cur / next) * 100))
})
</script>

<template>
  <div class="home-page">
    <!-- Onboarding modal -->
    <transition name="fade">
      <div v-if="showOnboarding" class="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
        <div class="onboarding-card quest-surface-card">
          <div class="onboarding-crest" aria-hidden="true">⚔️</div>
          <h1 id="onboarding-title" class="onboarding-title font-display">Welcome, Seeker</h1>
          <p class="onboarding-sub">Choose your grade and enter your name to begin the Math Quest.</p>

          <div class="grade-pick">
            <button
              v-for="g in [5, 6]" :key="g"
              class="grade-pick-btn"
              :class="{ active: chosenGrade === g }"
              @click="chosenGrade = g as 5|6"
            >Grade {{ g }}</button>
          </div>

          <div class="name-row">
            <label for="nickname-input" class="name-label">Your name</label>
            <input
              id="nickname-input"
              v-model="nickname"
              class="name-input"
              type="text"
              maxlength="24"
              placeholder="e.g. Aria"
              @keydown.enter="startAdventure"
              autocomplete="off"
            />
          </div>

          <button
            class="btn-start font-display"
            :disabled="!nickname.trim()"
            @click="startAdventure"
          >Begin Your Quest →</button>
        </div>
      </div>
    </transition>

    <!-- Main command center when onboarding done -->
    <div v-if="!showOnboarding" class="command-center">
      <div class="hero-block">
        <h1 class="hero-title font-display">Welcome back, <span class="hero-name">{{ store.student?.name || 'Seeker' }}</span></h1>
        <p class="hero-sub">Level {{ store.student?.level ?? 1 }} · {{ store.student?.totalXp ?? 0 }} XP · Grade {{ store.student?.grade ?? 5 }}</p>
        <div class="xp-bar-wrap">
          <div class="xp-bar">
            <div class="xp-fill" :style="{ width: xpPct + '%' }"></div>
          </div>
          <span class="xp-label font-mono">{{ store.student?.currentXp ?? 0 }} / {{ store.student?.xpToNextLevel ?? 1000 }} XP</span>
        </div>
      </div>

      <div class="quick-actions">
        <NuxtLink to="/map" class="action-card action-primary">
          <span class="action-icon">🗺️</span>
          <div class="action-body">
            <span class="action-title font-display">Realm Map</span>
            <span class="action-desc">Choose a topic and battle</span>
          </div>
          <span class="action-arrow">→</span>
        </NuxtLink>

        <div v-if="store.topicMasteries?.length" class="recent-section">
          <h2 class="section-title font-display">Recent Battles</h2>
          <div class="recent-list">
            <NuxtLink
              v-for="m in store.topicMasteries.slice(-4).reverse()"
              :key="m.topicId"
              :to="`/lesson/${m.topicId}`"
              class="recent-item"
            >
              <span class="recent-name">{{ m.topicId.replace(/-/g, ' ') }}</span>
              <span class="recent-score font-mono" :style="{ color: m.bestScore >= 70 ? '#7AE0BF' : '#D9B66F' }">{{ m.bestScore }}%</span>
            </NuxtLink>
          </div>
        </div>

        <div v-else class="empty-state">
          <span class="empty-icon">🌟</span>
          <p class="empty-text">No battles yet — head to the Realm Map to start!</p>
          <NuxtLink to="/map" class="btn-cta font-display">Choose a Topic</NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page { min-height: 100vh; padding: var(--space-xl) var(--space-lg); }

/* Onboarding */
.onboarding-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 10, 22, 0.92);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--space-lg);
}
.onboarding-card {
  width: 100%;
  max-width: 440px;
  padding: 44px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 22px;
  border-radius: var(--radius-md);
  text-align: center;
}
.onboarding-crest { font-size: 52px; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
.onboarding-title { font-size: 28px; color: var(--quest-parchment); }
.onboarding-sub { font-size: 14px; color: var(--quest-parchment-muted); max-width: 320px; line-height: 1.55; }
.grade-pick { display: flex; gap: 10px; }
.grade-pick-btn {
  padding: 10px 28px;
  border-radius: 999px;
  border: 1px solid var(--border-medium);
  background: transparent;
  color: var(--quest-parchment-muted);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.grade-pick-btn.active { background: rgba(217,182,111,0.15); border-color: var(--quest-gold); color: var(--quest-gold); }
.name-row { width: 100%; display: flex; flex-direction: column; gap: 6px; text-align: left; }
.name-label { font-size: 12px; color: var(--quest-gold); text-transform: uppercase; letter-spacing: 0.06em; }
.name-input {
  width: 100%;
  padding: 12px 14px;
  background: rgba(11,19,39,0.8);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment);
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.name-input:focus { border-color: var(--quest-gold); }
.btn-start {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #D9B66F, #B8922A);
  border: none;
  border-radius: var(--radius-sm);
  color: #0B1327;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-start:disabled { opacity: 0.45; cursor: not-allowed; }
.btn-start:not(:disabled):hover { opacity: 0.88; }

/* Command center */
.command-center { max-width: 700px; margin: 0 auto; display: flex; flex-direction: column; gap: var(--space-xl); }
.hero-block { display: flex; flex-direction: column; gap: 10px; }
.hero-title { font-size: 32px; color: var(--quest-parchment); }
.hero-name { color: var(--quest-gold); }
.hero-sub { font-size: 14px; color: var(--quest-parchment-muted); }
.xp-bar-wrap { display: flex; align-items: center; gap: 12px; }
.xp-bar { flex: 1; height: 10px; background: var(--quest-abyss); border-radius: 999px; overflow: hidden; border: 1px solid var(--border-subtle); }
.xp-fill { height: 100%; background: linear-gradient(90deg, #D9B66F, #FFE8B8); border-radius: 999px; transition: width 0.5s ease; }
.xp-label { font-size: 12px; color: var(--quest-parchment-muted); white-space: nowrap; }

.quick-actions { display: flex; flex-direction: column; gap: 16px; }
.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(25,61,101,0.4);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--quest-parchment);
  transition: all 0.2s;
}
.action-card:hover { border-color: var(--quest-gold); background: rgba(217,182,111,0.08); transform: translateY(-1px); }
.action-primary { border-color: var(--quest-gold); }
.action-icon { font-size: 32px; }
.action-body { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.action-title { font-size: 18px; }
.action-desc { font-size: 13px; color: var(--quest-parchment-muted); }
.action-arrow { font-size: 18px; color: var(--quest-gold); }

.section-title { font-size: 16px; color: var(--quest-parchment); margin-bottom: 8px; }
.recent-list { display: flex; flex-direction: column; gap: 8px; }
.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: rgba(25,61,101,0.3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--quest-parchment);
  font-size: 14px;
  transition: border-color 0.2s;
}
.recent-item:hover { border-color: var(--quest-gold); }
.recent-score { font-size: 13px; }

.empty-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 40px; text-align: center; border: 1px dashed var(--border-subtle); border-radius: var(--radius-md); }
.empty-icon { font-size: 40px; }
.empty-text { font-size: 14px; color: var(--quest-parchment-muted); }
.btn-cta { padding: 12px 28px; background: linear-gradient(135deg, #D9B66F, #B8922A); border: none; border-radius: var(--radius-sm); color: #0B1327; font-size: 14px; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-block; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.4s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
