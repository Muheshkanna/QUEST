<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { defaultStudent } from '~/composables/useQuestData'

const store = useGameStore()
const router = useRouter()

// Global route guard to halt any speech synthesis whenever navigating
router.beforeEach(() => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel()
    } catch {}
  }
})

// Safe student: always a full object even before initFromStorage runs
const safeStudent = computed(() => store.student ?? { ...defaultStudent })
</script>

<template>
  <div class="quest-viewport">
    <ClientOnly>
      <QuestHeader
        :student="safeStudent"
        :active-nav="store.activeNav"
        @update:active-nav="(v) => store.activeNav = v"
        @update:grade="store.setGrade"
        @reset-demo="store.resetDemoState"
      />
    </ClientOnly>
    <main class="quest-main-container" id="main-content">
      <transition name="toast">
        <div v-if="store.notification" class="quest-notification-banner" role="alert">
          <div class="notification-body">
            <span class="notification-icon">✨</span>
            <div class="notification-text">
              <span class="notification-title font-display">{{ store.notification.title }}</span>
              <span class="notification-msg">{{ store.notification.message }}</span>
            </div>
          </div>
        </div>
      </transition>
      <NuxtPage />
    </main>
    <footer class="quest-footer">
      <div class="footer-content">
        <div class="footer-left">
          <span class="brand-sub font-display">QUEST Command Center</span>
          <span class="footer-copy">An educational adventure platform powered by immersive mathematical progression.</span>
        </div>
        <div class="footer-links">
          <NuxtLink to="/" class="btn-link">Command Center</NuxtLink>
          <span class="sep">•</span>
          <NuxtLink to="/map" class="btn-link">Realms</NuxtLink>
          <span class="sep">•</span>
          <NuxtLink to="/codex" class="btn-link">Scholar Codex</NuxtLink>
          <span class="sep">•</span>
          <NuxtLink to="/vault" class="btn-link">Vault of Glory</NuxtLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.quest-viewport {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.quest-main-container {
  flex: 1;
}

.quest-notification-banner {
  position: fixed;
  top: 72px;
  right: 20px;
  z-index: 100;
  background: rgba(16, 27, 53, 0.95);
  border: 1px solid var(--quest-gold);
  border-radius: var(--radius-sm);
  padding: 12px 18px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5), 0 0 12px var(--quest-gold-glow);
  max-width: 380px;
}

.notification-body {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-icon {
  font-size: 22px;
}

.notification-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notification-title {
  color: var(--quest-gold);
  font-size: 14px;
  font-weight: 700;
}

.notification-msg {
  color: var(--quest-parchment);
  font-size: 12px;
}

.quest-footer {
  border-top: 1px solid var(--border-subtle);
  background: rgba(11, 19, 39, 0.7);
  padding: 24px;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.brand-sub {
  color: var(--quest-gold);
  font-size: 14px;
  font-weight: 700;
}

.footer-copy {
  color: var(--quest-parchment-muted);
  font-size: 12px;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-link {
  color: var(--quest-parchment-muted);
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s ease;
}

.btn-link:hover {
  color: var(--quest-gold);
}

.sep {
  color: var(--border-medium);
  font-size: 12px;
}

@media (max-width: 900px) {
  .quest-main-container {
    padding-bottom: 74px; /* Space for mobile bottom navigation dock */
  }
  .quest-footer {
    padding-bottom: 92px; /* Ensure footer content is above bottom dock */
  }
}
</style>
