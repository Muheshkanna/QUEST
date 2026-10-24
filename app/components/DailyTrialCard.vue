<script setup lang="ts">
import { ref } from 'vue'
import type { DailyTrial } from '~/types/quest'

const props = defineProps<{
  trial: DailyTrial
}>()

const emit = defineEmits<{
  (e: 'solve', optionIndex: number): void
}>()

const selectedOption = ref<number | null>(null)
const feedback = ref<{ success: boolean; explanation: string } | null>(null)

const handleOptionClick = (index: number) => {
  if (props.trial.completed) return
  selectedOption.value = index
}

const handleVerify = () => {
  if (selectedOption.value === null || props.trial.completed) return
  emit('solve', selectedOption.value)
  if (selectedOption.value === props.trial.correctIndex) {
    feedback.value = {
      success: true,
      explanation: props.trial.explanation
    }
  } else {
    feedback.value = {
      success: false,
      explanation: 'The ancient keystone rejects this sequence! Examine the rule: multiply by 2, then add 1.'
    }
  }
}
</script>

<template>
  <div class="trial-card quest-surface-card" :class="{ 'is-completed': trial.completed }">
    <!-- Header -->
    <div class="trial-header">
      <div class="trial-meta-left">
        <span class="badge badge-gold">Daily Crucible</span>
        <span class="badge badge-epic">{{ trial.difficulty }}</span>
        <span class="trial-realm-tag">📍 {{ trial.realmName }}</span>
      </div>
      <div class="trial-reward">
        <span class="reward-spark">✨</span>
        <span class="reward-xp font-mono">+{{ trial.xpReward }} XP</span>
      </div>
    </div>

    <!-- Title & Lore -->
    <div class="trial-body">
      <h3 class="trial-title font-display">{{ trial.title }}</h3>
      <p class="trial-desc">{{ trial.description }}</p>

      <!-- Question Box -->
      <div class="question-container">
        <span class="question-label">Arcane Inscription:</span>
        <p class="question-text font-mono">{{ trial.question }}</p>
      </div>

      <!-- Multiple Choice Options -->
      <div class="options-grid" role="radiogroup" aria-label="Trial Answer Options">
        <button
          v-for="(opt, idx) in trial.options"
          :key="idx"
          type="button"
          role="radio"
          :aria-checked="selectedOption === idx"
          class="option-pill"
          :class="{
            'is-selected': selectedOption === idx,
            'is-correct': trial.completed && idx === trial.correctIndex,
            'is-disabled': trial.completed
          }"
          :disabled="trial.completed"
          @click="handleOptionClick(idx)"
          @keydown.enter.space.prevent="handleOptionClick(idx)"
        >
          <span class="option-glyph font-mono">
            {{ ['A', 'B', 'C', 'D'][idx] }}
          </span>
          <span class="option-val font-mono">{{ opt }}</span>
        </button>
      </div>

      <!-- Feedback / Resolution Message -->
      <div v-if="feedback || trial.completed" class="trial-feedback" :class="trial.completed ? 'feedback-success' : 'feedback-error'">
        <span class="feedback-icon">{{ trial.completed ? '🏆' : '⚠️' }}</span>
        <div class="feedback-content">
          <strong>{{ trial.completed ? 'Trial Conquered!' : 'Harmonic Discrepancy' }}</strong>
          <p>{{ trial.completed ? trial.explanation : feedback?.explanation }}</p>
        </div>
      </div>
    </div>

    <!-- Footer Action -->
    <div class="trial-footer">
      <button
        v-if="!trial.completed"
        type="button"
        class="btn-gold"
        :disabled="selectedOption === null"
        @click="handleVerify"
      >
        <span>Engrave Solution</span>
        <span aria-hidden="true">→</span>
      </button>
      <div v-else class="completed-seal">
        <span class="seal-icon">✨</span>
        <span>Runestone Solved for Today (+{{ trial.xpReward }} XP Claimed)</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trial-card {
  padding: 24px;
  border: 1px solid rgba(217, 182, 111, 0.35);
  background: linear-gradient(135deg, rgba(25, 61, 101, 0.6) 0%, rgba(16, 27, 53, 0.8) 100%);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  position: relative;
  overflow: hidden;
  margin-bottom: var(--space-xl);
}

.trial-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(156, 138, 214, 0.15), transparent 70%);
  pointer-events: none;
}

.trial-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.trial-meta-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trial-realm-tag {
  font-size: 11px;
  color: var(--quest-parchment-muted);
}

.trial-reward {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(217, 182, 111, 0.15);
  border: 1px solid var(--quest-gold);
  padding: 3px 10px;
  border-radius: var(--radius-full);
}

.reward-spark {
  font-size: 13px;
}

.reward-xp {
  font-size: 12px;
  font-weight: 700;
  color: var(--quest-gold);
}

.trial-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.trial-title {
  font-size: 18px;
  color: var(--quest-parchment);
}

.trial-desc {
  font-size: 13px;
  color: var(--quest-parchment-muted);
  line-height: 1.5;
}

.question-container {
  background: rgba(11, 19, 39, 0.7);
  border-left: 3px solid var(--quest-gold);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.question-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--quest-gold);
  font-weight: 700;
}

.question-text {
  font-size: 14px;
  color: var(--quest-parchment);
  font-weight: 600;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 4px;
}

.option-pill {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(25, 61, 101, 0.4);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  color: var(--quest-parchment);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.option-pill:hover:not(:disabled) {
  background: rgba(35, 82, 136, 0.65);
  border-color: var(--quest-gold);
}

.option-pill:focus-visible {
  outline: 2px solid var(--quest-gold);
  outline-offset: 2px;
}

.option-pill.is-selected {
  background: rgba(217, 182, 111, 0.15);
  border-color: var(--quest-gold);
  box-shadow: 0 0 10px rgba(217, 182, 111, 0.2);
}

.option-pill.is-correct {
  background: rgba(40, 116, 91, 0.3);
  border-color: #28745B;
  color: #7AE0BF;
}

.option-glyph {
  font-size: 12px;
  font-weight: 700;
  color: var(--quest-gold);
  background: rgba(11, 19, 39, 0.6);
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-val {
  font-size: 14px;
  font-weight: 700;
}

.option-pill.is-correct .option-glyph {
  color: #7AE0BF;
}

.trial-feedback {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  line-height: 1.5;
}

.feedback-success {
  background: rgba(40, 116, 91, 0.25);
  border: 1px solid var(--quest-emerald);
  color: #7AE0BF;
}

.feedback-error {
  background: rgba(184, 50, 50, 0.2);
  border: 1px solid #d9534f;
  color: #ffb8b8;
}

.feedback-icon {
  font-size: 18px;
}

.trial-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid var(--border-subtle);
}

.completed-seal {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7AE0BF;
  font-size: 13px;
  font-weight: 600;
}

@media (max-width: 640px) {
  .options-grid {
    grid-template-columns: 1fr;
  }
}
</style>
