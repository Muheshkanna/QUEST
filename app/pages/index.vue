<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const store = useGameStore()
const router = useRouter()

const showOnboarding = ref(false)
const nickname = ref('')
const password = ref('')
const chosenGrade = ref<5 | 6>(5)
const authMode = ref<'signin' | 'register'>('signin')
const existingUserFound = ref<any | null>(null)
const isCheckingDb = ref(false)
const errorMessage = ref<string | null>(null)
const isSubmitting = ref(false)

onMounted(() => {
  store.initFromStorage()
  // Show onboarding only for brand-new players (no name set)
  if (!store.student?.name) {
    showOnboarding.value = true
  }
})

// Debounced lookup against SQLite database to detect returning scholar
let checkTimeout: any = null
watch(nickname, (val) => {
  clearTimeout(checkTimeout)
  errorMessage.value = null
  const trimmed = val.trim()
  if (!trimmed) {
    existingUserFound.value = null
    return
  }
  checkTimeout = setTimeout(async () => {
    isCheckingDb.value = true
    try {
      const res = await fetch(`/api/user?name=${encodeURIComponent(trimmed)}`)
      if (res.ok) {
        const data = await res.json()
        if (data.exists && data.user) {
          existingUserFound.value = data.user
          chosenGrade.value = data.user.grade as 5 | 6
          authMode.value = 'signin'
        } else {
          existingUserFound.value = null
          authMode.value = 'register'
        }
      }
    } catch {
      existingUserFound.value = null
    } finally {
      isCheckingDb.value = false
    }
  }, 250)
})

async function submitAuth() {
  const name = nickname.value.trim()
  const pwd = password.value.trim()
  errorMessage.value = null

  if (!name) {
    errorMessage.value = 'Please enter your scholar name.'
    return
  }
  if (!pwd) {
    errorMessage.value = 'Please enter your password to continue.'
    return
  }
  if (authMode.value === 'register' && pwd.length < 3) {
    errorMessage.value = 'Password must be at least 3 characters long.'
    return
  }

  isSubmitting.value = true
  try {
    if (authMode.value === 'signin') {
      const res = await store.loginUser(name, pwd)
      if (res.success) {
        showOnboarding.value = false
        password.value = ''
        router.push('/map')
      } else {
        errorMessage.value = res.error || 'Incorrect password for this scholar account.'
      }
    } else {
      const res = await store.registerUser(name, pwd, chosenGrade.value)
      if (res.success) {
        showOnboarding.value = false
        password.value = ''
        router.push('/map')
      } else {
        errorMessage.value = res.error || 'Failed to create account.'
      }
    }
  } catch (err: any) {
    errorMessage.value = err.message || 'Authentication error.'
  } finally {
    isSubmitting.value = false
  }
}

function openSwitchScholar() {
  nickname.value = ''
  password.value = ''
  errorMessage.value = null
  existingUserFound.value = null
  authMode.value = 'signin'
  showOnboarding.value = true
}

const xpPct = computed(() => {
  const cur = store.student?.currentXp ?? 0
  const next = store.student?.xpToNextLevel ?? 1000
  return Math.min(100, Math.round((cur / next) * 100))
})
</script>

<template>
  <div class="home-page">
    <!-- Onboarding / Login modal -->
    <transition name="fade">
      <div v-if="showOnboarding" class="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
        <div class="onboarding-card quest-surface-card">
          <div class="onboarding-crest" aria-hidden="true">🛡️</div>
          <h1 id="onboarding-title" class="onboarding-title font-display">
            {{ authMode === 'signin' ? 'Scholar Sign In' : 'Create Scholar Account' }}
          </h1>
          <p class="onboarding-sub">
            {{ authMode === 'signin' 
               ? 'Enter your name and password to retrieve your saved Grade, XP, and badges.' 
               : 'Set a unique scholar name and password to protect your account and save your progress.' }}
          </p>

          <!-- Auth mode toggle tabs -->
          <div class="auth-tabs">
            <button
              type="button"
              class="auth-tab"
              :class="{ active: authMode === 'signin' }"
              @click="authMode = 'signin'; errorMessage = null"
            >
              🔑 Sign In
            </button>
            <button
              type="button"
              class="auth-tab"
              :class="{ active: authMode === 'register' }"
              @click="authMode = 'register'; errorMessage = null"
            >
              ✨ Create Account
            </button>
          </div>

          <!-- Error Alert Banner -->
          <div v-if="errorMessage" class="auth-error-banner" role="alert">
            <span class="error-icon">⚠️</span>
            <span class="error-text">{{ errorMessage }}</span>
          </div>

          <!-- Returning scholar database banner -->
          <div v-if="existingUserFound && authMode === 'signin'" class="existing-user-banner">
            <span class="user-badge font-display">✨ Account Found in Database!</span>
            <p class="user-status-text">
              Welcome back, <strong>{{ existingUserFound.name }}</strong>! We found your saved journey in <strong>Grade {{ existingUserFound.grade }}</strong> (Level {{ existingUserFound.level }}, {{ (existingUserFound.totalXp || 0).toLocaleString() }} XP).
            </p>
          </div>

          <div class="name-row">
            <label for="nickname-input" class="name-label">
              Scholar Name
              <span v-if="isCheckingDb" class="checking-indicator font-mono">Checking database…</span>
            </label>
            <input
              id="nickname-input"
              v-model="nickname"
              class="name-input"
              type="text"
              maxlength="24"
              placeholder="e.g. Kanna, Aria"
              autocomplete="username"
              @keydown.enter="submitAuth"
            />
          </div>

          <div class="name-row">
            <label for="password-input" class="name-label">
              {{ authMode === 'signin' ? 'Account Password' : 'Create Password' }}
            </label>
            <input
              id="password-input"
              v-model="password"
              class="name-input"
              type="password"
              maxlength="32"
              :placeholder="authMode === 'signin' ? 'Enter your password' : 'Create a password (min 3 chars)'"
              autocomplete="current-password"
              @keydown.enter="submitAuth"
            />
          </div>

          <div v-if="authMode === 'register'" class="grade-pick">
            <span class="grade-label">Select Grade Curriculum:</span>
            <div class="grade-btns">
              <button
                v-for="g in [5, 6]" :key="g"
                class="grade-pick-btn"
                :class="{ active: chosenGrade === g }"
                @click="chosenGrade = g as 5|6"
                type="button"
              >Grade {{ g }}</button>
            </div>
          </div>

          <button
            class="btn-start font-display"
            :disabled="!nickname.trim() || !password.trim() || isSubmitting"
            @click="submitAuth"
          >
            <span v-if="isSubmitting">Authenticating…</span>
            <span v-else>{{ authMode === 'signin' ? 'Unlock & Resume Saved Quest →' : 'Create Account & Begin Quest →' }}</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- Main command center when onboarding done -->
    <div v-if="!showOnboarding" class="command-center">
      <div class="hero-block">
        <div class="hero-top-row">
          <div>
            <h1 class="hero-title font-display">Welcome back, <span class="hero-name">{{ store.student?.name || 'Seeker' }}</span></h1>
            <p class="hero-sub">Grade {{ store.student?.grade ?? 5 }} Scholar · Level {{ store.student?.level ?? 1 }} · {{ (store.student?.totalXp ?? 0).toLocaleString() }} XP</p>
          </div>
          <button class="btn-switch-scholar font-display" @click="openSwitchScholar" title="Enter a different name or load another session">
            Switch Scholar 👤
          </button>
        </div>
        <div class="xp-bar-wrap">
          <div class="xp-bar">
            <div class="xp-fill" :style="{ width: xpPct + '%' }"></div>
          </div>
          <span class="xp-label font-mono">{{ store.student?.currentXp ?? 0 }} / {{ store.student?.xpToNextLevel ?? 1000 }} XP</span>
        </div>
      </div>

      <div class="quick-actions">
        <div class="action-cards-grid">
          <NuxtLink to="/map" class="action-card action-primary">
            <span class="action-icon">🗺️</span>
            <div class="action-body">
              <span class="action-title font-display">Realms of Study</span>
              <span class="action-desc">Choose a topic and battle</span>
            </div>
            <span class="action-arrow">→</span>
          </NuxtLink>

          <NuxtLink to="/codex" class="action-card">
            <span class="action-icon">📜</span>
            <div class="action-body">
              <span class="action-title font-display">Scholar Codex</span>
              <span class="action-desc">Profile, titles & mastery</span>
            </div>
            <span class="action-arrow">→</span>
          </NuxtLink>

          <NuxtLink to="/vault" class="action-card">
            <span class="action-icon">🏆</span>
            <div class="action-body">
              <span class="action-title font-display">Vault of Glory</span>
              <span class="action-desc">Trophies & milestones</span>
            </div>
            <span class="action-arrow">→</span>
          </NuxtLink>
        </div>

        <!-- Daily Crucible Card -->
        <div v-if="store.dailyTrial" class="daily-trial-section">
          <DailyTrialCard
            :trial="store.dailyTrial"
            @solve="(idx) => store.submitDailyTrial(idx)"
          />
        </div>

        <div v-if="store.topicMasteries?.length" class="recent-section">
          <h2 class="section-title font-display">Recent Battles</h2>
          <div class="recent-list">
            <NuxtLink
              v-for="m in store.topicMasteries.slice(-4).reverse()"
              :key="m.topicId"
              :to="`/lesson/${m.topicId}`"
              class="recent-item"
            >
              <span class="recent-name">{{ (m.topicId ?? '').replace(/-/g, ' ') }}</span>
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
.onboarding-sub { font-size: 14px; color: var(--quest-parchment-muted); max-width: 340px; line-height: 1.55; }

/* Auth Mode Tabs */
.auth-tabs {
  display: flex;
  background: rgba(11, 19, 39, 0.7);
  padding: 4px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  width: 100%;
}
.auth-tab {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--quest-parchment-muted);
  font-size: 13px;
  font-weight: 600;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}
.auth-tab:hover { color: var(--quest-parchment); }
.auth-tab.active {
  background: rgba(25, 61, 101, 0.85);
  color: var(--quest-gold);
  box-shadow: inset 0 0 8px rgba(217, 182, 111, 0.2);
}

/* Error Banner */
.auth-error-banner {
  background: rgba(200, 60, 60, 0.2);
  border: 1px solid #FF8A8A;
  color: #FF8A8A;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  text-align: left;
}
.error-icon { font-size: 16px; flex-shrink: 0; }
.error-text { line-height: 1.4; }

.grade-pick { display: flex; flex-direction: column; gap: 8px; width: 100%; text-align: left; }
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

.existing-user-banner {
  background: rgba(40, 116, 91, 0.25);
  border: 1px solid #7AE0BF;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.user-badge { color: #7AE0BF; font-weight: 700; font-size: 13px; }
.user-status-text { font-size: 12px; color: var(--quest-parchment); margin: 0; line-height: 1.45; }
.checking-indicator { font-size: 10px; color: var(--quest-gold); text-transform: none; margin-left: 8px; }

.grade-pick { display: flex; flex-direction: column; gap: 8px; width: 100%; text-align: left; }
.grade-label { font-size: 12px; color: var(--quest-gold); text-transform: uppercase; letter-spacing: 0.06em; }
.grade-btns { display: flex; gap: 10px; }

/* Command center */
.command-center { max-width: 860px; margin: 0 auto; display: flex; flex-direction: column; gap: var(--space-xl); }
.hero-block { display: flex; flex-direction: column; gap: 10px; }
.hero-top-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.btn-switch-scholar {
  background: rgba(25, 61, 101, 0.5);
  border: 1px solid var(--border-medium);
  color: var(--quest-gold);
  font-size: 13px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-switch-scholar:hover {
  background: rgba(217, 182, 111, 0.2);
  border-color: var(--quest-gold);
}
.hero-title { font-size: 32px; color: var(--quest-parchment); margin: 0; }
.hero-name { color: var(--quest-gold); }
.hero-sub { font-size: 14px; color: var(--quest-parchment-muted); margin: 6px 0 0; }
.xp-bar-wrap { display: flex; align-items: center; gap: 12px; }
.xp-bar { flex: 1; height: 10px; background: var(--quest-abyss); border-radius: 999px; overflow: hidden; border: 1px solid var(--border-subtle); }
.xp-fill { height: 100%; background: linear-gradient(90deg, #D9B66F, #FFE8B8); border-radius: 999px; transition: width 0.5s ease; }
.xp-label { font-size: 12px; color: var(--quest-parchment-muted); white-space: nowrap; }

.quick-actions { display: flex; flex-direction: column; gap: 24px; }
.action-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
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

@media (max-width: 640px) {
  .home-page {
    padding: var(--space-md) var(--space-sm);
  }
  .onboarding-overlay {
    padding: var(--space-sm);
  }
  .onboarding-card {
    padding: 24px 18px;
    gap: 16px;
  }
  .onboarding-title {
    font-size: 22px;
  }
  .hero-title {
    font-size: 22px;
  }
  .hero-top-row {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-switch-scholar {
    text-align: center;
  }
  .action-cards-grid {
    grid-template-columns: 1fr;
  }
  .action-card {
    padding: 14px;
  }
}
</style>
