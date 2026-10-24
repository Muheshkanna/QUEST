<script setup lang="ts">
import type { Realm, RealmId } from '~/types/quest'

const props = defineProps<{
  realms: Realm[]
  selectedRealmId: string
}>()

const emit = defineEmits<{
  (e: 'selectRealm', id: RealmId): void
}>()
</script>

<template>
  <section class="realms-section" aria-labelledby="realms-heading">
    <div class="section-header">
      <div class="section-title-wrap">
        <span class="badge badge-common">Expedition Portals</span>
        <h2 id="realms-heading" class="section-title font-display">The Three Sacred Realms</h2>
      </div>
      <p class="section-subtitle">
        Select a sanctuary to align your adventure focal point and unlock specialized mathematical crucibles.
      </p>
    </div>

    <div class="realms-grid">
      <div
        v-for="realm in realms"
        :key="realm.id"
        class="realm-card quest-surface-card"
        :class="[
          `realm-${realm.themeColor}`,
          { 'is-selected': selectedRealmId === realm.id }
        ]"
        tabindex="0"
        role="button"
        :aria-pressed="selectedRealmId === realm.id"
        @click="emit('selectRealm', realm.id)"
        @keydown.enter.space.prevent="emit('selectRealm', realm.id)"
      >
        <!-- Realm Glow Accent Strip -->
        <div class="realm-glow-header" />

        <!-- Decorative Geometric/Cosmic/Botanical Vector Illustration Header -->
        <div class="realm-artwork-banner" :class="`art-${realm.themeColor}`" aria-hidden="true">
          <!-- 1. Enchanted Forest: Bioluminescent Leaf Veins & Fibonacci Sprout -->
          <svg v-if="realm.id === 'enchanted-forest'" class="realm-art-svg" viewBox="0 0 320 80" preserveAspectRatio="none">
            <defs>
              <linearGradient id="forest-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#28745B" stop-opacity="0.6" />
                <stop offset="100%" stop-color="#101B35" stop-opacity="0.9" />
              </linearGradient>
            </defs>
            <rect width="320" height="80" fill="url(#forest-grad)" />
            <!-- Organic foliage ripples and fractions arcs -->
            <path d="M-20 60 Q 40 10, 100 50 T 220 30 T 340 70" fill="none" stroke="#7AE0BF" stroke-width="1.5" stroke-dasharray="3 3" opacity="0.6" />
            <path d="M20 80 Q 90 20, 160 60 T 300 40" fill="none" stroke="#28745B" stroke-width="2" opacity="0.8" />
            <!-- Leaf nodes & fraction markers -->
            <circle cx="95" cy="35" r="4" fill="#7AE0BF" opacity="0.8" />
            <circle cx="160" cy="60" r="3" fill="#D9B66F" opacity="0.7" />
            <circle cx="230" cy="33" r="5" fill="#7AE0BF" opacity="0.9" />
          </svg>

          <!-- 2. Temple of Wisdom: Sacred Polygons, Axioms & Gilded Compass -->
          <svg v-else-if="realm.id === 'temple-of-wisdom'" class="realm-art-svg" viewBox="0 0 320 80" preserveAspectRatio="none">
            <defs>
              <linearGradient id="temple-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8E743F" stop-opacity="0.5" />
                <stop offset="100%" stop-color="#101B35" stop-opacity="0.9" />
              </linearGradient>
            </defs>
            <rect width="320" height="80" fill="url(#temple-grad)" />
            <!-- Classical geometric triangles & concentric angle arcs -->
            <polygon points="160,10 210,70 110,70" fill="none" stroke="#D9B66F" stroke-width="1.5" opacity="0.5" />
            <polygon points="160,25 195,68 125,68" fill="none" stroke="#F1E8D6" stroke-width="1" stroke-dasharray="2 2" opacity="0.6" />
            <circle cx="160" cy="48" r="18" fill="none" stroke="#D9B66F" stroke-width="1" opacity="0.4" />
            <!-- Coordinate axes lines -->
            <line x1="20" y1="40" x2="300" y2="40" stroke="#D9B66F" stroke-width="1" stroke-dasharray="4 4" opacity="0.3" />
            <circle cx="60" cy="40" r="3" fill="#D9B66F" opacity="0.8" />
            <circle cx="260" cy="40" r="3" fill="#D9B66F" opacity="0.8" />
          </svg>

          <!-- 3. Celestial Frontier: Astral Coordinates, Orbital Rings & Constellations -->
          <svg v-else class="realm-art-svg" viewBox="0 0 320 80" preserveAspectRatio="none">
            <defs>
              <linearGradient id="celestial-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#9C8AD6" stop-opacity="0.5" />
                <stop offset="100%" stop-color="#101B35" stop-opacity="0.95" />
              </linearGradient>
            </defs>
            <rect width="320" height="80" fill="url(#celestial-grad)" />
            <!-- Orbit ellipses & vectors -->
            <ellipse cx="160" cy="40" rx="90" ry="26" fill="none" stroke="#9C8AD6" stroke-width="1.5" opacity="0.6" transform="rotate(-8 160 40)" />
            <ellipse cx="160" cy="40" rx="130" ry="34" fill="none" stroke="#D4C9FF" stroke-width="1" stroke-dasharray="3 3" opacity="0.4" transform="rotate(12 160 40)" />
            <!-- Starlight nodes -->
            <circle cx="90" cy="32" r="3" fill="#D4C9FF" opacity="0.9" />
            <circle cx="160" cy="40" r="5" fill="#D9B66F" opacity="0.8" />
            <circle cx="230" cy="46" r="3.5" fill="#D4C9FF" opacity="0.9" />
            <circle cx="280" cy="20" r="2" fill="#fff" opacity="0.7" />
          </svg>

          <span class="artwork-badge font-display">{{ realm.loreTag }}</span>
        </div>

        <div class="realm-card-body">
          <div class="realm-top-row">
            <span class="realm-icon" role="img" :aria-label="realm.title">{{ realm.icon }}</span>
            <div class="realm-badge-group">
              <span v-if="selectedRealmId === realm.id" class="badge badge-gold">Active</span>
              <span class="badge" :class="`badge-${realm.themeColor}`">Lvl {{ realm.levelReq }}+</span>
            </div>
          </div>

          <h3 class="realm-title font-display">{{ realm.title }}</h3>
          <span class="realm-subtitle">{{ realm.subtitle }}</span>

          <p class="realm-description">{{ realm.description }}</p>

          <div class="realm-curriculum-pill">
            <span class="pill-label">Curriculum:</span>
            <span class="pill-value">{{ realm.curriculum }}</span>
          </div>

          <!-- Progress bar -->
          <div class="realm-progress-block">
            <div class="progress-meta">
              <span class="progress-label">Sanctuary Mastery</span>
              <span class="progress-value font-mono">{{ realm.completedQuests }}/{{ realm.totalQuests }} ({{ realm.progressPercent }}%)</span>
            </div>
            <div class="progress-track" role="progressbar" :aria-valuenow="realm.progressPercent" :aria-valuemin="0" :aria-valuemax="100">
              <div 
                class="progress-fill" 
                :class="`fill-${realm.themeColor}`"
                :style="{ width: `${realm.progressPercent}%` }" 
              />
            </div>
          </div>

          <div class="realm-card-footer">
            <button
              type="button"
              class="btn-realm-enter"
              :class="{ 'btn-active-realm': selectedRealmId === realm.id }"
            >
              {{ selectedRealmId === realm.id ? 'Currently Exploring' : 'Commune with Realm' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.realms-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title {
  font-size: 20px;
  color: var(--quest-parchment);
}

.section-subtitle {
  font-size: 13px;
  color: var(--quest-parchment-muted);
}

.realms-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
}

.realm-card {
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

.realm-card:hover {
  transform: translateY(-2px);
  border-color: var(--quest-gold);
}

.realm-card:focus-visible {
  outline: 2px solid var(--quest-gold);
  outline-offset: 3px;
}

.realm-card.is-selected {
  border-color: var(--quest-gold);
  box-shadow: 0 0 20px rgba(217, 182, 111, 0.25), 0 8px 24px rgba(5, 10, 22, 0.7);
}

.realm-glow-header {
  height: 4px;
  width: 100%;
}

.realm-emerald .realm-glow-header {
  background: linear-gradient(90deg, #28745B, #7AE0BF);
}

.realm-gold .realm-glow-header {
  background: linear-gradient(90deg, #D9B66F, #FFE8B8);
}

.realm-violet .realm-glow-header {
  background: linear-gradient(90deg, #9C8AD6, #D4C9FF);
}

/* Distinct Realm Vector Artwork */
.realm-artwork-banner {
  position: relative;
  height: 64px;
  width: 100%;
  overflow: hidden;
  border-bottom: 1px solid var(--border-subtle);
}

.realm-art-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.artwork-badge {
  position: absolute;
  bottom: 6px;
  left: 12px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 2px 6px;
  border-radius: 3px;
  backdrop-filter: blur(4px);
}

.art-emerald .artwork-badge {
  color: #7AE0BF;
  background: rgba(16, 27, 53, 0.85);
  border: 1px solid rgba(40, 116, 91, 0.5);
}

.art-gold .artwork-badge {
  color: var(--quest-gold);
  background: rgba(16, 27, 53, 0.85);
  border: 1px solid rgba(217, 182, 111, 0.4);
}

.art-violet .artwork-badge {
  color: #D4C9FF;
  background: rgba(16, 27, 53, 0.85);
  border: 1px solid rgba(156, 138, 214, 0.4);
}

.realm-card-body {
  padding: 18px 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.realm-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.realm-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.4));
}

.realm-badge-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.realm-title {
  font-size: 17px;
  color: var(--quest-parchment);
  line-height: 1.25;
}

.realm-subtitle {
  font-size: 11px;
  font-style: italic;
  color: var(--quest-parchment-muted);
  margin-top: -6px;
}

.realm-description {
  font-size: 13px;
  color: var(--quest-parchment-muted);
  line-height: 1.5;
  flex: 1;
}

.realm-curriculum-pill {
  background: rgba(11, 19, 39, 0.6);
  border: 1px solid var(--border-subtle);
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.pill-label {
  font-size: 10px;
  text-transform: uppercase;
  color: var(--quest-gold);
  font-weight: 700;
}

.pill-value {
  color: var(--quest-parchment);
  line-height: 1.3;
}

.realm-progress-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--quest-parchment-muted);
}

.progress-track {
  height: 8px;
  background: var(--quest-abyss);
  border-radius: var(--radius-full);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}

.fill-emerald {
  background: linear-gradient(90deg, #28745B, #7AE0BF);
  box-shadow: 0 0 8px rgba(40, 116, 91, 0.6);
}

.fill-gold {
  background: linear-gradient(90deg, #D9B66F, #FFE8B8);
  box-shadow: 0 0 8px rgba(217, 182, 111, 0.6);
}

.fill-violet {
  background: linear-gradient(90deg, #9C8AD6, #D4C9FF);
  box-shadow: 0 0 8px rgba(156, 138, 214, 0.6);
}

.realm-card-footer {
  margin-top: 6px;
}

.btn-realm-enter {
  width: 100%;
  padding: 8px 12px;
  background: rgba(25, 61, 101, 0.5);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-realm-enter:hover {
  background: rgba(35, 82, 136, 0.8);
  border-color: var(--quest-gold);
  color: #fff;
}

.btn-active-realm {
  background: rgba(217, 182, 111, 0.15);
  border-color: var(--quest-gold);
  color: var(--quest-gold);
  font-weight: 700;
}

@media (max-width: 1024px) {
  .realms-grid {
    grid-template-columns: 1fr;
  }
}
</style>
