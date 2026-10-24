<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useQuestState } from '~/composables/useQuestState'
import type { RealmId } from '~/types/quest'

const {
  student,
  realms,
  dailyTrial,
  topicMasteries,
  achievements,
  activities,
  selectedRealmId,
  selectedRealm,
  notification,
  initFromStorage,
  submitDailyTrial,
  continueAdventure,
  resetDemoState,
  setGrade
} = useQuestState()

const activeNav = ref<string>('command-center')
const apiStatus = ref<'checking' | 'online' | 'offline'>('checking')
const selectedTopic = ref<any>(null)

const checkApiHealth = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/health')
    if (res.ok) {
      const data = await res.json()
      if (data.status === 'online') {
        apiStatus.value = 'online'
        return
      }
    }
  } catch (e) {
    // try relative url in case hosted on same origin
    try {
      const resRel = await fetch('/api/health')
      if (resRel.ok) {
        apiStatus.value = 'online'
        return
      }
    } catch {}
  }
  apiStatus.value = 'offline'
}

onMounted(() => {
  initFromStorage()
  checkApiHealth()
})

const handleSelectRealm = (id: RealmId) => {
  selectedRealmId.value = id
}

const handleContinueAdventure = () => {
  continueAdventure()
}

const handleSelectTopic = (topic: any) => {
  selectedTopic.value = topic
  // If the topic has an associated realm, also align the realm
  if (topic.realm === 'Enchanted Forest') selectedRealmId.value = 'enchanted-forest'
  else if (topic.realm === 'Temple of Wisdom') selectedRealmId.value = 'temple-of-wisdom'
  else if (topic.realm === 'Celestial Frontier') selectedRealmId.value = 'celestial-frontier'
}

const handleUpdateGrade = (grade: 5 | 6) => {
  setGrade(grade)
}

const handleSolveTrial = (optionIndex: number) => {
  submitDailyTrial(optionIndex)
}
</script>

<template>
  <div class="quest-viewport">
    <!-- Header with Crest, Nav, HUD -->
    <QuestHeader
      :student="student"
      v-model:active-nav="activeNav"
      @update:grade="handleUpdateGrade"
      @reset-demo="resetDemoState"
    />

    <!-- Main Command Center Canvas -->
    <main class="quest-main-container" id="main-content">
      <!-- Floating Victory Notification -->
      <transition name="toast">
        <div v-if="notification" class="quest-notification-banner" role="alert">
          <div class="notification-body">
            <span class="notification-icon">✨</span>
            <div class="notification-text">
              <span class="notification-title font-display">{{ notification.title }}</span>
              <span class="notification-msg">{{ notification.message }}</span>
            </div>
          </div>
        </div>
      </transition>

      <!-- View: Command Center (Main) -->
      <div v-if="activeNav === 'command-center'" class="dashboard-layout">
        <!-- Main Adventure Column (Left 2/3) -->
        <div class="adventure-lane">
          <!-- Hero Banner: Continue Adventure & Active Sector -->
          <HeroBanner
            :realm="selectedRealm"
            @continue="handleContinueAdventure"
          />

          <!-- Daily Trial Interactive Card -->
          <DailyTrialCard
            :trial="dailyTrial"
            @solve="handleSolveTrial"
          />

          <!-- The Three Sacred Realms -->
          <RealmCards
            :realms="realms"
            :selected-realm-id="selectedRealmId"
            @select-realm="handleSelectRealm"
          />

          <!-- Georgia Standards 20 Curriculum Topics Explorer -->
          <TopicPicker
            :current-grade="student.grade || 5"
            :selected-topic-id="selectedTopic?.id"
            @select-topic="handleSelectTopic"
            @update:grade="handleUpdateGrade"
          />
        </div>

        <!-- Character Codex Column (Right 1/3) -->
        <div class="codex-lane">
          <!-- Topic Mastery Matrix -->
          <TopicMasteryCard
            :masteries="topicMasteries"
          />

          <!-- Character Codex & Achievements -->
          <CharacterCodex
            :student="student"
            :achievements="achievements"
            :activities="activities"
          />
        </div>
      </div>

      <!-- View: Realms of Study Dedicated View -->
      <div v-else-if="activeNav === 'realms'" class="subpage-layout">
        <div class="subpage-header">
          <div class="subpage-breadcrumb">
            <span class="badge badge-gold">Sanctuary Map</span>
            <span class="crumb-text">Grade {{ student.grade || 5 }} Territory</span>
          </div>
          <h2 class="subpage-title font-display">The Realms of Study & Curriculum Islands</h2>
          <p class="subpage-desc">Explore the 20 official Georgia K-12 Standards topics distributed across the Enchanted Forest, Temple of Wisdom, and Celestial Frontier.</p>
        </div>

        <HeroBanner
          :realm="selectedRealm"
          @continue="handleContinueAdventure"
        />

        <RealmCards
          :realms="realms"
          :selected-realm-id="selectedRealmId"
          @select-realm="handleSelectRealm"
        />

        <TopicPicker
          :current-grade="student.grade || 5"
          :selected-topic-id="selectedTopic?.id"
          @select-topic="handleSelectTopic"
          @update:grade="handleUpdateGrade"
        />
      </div>

      <!-- View: Scholar Codex Dedicated View -->
      <div v-else-if="activeNav === 'codex'" class="subpage-layout">
        <div class="subpage-header">
          <div class="subpage-breadcrumb">
            <span class="badge badge-emerald">Scholar Codex</span>
            <span class="crumb-text">Axiom Archives</span>
          </div>
          <h2 class="subpage-title font-display">Arcane Disciplines & Mastery Matrix</h2>
          <p class="subpage-desc">Comprehensive index of mastered mathematical axioms, numerical leyline attunement, and continuous progress chronicles.</p>
        </div>
        <div class="subpage-grid">
          <TopicMasteryCard :masteries="topicMasteries" />
          <CharacterCodex :student="student" :achievements="achievements" :activities="activities" />
        </div>
      </div>

      <!-- View: Vault of Glory (Achievements Dedicated) -->
      <div v-else-if="activeNav === 'achievements'" class="subpage-layout">
        <div class="subpage-header">
          <div class="subpage-breadcrumb">
            <span class="badge badge-violet">Vault of Glory</span>
            <span class="crumb-text">Hall of Relics</span>
          </div>
          <h2 class="subpage-title font-display">Trophies, Relics & Astral Honors</h2>
          <p class="subpage-desc">Permanent attestations of your heroic mathematical journey and crucible conquests.</p>
        </div>
        <div class="subpage-grid">
          <CharacterCodex :student="student" :achievements="achievements" :activities="activities" />
          <div class="subpage-col-stack">
            <DailyTrialCard :trial="dailyTrial" @solve="handleSolveTrial" />
            <TopicMasteryCard :masteries="topicMasteries" />
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="quest-footer">
      <div class="footer-content">
        <div class="footer-left">
          <span class="brand-sub">QUEST Command Center</span>
          <span class="footer-copy">An educational adventure platform powered by immersive mathematical progression.</span>
        </div>
        <div class="footer-links">
          <button type="button" class="btn-link" @click="activeNav = 'command-center'">Command Center</button>
          <span class="sep">•</span>
          <button type="button" class="btn-link" @click="activeNav = 'realms'">Realms</button>
          <span class="sep">•</span>
          <button type="button" class="btn-link" @click="activeNav = 'codex'">Codex</button>
          <span class="sep">•</span>
          <button type="button" class="btn-link" @click="activeNav = 'achievements'">Vault of Glory</button>
          <span class="sep">•</span>
          <button type="button" class="btn-link" @click="resetDemoState">Reset Demo Data</button>
          <span class="sep">•</span>
          <div class="api-status-pill" :class="`status-${apiStatus}`" title="Vercel Python FastAPI Server Status">
            <span class="status-dot" />
            <span class="status-text font-mono">API: {{ apiStatus }}</span>
          </div>
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
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px 64px;
  flex: 1;
  position: relative;
}

/* Notification Banner */
.quest-notification-banner {
  position: fixed;
  top: 76px;
  right: 24px;
  z-index: 100;
  background: rgba(16, 27, 53, 0.96);
  border: 1px solid var(--quest-gold);
  border-radius: var(--radius-sm);
  padding: 14px 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), 0 0 16px var(--quest-gold-glow);
  backdrop-filter: blur(12px);
}

.notification-body {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-icon {
  font-size: 20px;
}

.notification-text {
  display: flex;
  flex-direction: column;
}

.notification-title {
  font-size: 14px;
  color: var(--quest-gold);
  font-weight: 700;
}

.notification-msg {
  font-size: 12px;
  color: var(--quest-parchment);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-12px) scale(0.95);
}

/* Dashboard 2-column layout */
.dashboard-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(350px, 1.2fr);
  gap: 32px;
  align-items: start;
}

.adventure-lane {
  display: flex;
  flex-direction: column;
}

.codex-lane {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Dedicated Subpages */
.subpage-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.subpage-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.subpage-breadcrumb {
  display: flex;
  align-items: center;
  gap: 10px;
}

.crumb-text {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--quest-parchment-muted);
}

.subpage-title {
  font-size: 28px;
  color: var(--quest-parchment);
}

.subpage-desc {
  font-size: 14px;
  color: var(--quest-parchment-muted);
  max-width: 820px;
  line-height: 1.6;
}

.subpage-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
  align-items: start;
}

.subpage-col-stack {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Footer */
.quest-footer {
  border-top: 1px solid var(--border-subtle);
  background: var(--quest-abyss);
  padding: 24px;
  font-size: 12px;
  color: var(--quest-parchment-muted);
}

.footer-content {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-sub {
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--quest-gold);
}

.footer-copy {
  color: var(--quest-parchment-faint);
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-link {
  background: none;
  border: none;
  color: var(--quest-parchment-muted);
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
}

.btn-link:hover, .btn-link:focus-visible {
  color: var(--quest-gold);
  text-decoration: underline;
}

.sep {
  color: var(--quest-parchment-faint);
}

.api-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 11px;
  background: rgba(11, 19, 39, 0.6);
  border: 1px solid var(--border-subtle);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-online .status-dot {
  background: #28745B;
  box-shadow: 0 0 6px #7AE0BF;
}

.status-online .status-text {
  color: #7AE0BF;
}

.status-offline .status-dot {
  background: #b85042;
  box-shadow: 0 0 6px #e07a5f;
}

.status-offline .status-text {
  color: #e07a5f;
}

.status-checking .status-dot {
  background: var(--quest-gold);
}

.status-checking .status-text {
  color: var(--quest-gold);
}

@media (max-width: 1080px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
  }
  .subpage-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .quest-main-container {
    padding: 20px 16px 48px;
  }
  .subpage-title {
    font-size: 22px;
  }
}
</style>
