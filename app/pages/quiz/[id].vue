<script setup lang="ts">
import { useGameStore } from '~/stores/game'
import { onMounted, watch, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const store = useGameStore()
const route = useRoute()
const router = useRouter()

const topicId = route.params.id as string
const answered = ref(false)
const selectedIdx = ref<number | null>(null)
const isCorrect = ref(false)
const showMisconception = ref(false)
const diagnosedMisconception = ref<string | null>(null)

const currentQ = computed(() => store.quiz.questions[store.quiz.currentIndex])
const progress = computed(() => {
  const total = store.quiz.questions.length || 10
  return Math.round(((store.quiz.currentIndex) / total) * 100)
})

const correctIndex = computed(() => {
  const q = currentQ.value
  if (!q) return 0
  return q.correct_index !== undefined ? q.correct_index : (q.correctIndex ?? 0)
})

const getOptionLetter = (opt: any, idx: number) => {
  if (typeof opt === 'object' && opt && opt.id) return opt.id
  return ['A', 'B', 'C', 'D'][idx] || ''
}

const getOptionText = (opt: any) => {
  if (typeof opt === 'object' && opt !== null) {
    return opt.text !== undefined ? String(opt.text) : JSON.stringify(opt)
  }
  return String(opt ?? '')
}

onMounted(() => {
  store.startQuiz(topicId)
})

// Navigate when quiz completes
watch(() => store.quiz.completed, (done) => {
  if (done) {
    router.push(`/results/${topicId}`)
  }
})

async function pick(idx: number) {
  if (answered.value) return
  answered.value = true
  selectedIdx.value = idx
  const q = currentQ.value
  if (!q) return

  const targetIdx = correctIndex.value
  isCorrect.value = idx === targetIdx

  if (!isCorrect.value) {
    showMisconception.value = true
    const chosenOpt = q.options?.[idx]
    const rawMisc = typeof chosenOpt === 'object' && chosenOpt ? (chosenOpt.misconception_id || chosenOpt.misconception) : null
    if (rawMisc) {
      diagnosedMisconception.value = String(rawMisc).replace(/_/g, ' ')
    } else {
      diagnosedMisconception.value = null
    }

    try {
      const res = await fetch('/api/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic_id: topicId,
          question_id: q.id,
          chosen_index: idx,
          attempt: 1,
          state: { combo: store.quiz.correctStreak, difficulty: store.quiz.difficulty }
        })
      })
      if (res.ok) {
        const data = await res.json()
        if (data.diagnosis?.kid_label) {
          diagnosedMisconception.value = data.diagnosis.kid_label
        }
      }
    } catch {
      // offline fallback
    }
  }
}

function next() {
  store.submitAnswer(selectedIdx.value!)
  answered.value = false
  selectedIdx.value = null
  isCorrect.value = false
  showMisconception.value = false
  diagnosedMisconception.value = null
}
</script>

<template>
  <div class="quiz-battle">
    <!-- Loading state -->
    <div v-if="!store.quiz.questions.length && !store.quiz.completed" class="loading-state">
      <div class="loading-orb"></div>
      <p class="loading-text font-display">Summoning questions from the arcane vault…</p>
    </div>

    <!-- Quiz UI -->
    <div v-else-if="!store.quiz.completed" class="battle-arena">
      <!-- Progress header -->
      <div class="battle-header">
        <div class="battle-breadcrumb">
          <NuxtLink to="/map" class="back-link">← Realms</NuxtLink>
          <span class="sep">/</span>
          <span class="topic-name">{{ topicId.replace(/-/g, ' ').replace(/g\d /i, '').toUpperCase() }}</span>
        </div>
        <div class="battle-progress">
          <div class="progress-track" role="progressbar" :aria-valuenow="store.quiz.currentIndex + 1" :aria-valuemax="store.quiz.questions.length">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
          <span class="progress-label font-mono">{{ store.quiz.currentIndex + 1 }} / {{ store.quiz.questions.length }}</span>
        </div>
        <div class="score-display">
          <span class="score-icon">⚔️</span>
          <span class="score-val font-display">{{ store.quiz.score }} pts</span>
        </div>
      </div>

      <!-- Question card -->
      <div class="question-card quest-surface-card" v-if="currentQ">
        <div class="question-meta">
          <span class="difficulty-badge" :class="`diff-${store.quiz.difficulty}`">{{ store.quiz.difficulty.toUpperCase() }}</span>
          <span class="q-number font-mono">Q{{ store.quiz.currentIndex + 1 }}</span>
        </div>
        <p class="question-text font-display" v-html="currentQ.stem || currentQ.question"></p>

        <!-- Options -->
        <div class="options-grid">
          <button
            v-for="(opt, i) in currentQ.options"
            :key="i"
            class="option-btn"
            :class="{
              'opt-correct': answered && i === correctIndex,
              'opt-wrong': answered && selectedIdx === i && i !== correctIndex,
              'opt-disabled': answered && i !== correctIndex && i !== selectedIdx
            }"
            :disabled="answered"
            :aria-pressed="selectedIdx === i"
            @click="pick(i)"
          >
            <span class="option-letter">{{ getOptionLetter(opt, i) }}</span>
            <span class="option-text">{{ getOptionText(opt) }}</span>
          </button>
        </div>

        <!-- Feedback -->
        <transition name="fade">
          <div v-if="answered" class="feedback-block" :class="isCorrect ? 'feedback-correct' : 'feedback-wrong'">
            <span class="feedback-icon">{{ isCorrect ? '✅' : '❌' }}</span>
            <div class="feedback-content">
              <p class="feedback-title font-display">{{ isCorrect ? 'Correct! Well struck!' : 'Not quite — the runes resist.' }}</p>
              <p v-if="!isCorrect && currentQ.explanation" class="feedback-explanation">{{ currentQ.explanation }}</p>
            </div>
          </div>
        </transition>

        <!-- Misconception card -->
        <transition name="slide-up">
          <div v-if="showMisconception && (diagnosedMisconception || currentQ.misconception)" class="misconception-card">
            <div class="misconception-header">
              <span class="misc-icon">🔍</span>
              <strong class="misc-title font-display">Common Mistake Detected</strong>
            </div>
            <p class="misc-body">{{ diagnosedMisconception || currentQ.misconception }}</p>
          </div>
        </transition>

        <!-- Next button -->
        <div v-if="answered" class="next-row">
          <button class="btn-next font-display" @click="next">
            {{ store.quiz.currentIndex + 1 < store.quiz.questions.length ? 'Next Question →' : 'See Results →' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Completed redirect -->
    <div v-else class="loading-state">
      <div class="loading-orb"></div>
      <p class="loading-text font-display">Tallying your score…</p>
    </div>
  </div>
</template>

<style scoped>
.quiz-battle {
  min-height: 100vh;
  padding: var(--space-xl) var(--space-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  min-height: 60vh;
}
.loading-orb {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: conic-gradient(var(--quest-gold), transparent, var(--quest-gold));
  animation: spin 1.4s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { color: var(--quest-gold); font-size: 18px; }

/* Battle arena */
.battle-arena {
  width: 100%;
  max-width: 760px;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.battle-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.battle-breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--quest-parchment-muted); }
.back-link { color: var(--quest-gold); text-decoration: none; }
.back-link:hover { text-decoration: underline; }
.topic-name { color: var(--quest-parchment); font-weight: 600; font-size: 12px; letter-spacing: 0.05em; }
.battle-progress { flex: 1; min-width: 160px; display: flex; align-items: center; gap: 10px; }
.progress-track { flex: 1; height: 8px; background: var(--quest-abyss); border-radius: 999px; overflow: hidden; border: 1px solid var(--border-subtle); }
.progress-fill { height: 100%; background: linear-gradient(90deg, #D9B66F, #FFE8B8); border-radius: 999px; transition: width 0.4s ease; }
.progress-label { font-size: 12px; color: var(--quest-parchment-muted); white-space: nowrap; }
.score-display { display: flex; align-items: center; gap: 6px; }
.score-val { font-size: 18px; color: var(--quest-gold); }

/* Question card */
.question-card {
  padding: 28px;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.question-meta { display: flex; align-items: center; justify-content: space-between; }
.difficulty-badge { padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; }
.diff-easy { background: rgba(40,116,91,0.25); color: #7AE0BF; border: 1px solid rgba(40,116,91,0.5); }
.diff-medium { background: rgba(217,182,111,0.2); color: var(--quest-gold); border: 1px solid rgba(217,182,111,0.4); }
.diff-hard { background: rgba(200,60,60,0.2); color: #FF8A8A; border: 1px solid rgba(200,60,60,0.4); }
.q-number { font-size: 12px; color: var(--quest-parchment-muted); }
.question-text { font-size: 20px; color: var(--quest-parchment); line-height: 1.5; }

/* Options */
.options-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 600px) { .options-grid { grid-template-columns: 1fr; } }

.option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(25, 61, 101, 0.4);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment);
  font-size: 15px;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
}
.option-btn:hover:not(:disabled) {
  background: rgba(217,182,111,0.15);
  border-color: var(--quest-gold);
  transform: translateY(-1px);
}
.option-btn:disabled { cursor: default; }
.option-letter {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}
.opt-correct { background: rgba(40,116,91,0.3) !important; border-color: #7AE0BF !important; color: #7AE0BF !important; }
.opt-wrong { background: rgba(200,60,60,0.3) !important; border-color: #FF8A8A !important; color: #FF8A8A !important; }
.opt-disabled { opacity: 0.5; }

/* Feedback */
.feedback-block {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid;
}
.feedback-correct { background: rgba(40,116,91,0.15); border-color: rgba(122,224,191,0.4); }
.feedback-wrong { background: rgba(200,60,60,0.1); border-color: rgba(255,138,138,0.4); }
.feedback-icon { font-size: 20px; flex-shrink: 0; }
.feedback-title { font-size: 15px; color: var(--quest-parchment); }
.feedback-explanation { font-size: 13px; color: var(--quest-parchment-muted); margin-top: 4px; line-height: 1.5; }

/* Misconception card */
.misconception-card {
  background: rgba(217,182,111,0.08);
  border: 1px solid rgba(217,182,111,0.35);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.misconception-header { display: flex; align-items: center; gap: 8px; }
.misc-icon { font-size: 16px; }
.misc-title { font-size: 14px; color: var(--quest-gold); }
.misc-body { font-size: 13px; color: var(--quest-parchment-muted); line-height: 1.55; }

/* Next button */
.next-row { display: flex; justify-content: flex-end; }
.btn-next {
  padding: 12px 28px;
  background: linear-gradient(135deg, #D9B66F, #B8922A);
  border: none;
  border-radius: var(--radius-sm);
  color: #0B1327;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-next:hover { opacity: 0.9; }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-up-enter-active { transition: all 0.35s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(10px); }
</style>
