<script setup lang="ts">
import type { Realm } from '~/types/quest'

const props = defineProps<{
  realm: Realm
}>()

const emit = defineEmits<{
  (e: 'continue'): void
}>()
</script>

<template>
  <section class="hero-banner quest-surface-card" aria-labelledby="banner-heading">
    <!-- Ambient Backdrop Art Gradients -->
    <div class="banner-ambient" :class="`ambient-${realm.themeColor}`" aria-hidden="true" />
    
    <div class="banner-content">
      <div class="banner-badge-row">
        <span class="badge badge-gold">Active Expedition</span>
        <span class="banner-lore-pill">{{ realm.loreTag }}</span>
      </div>

      <div class="banner-main-grid">
        <div class="banner-text-col">
          <h2 id="banner-heading" class="banner-title font-display">
            Resume Your Quest in {{ realm.title }}
          </h2>
          <p class="banner-desc">
            {{ realm.description }} Current sector curriculum focuses on 
            <strong class="text-gold">{{ realm.curriculum }}</strong>.
          </p>

          <div class="banner-stats-row">
            <div class="banner-stat">
              <span class="stat-num font-mono">{{ realm.completedQuests }} / {{ realm.totalQuests }}</span>
              <span class="stat-name">Crucibles Cleared</span>
            </div>
            <div class="banner-stat-divider" />
            <div class="banner-stat">
              <span class="stat-num font-mono text-emerald">{{ realm.progressPercent }}%</span>
              <span class="stat-name">Realm Harmonic Balance</span>
            </div>
            <div class="banner-stat-divider" />
            <div class="banner-stat">
              <span class="stat-num font-mono text-gold">+120 XP</span>
              <span class="stat-name">Next Milestone Reward</span>
            </div>
          </div>
        </div>

        <div class="banner-action-col">
          <button 
            type="button" 
            class="btn-gold btn-continue-pulse"
            @click="emit('continue')"
          >
            <span class="btn-icon" aria-hidden="true">⚔️</span>
            <span>Continue Adventure</span>
          </button>
          <span class="action-subtext">Instant XP & Chamber Progression</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-banner {
  padding: 28px 32px;
  overflow: hidden;
  border: 1px solid var(--border-medium);
  margin-bottom: var(--space-xl);
  background: linear-gradient(135deg, rgba(25, 61, 101, 0.7) 0%, rgba(16, 27, 53, 0.85) 100%);
}

.banner-ambient {
  position: absolute;
  top: -40%;
  right: -10%;
  width: 500px;
  height: 350px;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(60px);
  opacity: 0.25;
}

.ambient-emerald {
  background: radial-gradient(circle, #28745B 0%, transparent 70%);
}

.ambient-gold {
  background: radial-gradient(circle, #D9B66F 0%, transparent 70%);
}

.ambient-violet {
  background: radial-gradient(circle, #9C8AD6 0%, transparent 70%);
}

.banner-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.banner-badge-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.banner-lore-pill {
  font-size: 11px;
  font-family: var(--font-display);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--quest-parchment-muted);
}

.banner-main-grid {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-xl);
  align-items: center;
}

.banner-text-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.banner-title {
  font-size: 26px;
  color: var(--quest-parchment);
  line-height: 1.25;
}

.banner-desc {
  font-size: 14px;
  color: var(--quest-parchment-muted);
  max-width: 680px;
  line-height: 1.6;
}

.text-gold {
  color: var(--quest-gold);
}

.text-emerald {
  color: #7AE0BF;
}

.banner-stats-row {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.banner-stat {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 16px;
  font-weight: 700;
  color: var(--quest-parchment);
}

.stat-name {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--quest-parchment-muted);
}

.banner-stat-divider {
  width: 1px;
  height: 24px;
  background: var(--border-medium);
}

.banner-action-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.btn-continue-pulse {
  font-size: 15px;
  padding: 14px 28px;
  border-radius: var(--radius-sm);
}

.btn-icon {
  font-size: 16px;
}

.action-subtext {
  font-size: 11px;
  color: var(--quest-parchment-muted);
  letter-spacing: 0.03em;
}

@media (max-width: 860px) {
  .banner-main-grid {
    grid-template-columns: 1fr;
  }
  .banner-action-col {
    align-items: flex-start;
  }
}
</style>
