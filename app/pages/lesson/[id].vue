<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const store = useGameStore()
const route = useRoute()
const router = useRouter()

const topicId = route.params.id as string
const lesson = ref<any>(null)
const loading = ref(true)
const apiError = ref(false)

onMounted(async () => {
  store.initFromStorage()
  try {
    const res = await fetch(`/api/lesson/${topicId}`)
    if (res.ok) {
      lesson.value = await res.json()
      apiError.value = false
    } else {
      apiError.value = true
    }
  } catch {
    apiError.value = true
  } finally {
    loading.value = false
  }
})

function startBattle() {
  router.push(`/quiz/${topicId}`)
}
</script>

<template>
  <div class="lesson-page">
    <div class="lesson-breadcrumb">
      <NuxtLink to="/map" class="back-link">← Realm Map</NuxtLink>
      <span class="sep">/</span>
      <span class="crumb-topic">{{ topicId.replace(/-/g, ' ') }}</span>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-orb"></div>
      <p class="font-display" style="color:var(--quest-gold)">Consulting the arcane scrolls…</p>
    </div>

    <div v-else-if="apiError" class="error-block">
      <h2 class="font-display" style="color:var(--quest-parchment)">⚠️ Lesson Unavailable</h2>
      <p style="color:var(--quest-parchment-muted)">The FastAPI server is not running. Start it with <code>uvicorn api.index:app --reload</code> to load the lesson.</p>
      <button class="btn-battle" @click="startBattle">Skip to Battle →</button>
    </div>

    <div v-else-if="lesson" class="lesson-content">
      <header class="lesson-header">
        <span class="lesson-badge badge-gold">Lesson</span>
        <h1 class="lesson-title font-display">{{ lesson.title }}</h1>
        <p v-if="lesson.bigIdea" class="lesson-big-idea">{{ lesson.bigIdea }}</p>
      </header>

      <div v-if="lesson.explanation" class="lesson-body quest-surface-card" v-html="lesson.explanation"></div>

      <div v-if="lesson.keySteps?.length" class="key-steps quest-surface-card">
        <h2 class="steps-title font-display">Key Steps</h2>
        <ol class="steps-list">
          <li v-for="(step, i) in lesson.keySteps" :key="i" class="step-item">{{ step }}</li>
        </ol>
      </div>

      <div v-if="lesson.example" class="example-card quest-surface-card">
        <h2 class="example-title font-display">Worked Example</h2>
        <div v-html="lesson.example"></div>
      </div>

      <div class="battle-cta">
        <p class="cta-lore font-display">The realm awaits your challenge. Prove your mastery!</p>
        <button class="btn-battle" @click="startBattle">⚔️ Enter the Boss Battle</button>
      </div>
    </div>

    <div v-else class="error-block">
      <p style="color:var(--quest-parchment-muted)">No lesson data found for this topic.</p>
      <button class="btn-battle" @click="startBattle">Start Battle Anyway →</button>
    </div>
  </div>
</template>

<style scoped>
.lesson-page {
  max-width: 760px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.lesson-breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--quest-parchment-muted); }
.back-link { color: var(--quest-gold); text-decoration: none; }
.back-link:hover { text-decoration: underline; }
.crumb-topic { color: var(--quest-parchment); text-transform: capitalize; }
.sep { color: var(--border-medium); }

.loading-state { display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 80px 0; }
.loading-orb { width: 56px; height: 56px; border-radius: 50%; background: conic-gradient(var(--quest-gold), transparent, var(--quest-gold)); animation: spin 1.4s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.error-block { display: flex; flex-direction: column; gap: 16px; padding: 40px; text-align: center; border: 1px dashed rgba(255,138,138,0.4); border-radius: var(--radius-md); }
code { background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 3px; font-size: 12px; }

.lesson-header { display: flex; flex-direction: column; gap: 8px; }
.lesson-badge { padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; background: rgba(217,182,111,0.15); border: 1px solid rgba(217,182,111,0.4); color: var(--quest-gold); display: inline-block; }
.lesson-title { font-size: 28px; color: var(--quest-parchment); line-height: 1.3; }
.lesson-big-idea { font-size: 15px; color: var(--quest-parchment-muted); line-height: 1.6; font-style: italic; }

.lesson-body, .key-steps, .example-card {
  padding: 24px 28px;
  border-radius: var(--radius-sm);
  font-size: 15px;
  color: var(--quest-parchment);
  line-height: 1.7;
}

.steps-title, .example-title { font-size: 17px; color: var(--quest-gold); margin-bottom: 14px; }
.steps-list { padding-left: 20px; display: flex; flex-direction: column; gap: 8px; }
.step-item { color: var(--quest-parchment-muted); line-height: 1.6; }

.battle-cta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
  border: 1px solid rgba(217,182,111,0.3);
  border-radius: var(--radius-md);
  background: rgba(217,182,111,0.05);
  text-align: center;
}
.cta-lore { font-size: 18px; color: var(--quest-parchment); }
.btn-battle {
  padding: 14px 36px;
  background: linear-gradient(135deg, #D9B66F, #B8922A);
  border: none;
  border-radius: var(--radius-sm);
  color: #0B1327;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}
.btn-battle:hover { opacity: 0.9; transform: translateY(-1px); }
</style>
