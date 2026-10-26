<script setup lang="ts">
import type { StudentProfile } from '~/types/quest'
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps<{
  student: StudentProfile
  activeNav: string
}>()

const emit = defineEmits<{
  (e: 'update:activeNav', nav: string): void
  (e: 'update:grade', grade: 5 | 6): void
  (e: 'resetDemo'): void
}>()

const route = useRoute()
const isMobileMenuOpen = ref(false)

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

function closeMobileMenu() {
  isMobileMenuOpen.value = false
}

// Automatically close mobile menu when navigating routes
watch(() => route.path, () => {
  closeMobileMenu()
})

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isMobileMenuOpen.value) {
    closeMobileMenu()
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('keydown', handleKeydown)
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', handleKeydown)
  }
})

// Defensive wrapper — prevents crashes if student fields are undefined during hydration
const s = computed(() => ({
  name: props.student?.name ?? '',
  title: props.student?.title ?? '',
  avatar: props.student?.avatar ?? '⚔️',
  level: props.student?.level ?? 1,
  currentXp: props.student?.currentXp ?? 0,
  xpToNextLevel: props.student?.xpToNextLevel ?? 1000,
  totalXp: props.student?.totalXp ?? 0,
  streakDays: props.student?.streakDays ?? 0,
  streakShields: props.student?.streakShields ?? 0,
  grade: props.student?.grade ?? 5,
}))

const navItems = [
  {
    id: 'command-center',
    label: 'Command Center',
    shortLabel: 'Command',
    desc: 'Scholar sanctuary & daily trials',
    icon: '🏛️',
    to: '/'
  },
  {
    id: 'realms',
    label: 'Realms of Study',
    shortLabel: 'Realms',
    desc: 'Battle realms, infographics & lessons',
    icon: '🗺️',
    to: '/map'
  },
  {
    id: 'codex',
    label: 'Scholar Codex',
    shortLabel: 'Codex',
    desc: 'Living chronicle, titles & mastery',
    icon: '📜',
    to: '/codex'
  },
  {
    id: 'achievements',
    label: 'Vault of Glory',
    shortLabel: 'Vault',
    desc: 'Trophies, relics & heroic feats',
    icon: '🏆',
    to: '/vault'
  }
]

const isTabActive = (item: typeof navItems[0]) => {
  if (item.id === 'command-center') {
    return route.path === '/'
  }
  if (item.id === 'realms') {
    return route.path === '/map' || route.path.startsWith('/lesson') || route.path.startsWith('/quiz') || route.path.startsWith('/results')
  }
  if (item.id === 'codex') {
    return route.path.startsWith('/codex')
  }
  if (item.id === 'achievements') {
    return route.path.startsWith('/vault')
  }
  return props.activeNav === item.id
}
</script>

<template>
  <header class="quest-header">
    <div class="header-container">
      <!-- Brand & Crest -->
      <NuxtLink to="/" class="brand-group" @click="closeMobileMenu">
        <div class="brand-crest" aria-hidden="true">
          <svg viewBox="0 0 40 40" class="crest-svg" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="20,2 38,11 38,29 20,38 2,29 2,11" stroke="#D9B66F" stroke-width="2" fill="rgba(25, 61, 101, 0.6)" />
            <polygon points="20,7 33,14 33,26 20,33 7,26 7,14" stroke="#D9B66F" stroke-width="1" stroke-dasharray="2 2" />
            <path d="M20 10 L25 20 L20 23 L15 20 Z" fill="#D9B66F" />
            <circle cx="20" cy="20" r="3" fill="#F1E8D6" />
          </svg>
        </div>
        <div class="brand-meta">
          <span class="brand-title">QUEST</span>
          <span class="brand-tagline">Arcanum of Learning</span>
        </div>
      </NuxtLink>

      <!-- Desktop Main Navigation -->
      <nav class="header-nav header-nav-desktop" aria-label="Main Navigation">
        <NuxtLink
          v-for="item in navItems"
          :key="item.id"
          :to="item.to"
          class="nav-tab"
          :class="{ 'is-active': isTabActive(item) }"
          @click="emit('update:activeNav', item.id)"
        >
          <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="isTabActive(item)" class="active-indicator" />
        </NuxtLink>
      </nav>

      <!-- Student HUD / Metrics Pill (Desktop & Tablet) -->
      <div class="header-hud">
        <!-- Grade Selector (5 vs 6) -->
        <div class="hud-grade-picker" role="radiogroup" aria-label="Select Grade Level">
          <button
            type="button"
            class="btn-grade-toggle"
            :class="{ 'is-active': s.grade === 5 }"
            @click="emit('update:grade', 5)"
            title="Switch curriculum to Grade 5"
          >
            G5
          </button>
          <button
            type="button"
            class="btn-grade-toggle"
            :class="{ 'is-active': s.grade === 6 }"
            @click="emit('update:grade', 6)"
            title="Switch curriculum to Grade 6"
          >
            G6
          </button>
        </div>

        <!-- Daily Streak Fire -->
        <div class="hud-streak" title="Daily Learning Streak">
          <span class="streak-icon" role="img" aria-label="Streak Flame">🔥</span>
          <div class="streak-data">
            <span class="streak-count">{{ s.streakDays }}</span>
            <span class="streak-label">Days</span>
          </div>
          <div v-if="s.streakShields > 0" class="streak-shield" title="Streak Freeze Shield Active">
            🛡️{{ s.streakShields }}
          </div>
        </div>

        <!-- Level & XP Mini-Bar -->
        <div class="hud-level-group" title="Current Level and Progress">
          <div class="level-seal">
            <span class="level-text">LVL</span>
            <span class="level-num">{{ s.level }}</span>
          </div>
          <div class="xp-mini-track">
            <div class="xp-mini-meta">
              <span class="xp-label">XP Progress</span>
              <span class="xp-numbers">{{ s.currentXp.toLocaleString() }} / {{ s.xpToNextLevel.toLocaleString() }}</span>
            </div>
            <div class="xp-bar-outer" role="progressbar" :aria-valuenow="s.currentXp" :aria-valuemin="0" :aria-valuemax="s.xpToNextLevel">
              <div 
                class="xp-bar-inner" 
                :style="{ width: Math.min(100, Math.round((s.currentXp / (s.xpToNextLevel || 1000)) * 100)) + '%' }" 
              />
            </div>
          </div>
        </div>

        <!-- Student Profile Avatar -->
        <div class="student-avatar-pill">
          <div class="avatar-frame">
            <span class="avatar-glyph">{{ s.avatar || '⚔️' }}</span>
            <span class="avatar-status-dot" />
          </div>
          <div class="student-names">
            <span class="student-name">{{ s.name || 'Seeker' }}</span>
            <span class="student-title">{{ s.title || 'Initiate' }}</span>
          </div>
        </div>

        <!-- Demo Reset (Desktop) -->
        <button
          type="button"
          class="btn-reset-demo"
          @click="emit('resetDemo')"
          title="Reset quest demo state in localStorage"
          aria-label="Reset quest demo state"
        >
          ↺
        </button>

        <!-- Mobile Menu Hamburger Button -->
        <button
          type="button"
          class="btn-mobile-toggle"
          :class="{ 'is-open': isMobileMenuOpen }"
          :aria-expanded="isMobileMenuOpen"
          aria-label="Toggle navigation menu"
          @click="toggleMobileMenu"
        >
          <span class="bar top-bar"></span>
          <span class="bar mid-bar"></span>
          <span class="bar bot-bar"></span>
        </button>
      </div>
    </div>

    <!-- Mobile Slide-Down / Slide-Out Menu Drawer -->
    <Teleport to="body">
      <transition name="drawer-fade">
        <div
          v-if="isMobileMenuOpen"
          class="mobile-drawer-backdrop"
          @click="closeMobileMenu"
        >
          <div
            class="mobile-drawer-sheet quest-surface-card"
            @click.stop
            role="dialog"
            aria-label="Mobile Navigation Menu"
          >
            <!-- Drawer Header Bar -->
            <div class="drawer-header">
              <div class="drawer-brand-wrap">
                <span class="drawer-brand-title font-display">QUEST</span>
                <span class="drawer-brand-sub">Navigation & Scholar Codex</span>
              </div>
              <button
                type="button"
                class="btn-close-drawer"
                aria-label="Close navigation menu"
                @click="closeMobileMenu"
              >
                ✕
              </button>
            </div>

            <!-- Scholar Card Summary inside Drawer -->
            <div class="drawer-scholar-panel">
              <div class="drawer-avatar-row">
                <div class="drawer-avatar-seal">
                  <span class="drawer-avatar-emoji">{{ s.avatar || '⚔️' }}</span>
                </div>
                <div class="drawer-scholar-titles">
                  <span class="drawer-scholar-name font-display">{{ s.name || 'Seeker' }}</span>
                  <span class="drawer-scholar-rank">Level {{ s.level }} · {{ s.title || 'Initiate' }}</span>
                </div>
                <div class="drawer-streak-chip">
                  🔥 {{ s.streakDays }}d
                </div>
              </div>

              <!-- XP Track in Drawer -->
              <div class="drawer-xp-section">
                <div class="drawer-xp-meta font-mono">
                  <span>Level Progress</span>
                  <span>{{ s.currentXp.toLocaleString() }} / {{ s.xpToNextLevel.toLocaleString() }} XP</span>
                </div>
                <div class="xp-bar-outer">
                  <div
                    class="xp-bar-inner"
                    :style="{ width: Math.min(100, Math.round((s.currentXp / (s.xpToNextLevel || 1000)) * 100)) + '%' }"
                  />
                </div>
              </div>

              <!-- Grade Selector in Drawer -->
              <div class="drawer-grade-row">
                <span class="drawer-grade-label">Curriculum Grade:</span>
                <div class="drawer-grade-buttons">
                  <button
                    type="button"
                    class="drawer-grade-btn"
                    :class="{ active: s.grade === 5 }"
                    @click="emit('update:grade', 5)"
                  >
                    Grade 5
                  </button>
                  <button
                    type="button"
                    class="drawer-grade-btn"
                    :class="{ active: s.grade === 6 }"
                    @click="emit('update:grade', 6)"
                  >
                    Grade 6
                  </button>
                </div>
              </div>
            </div>

            <!-- Full Navigation Menu Links -->
            <div class="drawer-nav-group">
              <span class="drawer-nav-heading">Realms & Codex</span>
              <nav class="drawer-nav-list" aria-label="Mobile Navigation Menu">
                <NuxtLink
                  v-for="item in navItems"
                  :key="'drawer-' + item.id"
                  :to="item.to"
                  class="drawer-nav-link"
                  :class="{ 'is-active': isTabActive(item) }"
                  @click="emit('update:activeNav', item.id); closeMobileMenu()"
                >
                  <span class="drawer-link-icon" aria-hidden="true">{{ item.icon }}</span>
                  <div class="drawer-link-text">
                    <span class="drawer-link-label font-display">{{ item.label }}</span>
                    <span class="drawer-link-desc">{{ item.desc }}</span>
                  </div>
                  <span class="drawer-link-arrow">→</span>
                </NuxtLink>
              </nav>
            </div>

            <!-- Drawer Bottom Actions -->
            <div class="drawer-actions">
              <button
                type="button"
                class="btn-drawer-reset"
                @click="emit('resetDemo'); closeMobileMenu()"
              >
                ↺ Reset Demo Progress
              </button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- Mobile Fixed Bottom Navigation Bar (Dock) -->
    <nav class="mobile-bottom-dock" aria-label="Mobile Bottom Navigation">
      <NuxtLink
        v-for="item in navItems"
        :key="'dock-' + item.id"
        :to="item.to"
        class="dock-item"
        :class="{ 'is-active': isTabActive(item) }"
        @click="emit('update:activeNav', item.id)"
      >
        <span class="dock-item-icon" aria-hidden="true">{{ item.icon }}</span>
        <span class="dock-item-label font-display">{{ item.shortLabel }}</span>
        <span v-if="isTabActive(item)" class="dock-item-indicator" />
      </NuxtLink>
    </nav>
  </header>
</template>

<style scoped>
.quest-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(11, 19, 39, 0.94);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-medium);
  box-shadow: 0 4px 20px rgba(5, 10, 22, 0.7);
  padding: 10px 24px;
}

.header-container {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  text-decoration: none;
  cursor: pointer;
}

.brand-crest {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.crest-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 0 6px var(--quest-gold-glow));
}

.brand-meta {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: var(--quest-gold);
  line-height: 1;
  text-shadow: 0 0 10px rgba(217, 182, 111, 0.4);
}

.brand-tagline {
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--quest-parchment-muted);
}

/* Desktop Main Navigation */
.header-nav {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(16, 27, 53, 0.6);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.nav-tab {
  position: relative;
  background: transparent;
  border: none;
  text-decoration: none;
  color: var(--quest-parchment-muted);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.nav-tab:hover {
  color: var(--quest-parchment);
  background: rgba(25, 61, 101, 0.4);
}

.nav-tab.is-active {
  color: var(--quest-gold);
  background: rgba(25, 61, 101, 0.85);
  box-shadow: inset 0 0 8px rgba(217, 182, 111, 0.15);
}

.active-indicator {
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background: var(--quest-gold);
  border-radius: 2px;
  box-shadow: 0 0 6px var(--quest-gold);
}

/* Header HUD */
.header-hud {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.hud-grade-picker {
  display: flex;
  align-items: center;
  background: rgba(16, 27, 53, 0.8);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  padding: 2px;
  gap: 2px;
}

.btn-grade-toggle {
  background: transparent;
  border: none;
  color: var(--quest-parchment-muted);
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.04em;
}

.btn-grade-toggle:hover {
  color: var(--quest-parchment);
}

.btn-grade-toggle.is-active {
  background: linear-gradient(135deg, #D9B66F 0%, #B89246 100%);
  color: var(--quest-midnight);
  box-shadow: 0 0 8px rgba(217, 182, 111, 0.4);
}

.hud-streak {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(25, 61, 101, 0.45);
  border: 1px solid rgba(217, 182, 111, 0.25);
  padding: 5px 10px;
  border-radius: var(--radius-full);
}

.streak-icon {
  font-size: 15px;
  filter: drop-shadow(0 0 4px #ff6b35);
}

.streak-data {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.streak-count {
  font-size: 13px;
  font-weight: 800;
  color: #ffb86c;
  font-family: var(--font-mono);
}

.streak-label {
  font-size: 8px;
  text-transform: uppercase;
  color: var(--quest-parchment-muted);
}

.streak-shield {
  font-size: 11px;
  background: rgba(40, 116, 91, 0.3);
  padding: 2px 4px;
  border-radius: 4px;
  border: 1px solid var(--quest-emerald);
}

.hud-level-group {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 160px;
}

.level-seal {
  background: linear-gradient(135deg, var(--quest-gold) 0%, var(--quest-gold-muted) 100%);
  color: var(--quest-midnight);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 10px var(--quest-gold-glow);
  border: 1.5px solid #fff;
  flex-shrink: 0;
}

.level-text {
  font-size: 8px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: 0.05em;
}

.level-num {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 800;
  line-height: 1;
}

.xp-mini-track {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.xp-mini-meta {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--quest-parchment-muted);
  font-family: var(--font-mono);
}

.xp-bar-outer {
  height: 7px;
  background: var(--quest-abyss);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  position: relative;
}

.xp-bar-inner {
  height: 100%;
  background: linear-gradient(90deg, #D9B66F 0%, #FFE8B8 100%);
  border-radius: var(--radius-full);
  transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 0 6px var(--quest-gold);
}

.student-avatar-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(25, 61, 101, 0.35);
  border: 1px solid var(--border-medium);
  padding: 4px 10px 4px 6px;
  border-radius: var(--radius-full);
}

.avatar-frame {
  position: relative;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--quest-abyss);
  border: 1.5px solid var(--quest-gold);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-glyph {
  font-size: 15px;
}

.avatar-status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 7px;
  height: 7px;
  background: #28745B;
  border-radius: 50%;
  border: 1.5px solid var(--quest-midnight);
}

.student-names {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.student-name {
  font-size: 12px;
  font-weight: 700;
  color: var(--quest-parchment);
}

.student-title {
  font-size: 10px;
  color: var(--quest-gold);
}

.btn-reset-demo {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--quest-parchment-muted);
  width: 28px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn-reset-demo:hover {
  color: var(--quest-gold);
  border-color: var(--quest-gold);
}

/* Mobile Hamburger Toggle Button */
.btn-mobile-toggle {
  display: none;
  background: rgba(25, 61, 101, 0.5);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  width: 38px;
  height: 38px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  cursor: pointer;
  padding: 6px;
  transition: all 0.2s ease;
}

.btn-mobile-toggle:hover {
  background: rgba(217, 182, 111, 0.15);
  border-color: var(--quest-gold);
}

.bar {
  width: 20px;
  height: 2px;
  background: var(--quest-gold);
  border-radius: 2px;
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.btn-mobile-toggle.is-open .top-bar {
  transform: translateY(7px) rotate(45deg);
}

.btn-mobile-toggle.is-open .mid-bar {
  opacity: 0;
}

.btn-mobile-toggle.is-open .bot-bar {
  transform: translateY(-7px) rotate(-45deg);
}

/* Mobile Bottom Dock (Hidden on Desktop) */
.mobile-bottom-dock {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 60;
  background: rgba(11, 19, 39, 0.96);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border-medium);
  box-shadow: 0 -4px 20px rgba(5, 10, 22, 0.8);
  padding: 6px 12px max(6px, env(safe-area-inset-bottom));
}

.dock-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 6px 4px;
  text-decoration: none;
  color: var(--quest-parchment-muted);
  border-radius: var(--radius-sm);
  position: relative;
  transition: all 0.2s ease;
  min-height: 48px;
}

.dock-item-icon {
  font-size: 20px;
  line-height: 1;
  transition: transform 0.2s ease;
}

.dock-item-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  line-height: 1;
}

.dock-item.is-active {
  color: var(--quest-gold);
}

.dock-item.is-active .dock-item-icon {
  transform: scale(1.15);
  filter: drop-shadow(0 0 6px var(--quest-gold));
}

.dock-item-indicator {
  position: absolute;
  top: 2px;
  width: 24px;
  height: 2px;
  background: var(--quest-gold);
  border-radius: 2px;
  box-shadow: 0 0 8px var(--quest-gold);
}

/* Mobile Drawer Modal Sheet */
.mobile-drawer-backdrop {
  position: fixed;
  inset: 0;
  z-index: 999;
  background: rgba(5, 10, 22, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  justify-content: flex-end;
}

.mobile-drawer-sheet {
  width: 100%;
  max-width: 380px;
  height: 100%;
  background: rgba(16, 27, 53, 0.98);
  border-left: 1px solid var(--border-medium);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 20px;
  gap: 18px;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.drawer-brand-wrap {
  display: flex;
  flex-direction: column;
}

.drawer-brand-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--quest-gold);
  letter-spacing: 0.08em;
}

.drawer-brand-sub {
  font-size: 11px;
  color: var(--quest-parchment-muted);
}

.btn-close-drawer {
  background: rgba(25, 61, 101, 0.5);
  border: 1px solid var(--border-medium);
  color: var(--quest-parchment);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn-close-drawer:hover {
  border-color: var(--quest-gold);
  color: var(--quest-gold);
}

/* Scholar Panel in Drawer */
.drawer-scholar-panel {
  background: rgba(25, 61, 101, 0.4);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.drawer-avatar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drawer-avatar-seal {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--quest-abyss);
  border: 2px solid var(--quest-gold);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 8px var(--quest-gold-glow);
  flex-shrink: 0;
}

.drawer-avatar-emoji {
  font-size: 22px;
}

.drawer-scholar-titles {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.drawer-scholar-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--quest-parchment);
}

.drawer-scholar-rank {
  font-size: 12px;
  color: var(--quest-gold);
}

.drawer-streak-chip {
  background: rgba(255, 107, 53, 0.15);
  border: 1px solid rgba(255, 107, 53, 0.4);
  color: #ffb86c;
  padding: 4px 8px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-mono);
}

.drawer-xp-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-xp-meta {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--quest-parchment-muted);
}

.drawer-grade-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid var(--border-subtle);
}

.drawer-grade-label {
  font-size: 12px;
  color: var(--quest-parchment-muted);
}

.drawer-grade-buttons {
  display: flex;
  gap: 6px;
}

.drawer-grade-btn {
  padding: 4px 12px;
  background: rgba(16, 27, 53, 0.8);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-xs);
  color: var(--quest-parchment-muted);
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s ease;
}

.drawer-grade-btn.active {
  background: linear-gradient(135deg, #D9B66F 0%, #B89246 100%);
  color: var(--quest-midnight);
  border-color: var(--quest-gold);
}

/* Drawer Navigation List */
.drawer-nav-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.drawer-nav-heading {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--quest-gold);
  padding: 0 4px;
}

.drawer-nav-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.drawer-nav-link {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  background: rgba(25, 61, 101, 0.35);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--quest-parchment);
  transition: all 0.2s ease;
}

.drawer-nav-link:hover {
  background: rgba(35, 82, 136, 0.5);
  border-color: var(--quest-gold);
}

.drawer-nav-link.is-active {
  background: rgba(25, 61, 101, 0.85);
  border-color: var(--quest-gold);
  box-shadow: inset 0 0 10px rgba(217, 182, 111, 0.2);
}

.drawer-link-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.drawer-link-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.drawer-link-label {
  font-size: 15px;
  font-weight: 700;
  color: var(--quest-parchment);
}

.drawer-nav-link.is-active .drawer-link-label {
  color: var(--quest-gold);
}

.drawer-link-desc {
  font-size: 11px;
  color: var(--quest-parchment-muted);
}

.drawer-link-arrow {
  color: var(--quest-gold);
  font-size: 16px;
  font-weight: 700;
}

.drawer-actions {
  padding-top: 10px;
  border-top: 1px solid var(--border-subtle);
}

.btn-drawer-reset {
  width: 100%;
  padding: 10px 14px;
  background: transparent;
  border: 1px dashed var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-drawer-reset:hover {
  color: var(--quest-gold);
  border-color: var(--quest-gold);
  background: rgba(217, 182, 111, 0.08);
}

/* Drawer Transitions */
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.25s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-fade-enter-active .mobile-drawer-sheet {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-fade-enter-from .mobile-drawer-sheet {
  transform: translateX(100%);
}

.drawer-fade-leave-active .mobile-drawer-sheet {
  transition: transform 0.2s ease-in;
}

.drawer-fade-leave-to .mobile-drawer-sheet {
  transform: translateX(100%);
}

/* Responsive Media Queries */
@media (max-width: 1024px) {
  .header-nav-desktop {
    display: none;
  }
  .hud-level-group {
    display: none;
  }
  .student-names {
    display: none;
  }
  .btn-mobile-toggle {
    display: flex;
  }
  .mobile-bottom-dock {
    display: flex;
  }
}

@media (max-width: 640px) {
  .quest-header {
    padding: 8px 14px;
  }
  .brand-tagline {
    display: none;
  }
  .hud-grade-picker {
    display: none;
  }
  .btn-reset-demo {
    display: none;
  }
  .student-avatar-pill {
    display: none;
  }
  .header-hud {
    gap: 8px;
  }
}
</style>
