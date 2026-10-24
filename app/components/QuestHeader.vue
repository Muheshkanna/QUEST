<script setup lang="ts">
import type { StudentProfile } from '~/types/quest'

const props = defineProps<{
  student: StudentProfile
  activeNav: string
}>()

const emit = defineEmits<{
  (e: 'update:activeNav', nav: string): void
  (e: 'resetDemo'): void
}>()

const navItems = [
  { id: 'command-center', label: 'Command Center', icon: '🏛️' },
  { id: 'realms', label: 'Realms of Study', icon: '🗺️' },
  { id: 'codex', label: 'Scholar Codex', icon: '📜' },
  { id: 'achievements', label: 'Vault of Glory', icon: '🏆' }
]
</script>

<template>
  <header class="quest-header">
    <div class="header-container">
      <!-- Brand & Crest -->
      <div class="brand-group">
        <div class="brand-crest" aria-hidden="true">
          <svg viewBox="0 0 40 40" class="crest-svg" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="20,2 38,11 38,29 20,38 2,29 2,11" stroke="#D9B66F" stroke-width="2" fill="rgba(25, 61, 101, 0.6)" />
            <polygon points="20,7 33,14 33,26 20,33 7,26 7,14" stroke="#D9B66F" stroke-width="1" stroke-dasharray="2 2" />
            <path d="M20 10 L25 20 L20 23 L15 20 Z" fill="#D9B66F" />
            <circle cx="20" cy="20" r="3" fill="#F1E8D6" />
          </svg>
        </div>
        <div class="brand-meta">
          <h1 class="brand-title">QUEST</h1>
          <span class="brand-tagline">Arcanum of Learning</span>
        </div>
      </div>

      <!-- Main Navigation -->
      <nav class="header-nav" aria-label="Main Navigation">
        <button
          v-for="item in navItems"
          :key="item.id"
          class="nav-tab"
          :class="{ 'is-active': activeNav === item.id }"
          @click="emit('update:activeNav', item.id)"
          type="button"
        >
          <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="activeNav === item.id" class="active-indicator" />
        </button>
      </nav>

      <!-- Student HUD / Metrics Pill -->
      <div class="header-hud">
        <!-- Daily Streak Fire -->
        <div class="hud-streak" title="Daily Learning Streak">
          <span class="streak-icon" role="img" aria-label="Streak Flame">🔥</span>
          <div class="streak-data">
            <span class="streak-count">{{ student.streakDays }}</span>
            <span class="streak-label">Days</span>
          </div>
          <div v-if="student.streakShields > 0" class="streak-shield" title="Streak Freeze Shield Active">
            🛡️{{ student.streakShields }}
          </div>
        </div>

        <!-- Level & XP Mini-Bar -->
        <div class="hud-level-group" title="Current Level and Progress">
          <div class="level-seal">
            <span class="level-text">LVL</span>
            <span class="level-num">{{ student.level }}</span>
          </div>
          <div class="xp-mini-track">
            <div class="xp-mini-meta">
              <span class="xp-label">XP Progress</span>
              <span class="xp-numbers">{{ student.currentXp.toLocaleString() }} / {{ student.xpToNextLevel.toLocaleString() }}</span>
            </div>
            <div class="xp-bar-outer" role="progressbar" :aria-valuenow="student.currentXp" :aria-valuemin="0" :aria-valuemax="student.xpToNextLevel">
              <div 
                class="xp-bar-inner" 
                :style="{ width: Math.min(100, Math.round((student.currentXp / student.xpToNextLevel) * 100)) + '%' }" 
              />
            </div>
          </div>
        </div>

        <!-- Student Profile Avatar -->
        <div class="student-avatar-pill" title="Kaelen Vance — Arcanist of Axioms">
          <div class="avatar-frame">
            <span class="avatar-glyph">{{ student.avatar }}</span>
            <span class="avatar-status-dot" />
          </div>
          <div class="student-names">
            <span class="student-name">{{ student.name }}</span>
            <span class="student-title">{{ student.title }}</span>
          </div>
        </div>

        <!-- Demo Reset -->
        <button
          type="button"
          class="btn-reset-demo"
          @click="emit('resetDemo')"
          title="Reset quest demo state in localStorage"
          aria-label="Reset quest demo state"
        >
          ↺
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.quest-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(11, 19, 39, 0.92);
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
}

.brand-crest {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
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

.header-hud {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
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
  font-size: 16px;
  filter: drop-shadow(0 0 4px #ff6b35);
}

.streak-data {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.streak-count {
  font-size: 14px;
  font-weight: 800;
  color: #ffb86c;
  font-family: var(--font-mono);
}

.streak-label {
  font-size: 9px;
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
  min-width: 170px;
}

.level-seal {
  background: linear-gradient(135deg, var(--quest-gold) 0%, var(--quest-gold-muted) 100%);
  color: var(--quest-midnight);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 10px var(--quest-gold-glow);
  border: 1.5px solid #fff;
}

.level-text {
  font-size: 8px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: 0.05em;
}

.level-num {
  font-family: var(--font-display);
  font-size: 15px;
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
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--quest-abyss);
  border: 1.5px solid var(--quest-gold);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-glyph {
  font-size: 16px;
}

.avatar-status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 8px;
  height: 8px;
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
}

.btn-reset-demo:hover {
  color: var(--quest-gold);
  border-color: var(--quest-gold);
}

@media (max-width: 1024px) {
  .header-nav {
    display: none;
  }
}

@media (max-width: 640px) {
  .student-names {
    display: none;
  }
  .hud-level-group {
    min-width: 120px;
  }
  .xp-mini-meta {
    display: none;
  }
}
</style>
