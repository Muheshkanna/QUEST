<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { ref, computed, onMounted } from 'vue'

const store = useGameStore()

interface Topic {
  id: string
  title: string
  fantasy_name: string
  tier: string
  unlock_order: number
  icon: string
  island_theme: string
  realm: string
  grade: number
}

const topics = ref<Topic[]>([])
const loading = ref(true)
const apiError = ref(false)

// Icon name → emoji map
const ICON_MAP: Record<string, string> = {
  tree: '🌳', droplet: '💧', scale: '⚖️', flask: '🧪', scroll: '📜',
  gem: '💎', cube: '🧊', sparkles: '✨', compass: '🧭', hourglass: '⏳',
  balance: '⚖️', tag: '🏷️', target: '🎯', pie: '🥧', diamond: '💠',
  thermometer: '🌡️', crystal: '🔮', scales: '⚖️', chart: '📊', zap: '⚡'
}

function iconEmoji(name: string) { return ICON_MAP[name] ?? '📌' }

async function loadTopics() {
  try {
    const res = await fetch('/api/topics')
    if (!res.ok) throw new Error('API down')
    const data = await res.json()
    topics.value = data.topics ?? data
    apiError.value = false
  } catch {
    apiError.value = true
    // Fallback: use static topic list baked in at build time
    try {
      const r = await fetch('/api/topics')
      // already failed above, use empty
    } catch {}
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  store.initFromStorage()
  loadTopics()
})

const grade = computed(() => store.student?.grade ?? 5)

const gradedTopics = computed(() =>
  topics.value.filter(t => t.grade === grade.value).sort((a, b) => a.unlock_order - b.unlock_order)
)

const realmGroups = computed(() => {
  const map: Record<string, Topic[]> = {}
  for (const t of gradedTopics.value) {
    if (!map[t.realm]) map[t.realm] = []
    map[t.realm].push(t)
  }
  return map
})

const REALM_THEME: Record<string, { color: string; glow: string }> = {
  'Enchanted Forest': { color: '#7AE0BF', glow: 'rgba(122,224,191,0.15)' },
  'Temple of Wisdom': { color: '#D9B66F', glow: 'rgba(217,182,111,0.15)' },
  'Celestial Frontier': { color: '#D4C9FF', glow: 'rgba(212,201,255,0.15)' },
}

function masteryFor(id: string) {
  return store.topicMasteries?.find((m: any) => m.topicId === id)
}
</script>

<template>
  <div class="map-page">
    <div class="map-header">
      <div class="grade-switcher">
        <button
          v-for="g in [5, 6]" :key="g"
          class="grade-btn"
          :class="{ active: grade === g }"
          @click="store.setGrade(g as 5|6)"
        >Grade {{ g }}</button>
      </div>
      <h1 class="map-title font-display">Realm Map — Grade {{ grade }}</h1>
      <p class="map-subtitle">Choose your topic and begin the battle</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-orb"></div>
      <p class="font-display" style="color:var(--quest-gold)">Loading the realm…</p>
    </div>

    <div v-else-if="apiError && !gradedTopics.length" class="error-banner">
      ⚠️ Could not reach the API. Start the FastAPI server to load live topics.
    </div>

    <div v-else class="realms-list">
      <section
        v-for="(topicList, realmName) in realmGroups"
        :key="realmName"
        class="realm-section"
        :style="{ '--realm-color': REALM_THEME[realmName]?.color ?? '#D9B66F', '--realm-glow': REALM_THEME[realmName]?.glow ?? 'transparent' }"
      >
        <div class="realm-label">
          <div class="realm-line"></div>
          <span class="realm-name font-display">{{ realmName }}</span>
          <div class="realm-line"></div>
        </div>

        <div class="topics-grid">
          <NuxtLink
            v-for="topic in topicList"
            :key="topic.id"
            :to="`/lesson/${topic.id}`"
            class="topic-node"
            :class="{ 'topic-flagship': topic.tier === 'flagship' }"
          >
            <div class="topic-icon">{{ iconEmoji(topic.icon) }}</div>
            <div class="topic-body">
              <span class="topic-fantasy font-display">{{ topic.fantasy_name }}</span>
              <span class="topic-title">{{ topic.title }}</span>
              <div v-if="masteryFor(topic.id)" class="mastery-bar-wrap">
                <div class="mastery-bar">
                  <div class="mastery-fill" :style="{ width: Math.min(100, masteryFor(topic.id)!.bestScore) + '%' }"></div>
                </div>
                <span class="mastery-pct font-mono">{{ masteryFor(topic.id)!.bestScore }}%</span>
              </div>
            </div>
            <span v-if="topic.tier === 'flagship'" class="flagship-badge">★ Flagship</span>
            <span class="topic-arrow">→</span>
          </NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.map-page {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.map-header { text-align: center; }
.grade-switcher { display: flex; justify-content: center; gap: 8px; margin-bottom: 16px; }
.grade-btn {
  padding: 7px 20px;
  border-radius: 999px;
  border: 1px solid var(--border-medium);
  background: transparent;
  color: var(--quest-parchment-muted);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.grade-btn.active { background: rgba(217,182,111,0.15); border-color: var(--quest-gold); color: var(--quest-gold); }
.map-title { font-size: 28px; color: var(--quest-parchment); }
.map-subtitle { font-size: 13px; color: var(--quest-parchment-muted); margin-top: 4px; }

.loading-state { display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 60px 0; }
.loading-orb { width: 56px; height: 56px; border-radius: 50%; background: conic-gradient(var(--quest-gold), transparent, var(--quest-gold)); animation: spin 1.4s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.error-banner {
  text-align: center;
  padding: 20px;
  border: 1px solid rgba(255,138,138,0.4);
  background: rgba(200,60,60,0.1);
  border-radius: var(--radius-sm);
  color: #FF8A8A;
  font-size: 14px;
}

.realms-list { display: flex; flex-direction: column; gap: var(--space-xl); }

.realm-section { display: flex; flex-direction: column; gap: 16px; }
.realm-label { display: flex; align-items: center; gap: 12px; }
.realm-line { flex: 1; height: 1px; background: var(--realm-color); opacity: 0.3; }
.realm-name { font-size: 14px; color: var(--realm-color); letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap; }

.topics-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }

.topic-node {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: rgba(25,61,101,0.4);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--quest-parchment);
  transition: all 0.2s ease;
  position: relative;
}
.topic-node:hover {
  background: var(--realm-glow);
  border-color: var(--realm-color);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.4);
}
.topic-flagship { border-color: var(--quest-gold); background: rgba(217,182,111,0.06); }
.topic-icon { font-size: 28px; flex-shrink: 0; }
.topic-body { display: flex; flex-direction: column; gap: 3px; flex: 1; min-width: 0; }
.topic-fantasy { font-size: 14px; color: var(--realm-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.topic-title { font-size: 12px; color: var(--quest-parchment-muted); }
.mastery-bar-wrap { display: flex; align-items: center; gap: 6px; margin-top: 4px; }
.mastery-bar { flex: 1; height: 4px; background: var(--quest-abyss); border-radius: 999px; overflow: hidden; }
.mastery-fill { height: 100%; background: var(--realm-color); border-radius: 999px; transition: width 0.5s ease; }
.mastery-pct { font-size: 10px; color: var(--quest-parchment-muted); white-space: nowrap; }
.flagship-badge {
  position: absolute;
  top: 8px;
  right: 36px;
  font-size: 10px;
  color: var(--quest-gold);
  background: rgba(217,182,111,0.12);
  border: 1px solid rgba(217,182,111,0.3);
  padding: 2px 6px;
  border-radius: 3px;
  letter-spacing: 0.04em;
}
.topic-arrow { font-size: 16px; color: var(--quest-parchment-muted); flex-shrink: 0; transition: transform 0.2s; }
.topic-node:hover .topic-arrow { transform: translateX(3px); color: var(--realm-color); }
</style>
