<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import Infographic from '~/components/Infographic.vue'
import Explainer from '~/components/Explainer.vue'

const store = useGameStore()
const route = useRoute()
const router = useRouter()

const topicId = route.params.id as string
const lesson = ref<any>(null)
const infographic = ref<any>(null)
const explainer = ref<any>(null)
const loading = ref(true)

type TabKey = 'lesson' | 'infographic' | 'explainer'
const activeTab = ref<TabKey>('lesson')

function stopAllSpeech() {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel()
    } catch {}
  }
}

onBeforeRouteLeave(() => {
  stopAllSpeech()
})

onBeforeUnmount(() => {
  stopAllSpeech()
})

// Fetch helper with graceful fallback to /fallback/*
async function fetchWithFallback(apiPath: string, fallbackPath: string): Promise<any | null> {
  try {
    const res = await fetch(apiPath)
    if (res.ok) {
      return await res.json()
    }
  } catch {
    // API server is down or unreachable; proceed to fallback
  }

  // Attempt static offline fallback
  try {
    const fallbackRes = await fetch(fallbackPath)
    if (fallbackRes.ok) {
      return await fallbackRes.json()
    }
  } catch {
    // Both failed
  }
  return null
}

onMounted(async () => {
  store.initFromStorage()
  loading.value = true

  try {
    const [lessonData, infographicData, explainerData] = await Promise.all([
      fetchWithFallback(`/api/lesson/${topicId}`, `/fallback/lessons/${topicId}.json`),
      fetchWithFallback(`/api/infographic/${topicId}`, `/fallback/infographics/${topicId}.json`),
      fetchWithFallback(`/api/explainer/${topicId}`, `/fallback/explainers/${topicId}.json`)
    ])

    lesson.value = lessonData
    infographic.value = infographicData
    explainer.value = explainerData
  } finally {
    loading.value = false
  }
})

// Compute available tabs - hide tab if endpoint returned 404 (no empty tabs)
const availableTabs = computed(() => {
  const tabs: { key: TabKey; label: string; icon: string }[] = [
    { key: 'lesson', label: 'Lesson', icon: '📜' }
  ]
  if (infographic.value) {
    tabs.push({ key: 'infographic', label: 'Infographic', icon: '🖼️' })
  }
  if (explainer.value) {
    tabs.push({ key: 'explainer', label: 'Explainer', icon: '🎬' })
  }
  return tabs
})

function selectTab(key: TabKey) {
  if (activeTab.value === 'explainer' && key !== 'explainer') {
    stopAllSpeech()
  }
  activeTab.value = key
}

function startBattle() {
  stopAllSpeech()
  router.push(`/quiz/${topicId}`)
}
</script>

<template>
  <div class="lesson-page" :class="{ 'has-split-layout': infographic && activeTab === 'lesson' }">
    <!-- Top Breadcrumb Navigation -->
    <div class="lesson-breadcrumb">
      <NuxtLink to="/map" class="back-link">← Realm Map</NuxtLink>
      <span class="sep">/</span>
      <span class="crumb-topic">{{ topicId.replace(/-/g, ' ') }}</span>
    </div>

    <!-- Loading Orb State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-orb"></div>
      <p class="font-display" style="color:var(--quest-gold)">Consulting the arcane scrolls…</p>
    </div>

    <div v-else-if="lesson || infographic || explainer" class="lesson-container">
      <!-- Tabs Navigation Header (Only renders available tabs) -->
      <div v-if="availableTabs.length > 1" class="tabs-bar" role="tablist" aria-label="Lesson content modes">
        <button
          v-for="tab in availableTabs"
          :key="tab.key"
          type="button"
          class="tab-btn font-display"
          :class="{ 'is-active': activeTab === tab.key }"
          role="tab"
          :aria-selected="activeTab === tab.key"
          :aria-controls="`tab-panel-${tab.key}`"
          :id="`tab-button-${tab.key}`"
          @click="selectTab(tab.key)"
        >
          <span class="tab-icon" aria-hidden="true">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <!-- TAB 1: LESSON TAB -->
      <div
        v-if="activeTab === 'lesson'"
        id="tab-panel-lesson"
        role="tabpanel"
        aria-labelledby="tab-button-lesson"
        class="tab-panel"
      >
        <!-- Desktop Two-Column Layout (or Stacked on Mobile) when Infographic exists -->
        <div v-if="infographic" class="lesson-split-grid">
          <!-- Left Column: Explanation, Steps & Example -->
          <div class="lesson-left-col">
            <header class="lesson-header">
              <span class="lesson-badge badge-gold">Lesson</span>
              <h1 class="lesson-title font-display">{{ lesson?.title || topicId.replace(/-/g, ' ') }}</h1>
              <p v-if="lesson?.bigIdea" class="lesson-big-idea">{{ lesson.bigIdea }}</p>
            </header>

            <div v-if="lesson?.explanation" class="lesson-body quest-surface-card" v-html="lesson.explanation"></div>

            <div v-if="lesson?.keySteps?.length" class="key-steps quest-surface-card">
              <h2 class="steps-title font-display">Key Steps</h2>
              <ol class="steps-list">
                <li v-for="(step, i) in lesson.keySteps" :key="i" class="step-item">{{ step }}</li>
              </ol>
            </div>

            <div v-if="lesson?.example" class="example-card quest-surface-card">
              <h2 class="example-title font-display">Worked Example</h2>
              <div v-html="lesson.example"></div>
            </div>

            <div class="battle-cta">
              <p class="cta-lore font-display">The realm awaits your challenge. Prove your mastery!</p>
              <button class="btn-battle" @click="startBattle">⚔️ Enter the Boss Battle</button>
            </div>
          </div>

          <!-- Right Column: Visual Infographic placed beside the explanation -->
          <div class="lesson-right-col">
            <div class="sticky-visual-wrapper">
              <Infographic :infographic="infographic" :topic-id="topicId" />
            </div>
          </div>
        </div>

        <!-- Single Column Layout when Infographic does not exist -->
        <div v-else class="lesson-single-col">
          <header class="lesson-header">
            <span class="lesson-badge badge-gold">Lesson</span>
            <h1 class="lesson-title font-display">{{ lesson?.title || topicId.replace(/-/g, ' ') }}</h1>
            <p v-if="lesson?.bigIdea" class="lesson-big-idea">{{ lesson.bigIdea }}</p>
          </header>

          <div v-if="lesson?.explanation" class="lesson-body quest-surface-card" v-html="lesson.explanation"></div>

          <div v-if="lesson?.keySteps?.length" class="key-steps quest-surface-card">
            <h2 class="steps-title font-display">Key Steps</h2>
            <ol class="steps-list">
              <li v-for="(step, i) in lesson.keySteps" :key="i" class="step-item">{{ step }}</li>
            </ol>
          </div>

          <div v-if="lesson?.example" class="example-card quest-surface-card">
            <h2 class="example-title font-display">Worked Example</h2>
            <div v-html="lesson.example"></div>
          </div>

          <div class="battle-cta">
            <p class="cta-lore font-display">The realm awaits your challenge. Prove your mastery!</p>
            <button class="btn-battle" @click="startBattle">⚔️ Enter the Boss Battle</button>
          </div>
        </div>
      </div>

      <!-- TAB 2: INFOGRAPHIC TAB (Dedicated Full-Width Visual View) -->
      <div
        v-else-if="activeTab === 'infographic' && infographic"
        id="tab-panel-infographic"
        role="tabpanel"
        aria-labelledby="tab-button-infographic"
        class="tab-panel tab-panel-focused"
      >
        <header class="lesson-header">
          <span class="lesson-badge badge-gold">Infographic</span>
          <h1 class="lesson-title font-display">{{ infographic.title }}</h1>
        </header>

        <Infographic :infographic="infographic" :topic-id="topicId" />

        <div class="battle-cta">
          <p class="cta-lore font-display">Ready to test these steps in battle?</p>
          <button class="btn-battle" @click="startBattle">⚔️ Enter the Boss Battle</button>
        </div>
      </div>

      <!-- TAB 3: EXPLAINER TAB (Interactive Narrated Walkthrough) -->
      <div
        v-else-if="activeTab === 'explainer' && explainer"
        id="tab-panel-explainer"
        role="tabpanel"
        aria-labelledby="tab-button-explainer"
        class="tab-panel tab-panel-focused"
      >
        <header class="lesson-header">
          <span class="lesson-badge badge-gold">Explainer</span>
          <h1 class="lesson-title font-display">Arcane Concept Walkthrough</h1>
        </header>

        <Explainer :explainer="explainer" :topic-id="topicId" />
      </div>
    </div>

    <!-- Empty State Fallback -->
    <div v-else class="error-block">
      <h2 class="font-display" style="color:var(--quest-parchment)">No Scroll Available</h2>
      <p style="color:var(--quest-parchment-muted)">No lesson or infographic data found for topic "{{ topicId }}".</p>
      <button class="btn-battle" @click="startBattle">Start Battle Anyway →</button>
    </div>
  </div>
</template>

<style scoped>
.lesson-page {
  max-width: 820px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  transition: max-width 0.3s ease;
}

.lesson-page.has-split-layout {
  max-width: 1360px;
}

.lesson-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--quest-parchment-muted);
}

.back-link {
  color: var(--quest-gold);
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}

.crumb-topic {
  color: var(--quest-parchment);
  text-transform: capitalize;
}

.sep {
  color: var(--border-medium);
}

/* Tabs Bar */
.tabs-bar {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 6px;
  background: var(--surface-sunken);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  width: fit-content;
  box-shadow: var(--shadow-sm);
}

.tab-btn {
  min-height: 44px;
  padding: 8px 20px;
  border: none;
  background: transparent;
  color: var(--quest-parchment-muted);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.04em;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: var(--quest-parchment);
  background: rgba(255, 255, 255, 0.05);
}

.tab-btn.is-active {
  background: linear-gradient(135deg, rgba(217, 182, 111, 0.22), rgba(40, 116, 91, 0.28));
  color: var(--quest-gold);
  border: 1px solid var(--quest-gold);
  box-shadow: 0 0 12px var(--quest-gold-glow);
}

.tab-btn:focus-visible {
  outline: 2px solid var(--quest-gold);
  outline-offset: 2px;
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  width: 100%;
}

.tab-panel-focused {
  max-width: 960px;
  margin: 0 auto;
}

/* Two-Column Grid for Desktop */
.lesson-split-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-xl);
  align-items: start;
}

@media (min-width: 1024px) {
  .lesson-split-grid {
    grid-template-columns: 1.15fr 1fr;
  }
}

.lesson-left-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.lesson-right-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.sticky-visual-wrapper {
  position: sticky;
  top: 24px;
}

.lesson-single-col {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  width: 100%;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 80px 0;
}

.loading-orb {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: conic-gradient(var(--quest-gold), transparent, var(--quest-gold));
  animation: spin 1.4s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-block {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 40px;
  text-align: center;
  border: 1px dashed rgba(255, 138, 138, 0.4);
  border-radius: var(--radius-md);
}

.lesson-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.lesson-badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  background: rgba(217, 182, 111, 0.15);
  border: 1px solid rgba(217, 182, 111, 0.4);
  color: var(--quest-gold);
  display: inline-block;
  width: fit-content;
}

.lesson-title {
  font-size: 28px;
  color: var(--quest-parchment);
  line-height: 1.3;
}

.lesson-big-idea {
  font-size: 15px;
  color: var(--quest-parchment-muted);
  line-height: 1.6;
  font-style: italic;
}

.lesson-body,
.key-steps,
.example-card {
  padding: 24px 28px;
  border-radius: var(--radius-sm);
  font-size: 15px;
  color: var(--quest-parchment);
  line-height: 1.7;
}

.steps-title,
.example-title {
  font-size: 17px;
  color: var(--quest-gold);
  margin-bottom: 14px;
}

.steps-list {
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  color: var(--quest-parchment-muted);
  line-height: 1.6;
}

.battle-cta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
  border: 1px solid rgba(217, 182, 111, 0.3);
  border-radius: var(--radius-md);
  background: rgba(217, 182, 111, 0.05);
  text-align: center;
}

.cta-lore {
  font-size: 18px;
  color: var(--quest-parchment);
}

.btn-battle {
  min-height: 44px;
  padding: 14px 36px;
  background: linear-gradient(135deg, #D9B66F, #B8922A);
  border: none;
  border-radius: var(--radius-sm);
  color: #0B1327;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-battle:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-battle:focus-visible {
  outline: 2px solid var(--quest-gold);
  outline-offset: 2px;
}

@media (max-width: 768px) {
  .lesson-page {
    padding: var(--space-md) var(--space-sm);
    gap: var(--space-md);
  }

  /* Flagship topics: override split max-width so it doesn't push viewport */
  .lesson-page.has-split-layout {
    max-width: 100%;
  }

  /* Un-stick the infographic on mobile so it scrolls normally */
  .sticky-visual-wrapper {
    position: static;
  }

  .tabs-bar {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    flex-wrap: nowrap;
  }
  .tab-btn {
    padding: 8px 14px;
    font-size: 13px;
    flex: 1;
    justify-content: center;
  }
  .lesson-body,
  .key-steps,
  .example-card {
    padding: 18px 16px;
  }
  .lesson-title {
    font-size: 22px;
  }
  .btn-battle {
    width: 100%;
    padding: 12px 20px;
    font-size: 15px;
  }

  /* Ensure lesson-container never causes horizontal scroll */
  .lesson-container {
    overflow: hidden;
    width: 100%;
  }

  /* Right column visual comes after lesson content on mobile */
  .lesson-right-col {
    order: -1; /* Show infographic first on mobile, before the text */
  }

  /* tab-panel should respect viewport */
  .tab-panel,
  .tab-panel-focused {
    max-width: 100%;
    width: 100%;
  }
}
</style>
