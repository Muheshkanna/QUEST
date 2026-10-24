<script setup lang="ts">
import type { StudentProfile, Achievement, ActivityLog } from '~/types/quest'

const props = defineProps<{
  student: StudentProfile
  achievements: Achievement[]
  activities: ActivityLog[]
}>()

const getRarityBadge = (rarity: string) => {
  switch (rarity) {
    case 'Legendary': return 'badge-gold'
    case 'Epic': return 'badge-violet'
    case 'Rare': return 'badge-emerald'
    default: return 'badge-common'
  }
}
</script>

<template>
  <aside class="character-codex" aria-label="Student Codex and Achievements">
    <!-- Character Profile Card -->
    <div class="profile-card quest-surface-card">
      <div class="profile-header-decor" />
      
      <div class="profile-body">
        <div class="avatar-hero-ring">
          <span class="avatar-large">{{ student.avatar }}</span>
          <div class="level-seal-overlap">
            <span class="seal-lvl font-display">{{ student.level }}</span>
          </div>
        </div>

        <div class="student-id-block">
          <h3 class="student-hero-name font-display">{{ student.name }}</h3>
          <span class="student-hero-title">{{ student.title }}</span>
          <span class="equipped-honorific">Equipped: "{{ student.equippedTitle }}"</span>
        </div>

        <!-- Overall XP Ledger -->
        <div class="xp-ledger">
          <div class="ledger-row">
            <span class="ledger-label">Cumulative Lore Acquired:</span>
            <span class="ledger-val font-mono text-gold">{{ student.totalXp.toLocaleString() }} XP</span>
          </div>
          <div class="ledger-row">
            <span class="ledger-label">Astral Sun Streak:</span>
            <span class="ledger-val font-mono">🔥 {{ student.streakDays }} Days</span>
          </div>
          <div class="ledger-row">
            <span class="ledger-label">Next Rank Milestone:</span>
            <span class="ledger-val font-mono text-emerald">Level {{ student.level + 1 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Achievements Vault -->
    <div class="achievements-card quest-surface-card">
      <div class="card-header">
        <div class="header-titles">
          <span class="badge badge-gold">Hall of Trophies</span>
          <h3 class="card-title font-display">Recent Milestones</h3>
        </div>
        <span class="achieve-count font-mono">{{ achievements.length }} Badges</span>
      </div>

      <div class="achievements-list">
        <div v-for="ach in achievements" :key="ach.id" class="achieve-item">
          <div class="achieve-icon-frame">
            <span class="achieve-glyph">{{ ach.icon }}</span>
          </div>
          <div class="achieve-info">
            <div class="achieve-top">
              <span class="achieve-title font-display">{{ ach.title }}</span>
              <span class="badge" :class="getRarityBadge(ach.rarity)">{{ ach.rarity }}</span>
            </div>
            <p class="achieve-desc">{{ ach.description }}</p>
            <div v-if="ach.progress" class="achieve-progress-row">
              <span class="progress-lbl font-mono">{{ ach.progress.current }} / {{ ach.progress.max }}</span>
              <div class="ach-track">
                <div class="ach-fill" :style="{ width: `${(ach.progress.current / ach.progress.max) * 100}%` }" />
              </div>
            </div>
            <span v-else-if="ach.unlockedAt" class="unlocked-date">Unlocked {{ ach.unlockedAt }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Activity Chronicle -->
    <div class="activity-card quest-surface-card">
      <div class="card-header">
        <div class="header-titles">
          <span class="badge badge-common">Chronicle</span>
          <h3 class="card-title font-display">Recent Actions</h3>
        </div>
      </div>

      <div class="activity-feed">
        <div v-for="act in activities" :key="act.id" class="activity-entry">
          <span class="entry-bullet" />
          <div class="entry-content">
            <p class="entry-text">{{ act.text }}</p>
            <div class="entry-meta">
              <span class="entry-xp font-mono">+{{ act.xpGained }} XP</span>
              <span class="entry-time">{{ act.timestamp }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.character-codex {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.profile-card {
  overflow: hidden;
  position: relative;
  border: 1px solid var(--border-medium);
}

.profile-header-decor {
  height: 60px;
  background: linear-gradient(135deg, rgba(25, 61, 101, 0.9) 0%, rgba(156, 138, 214, 0.4) 100%);
  border-bottom: 1px solid var(--border-subtle);
}

.profile-body {
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14px;
}

.avatar-hero-ring {
  position: relative;
  margin-top: -36px;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--quest-abyss);
  border: 2px solid var(--quest-gold);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px var(--quest-gold-glow);
}

.avatar-large {
  font-size: 36px;
}

.level-seal-overlap {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: linear-gradient(135deg, var(--quest-gold), var(--quest-gold-muted));
  color: var(--quest-midnight);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.4);
}

.seal-lvl {
  font-size: 11px;
  font-weight: 800;
}

.student-id-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.student-hero-name {
  font-size: 18px;
  color: var(--quest-parchment);
}

.student-hero-title {
  font-size: 12px;
  color: var(--quest-gold);
  font-weight: 600;
}

.equipped-honorific {
  font-size: 11px;
  color: var(--quest-parchment-muted);
  font-style: italic;
  margin-top: 2px;
}

.xp-ledger {
  width: 100%;
  background: rgba(11, 19, 39, 0.6);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
}

.ledger-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.ledger-label {
  color: var(--quest-parchment-muted);
}

.ledger-val {
  font-weight: 700;
  color: var(--quest-parchment);
}

.text-gold {
  color: var(--quest-gold);
}

.text-emerald {
  color: #7AE0BF;
}

/* Achievements */
.achievements-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-size: 16px;
  color: var(--quest-parchment);
}

.achieve-count {
  font-size: 11px;
  color: var(--quest-parchment-muted);
}

.achievements-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.achieve-item {
  display: flex;
  gap: 12px;
  background: rgba(11, 19, 39, 0.45);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px;
  align-items: flex-start;
}

.achieve-icon-frame {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: rgba(25, 61, 101, 0.6);
  border: 1px solid var(--border-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.achieve-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.achieve-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.achieve-title {
  font-size: 13px;
  color: var(--quest-parchment);
  font-weight: 700;
}

.achieve-desc {
  font-size: 11px;
  color: var(--quest-parchment-muted);
  line-height: 1.4;
}

.achieve-progress-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.progress-lbl {
  font-size: 10px;
  color: var(--quest-gold);
}

.ach-track {
  flex: 1;
  height: 4px;
  background: var(--quest-abyss);
  border-radius: 2px;
  overflow: hidden;
}

.ach-fill {
  height: 100%;
  background: var(--quest-gold);
}

.unlocked-date {
  font-size: 10px;
  color: #7AE0BF;
  font-style: italic;
  margin-top: 2px;
}

/* Activity */
.activity-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.activity-feed {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-entry {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.entry-bullet {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--quest-gold);
  margin-top: 6px;
  box-shadow: 0 0 6px var(--quest-gold);
}

.entry-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.entry-text {
  font-size: 12px;
  color: var(--quest-parchment);
  line-height: 1.4;
}

.entry-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
}

.entry-xp {
  color: var(--quest-gold);
  font-weight: 700;
}

.entry-time {
  color: var(--quest-parchment-faint);
}
</style>
