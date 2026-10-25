<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { computed } from 'vue'
import { defaultStudent } from '~/composables/useQuestData'

const store = useGameStore()

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
          <span class="brand-sub">QUEST Command Center</span>
          <span class="footer-copy">An educational adventure platform powered by immersive mathematical progression.</span>
        </div>
        <div class="footer-links">
          <NuxtLink to="/" class="btn-link">Command Center</NuxtLink>
          <span class="sep">•</span>
          <NuxtLink to="/map" class="btn-link">Realms</NuxtLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Retain existing global styles – unchanged */
</style>
