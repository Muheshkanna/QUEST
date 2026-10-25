import { defineStore } from 'pinia'
import { defaultStudent, defaultRealms, defaultDailyTrial, defaultTopicMasteries, defaultAchievements, defaultActivityLogs } from '../app/composables/useQuestData'

export const useGameStore = defineStore('game', {
  state: () => ({
    // Core data
    student: { ...defaultStudent },
    realms: [...defaultRealms],
    dailyTrial: { ...defaultDailyTrial },
    topicMasteries: [...defaultTopicMasteries],
    achievements: [...defaultAchievements],
    activities: [...defaultActivityLogs],

    // UI navigation
    activeNav: 'command-center', // command-center | realms | codex | achievements | quiz | results
    selectedRealmId: 'temple-of-wisdom',
    selectedTopic: null as any,
    selectedQuizId: null as string | null,

    // Quiz state
    quiz: {
      questions: [] as any[],
      currentIndex: 0,
      correctStreak: 0,
      difficulty: 'medium' as 'easy' | 'medium' | 'hard',
      score: 0,
      lastMisconception: null as any,
      completed: false
    },

    // Misc
    isLoaded: false,
    notification: null as null | { title: string; message: string; xp?: number },
    version: 1
  }),
  getters: {
    selectedRealm(state) {
      return state.realms.find(r => r.id === state.selectedRealmId) || state.realms[0]
    }
  },
  actions: {
    initFromStorage() {
      if (typeof window === 'undefined') return
      const STORAGE_KEY = 'quest_command_center_state_v2'
      try {
        const stored = localStorage.getItem(STORAGE_KEY)
        if (stored) {
          const parsed = JSON.parse(stored)
          if (parsed.student) this.student = parsed.student
          if (parsed.realms) this.realms = parsed.realms
          if (parsed.dailyTrial) this.dailyTrial = { ...defaultDailyTrial, completed: Boolean(parsed.dailyTrial.completed) }
          if (parsed.topicMasteries) this.topicMasteries = parsed.topicMasteries
          if (parsed.achievements) this.achievements = parsed.achievements
          if (parsed.activities) this.activities = parsed.activities
        }
      } catch (e) {
        console.warn('Failed to parse quest storage', e)
      } finally {
        this.isLoaded = true
      }
    },
    persistToStorage() {
      if (typeof window === 'undefined') return
      const STORAGE_KEY = 'quest_command_center_state_v2'
      try {
        const payload = {
          student: this.student,
          realms: this.realms,
          dailyTrial: this.dailyTrial,
          topicMasteries: this.topicMasteries,
          achievements: this.achievements,
          activities: this.activities
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
      } catch (e) {
        console.warn('Failed to save to storage', e)
      }
    },
    awardXp(amount: number, reason: string) {
      this.student.currentXp += amount
      this.student.totalXp += amount
      let leveledUp = false
      while (this.student.currentXp >= this.student.xpToNextLevel) {
        this.student.currentXp -= this.student.xpToNextLevel
        this.student.level += 1
        this.student.xpToNextLevel = Math.round(this.student.xpToNextLevel * 1.25)
        leveledUp = true
      }
      this.activities.unshift({
        id: 'log-' + Date.now(),
        text: reason,
        xpGained: amount,
        timestamp: 'Just now',
        type: leveledUp ? 'quest' : 'trial'
      })
      if (this.activities.length > 8) this.activities = this.activities.slice(0, 8)
      this.notification = {
        title: leveledUp ? `LEVEL UP! Attained Level ${this.student.level}` : 'Victory! XP Awarded',
        message: `${reason} (+${amount} XP)`,
        xp: amount
      }
      setTimeout(() => (this.notification = null), 4500)
      this.persistToStorage()
    },
    submitDailyTrial(selectedOptionIndex: number) {
      if (this.dailyTrial.completed) {
        return { success: true, explanation: this.dailyTrial.explanation }
      }
      if (selectedOptionIndex === this.dailyTrial.correctIndex) {
        this.dailyTrial.completed = true
        this.awardXp(this.dailyTrial.xpReward, `Solved Daily Trial: "${this.dailyTrial.title}"`)
        this.persistToStorage()
        return { success: true, explanation: this.dailyTrial.explanation }
      }
      return { success: false, explanation: 'The runes resist. Review the sequence rule and try again!' }
    },
    continueAdventure() {
      const activeRealm = this.realms.find(r => r.id === this.selectedRealmId) || this.realms[0]
      const xpGain = 120
      if (activeRealm.completedQuests < activeRealm.totalQuests) {
        activeRealm.completedQuests += 1
        activeRealm.progressPercent = Math.min(100, Math.round((activeRealm.completedQuests / activeRealm.totalQuests) * 100))
      }
      this.awardXp(xpGain, `Conquered chamber milestone in ${activeRealm.title}`)
      this.persistToStorage()
    },
    resetDemoState() {
      this.student = { ...defaultStudent }
      this.realms = [...defaultRealms]
      this.dailyTrial = { ...defaultDailyTrial }
      this.topicMasteries = [...defaultTopicMasteries]
      this.achievements = [...defaultAchievements]
      this.activities = [...defaultActivityLogs]
      if (typeof window !== 'undefined') {
        localStorage.removeItem('quest_command_center_state_v2')
        localStorage.removeItem('quest_command_center_state_v1')
      }
      this.notification = { title: 'State Purged', message: 'Demo state reset to original default lore.' }
      setTimeout(() => (this.notification = null), 3000)
    },
    setGrade(grade: 5 | 6) {
      this.student.grade = grade
      this.persistToStorage()
    },
    // ----- Quiz workflow -----
    async startQuiz(topicId: string) {
      this.activeNav = 'quiz'
      this.selectedTopic = { id: topicId }
      this.quiz = { questions: [], currentIndex: 0, correctStreak: 0, difficulty: 'medium', score: 0, lastMisconception: null, completed: false }
      try {
        const res = await fetch(`/api/questions?topic=${topicId}`)
        if (res.ok) {
          const data = await res.json()
          this.quiz.questions = data.questions?.slice(0, 10) || []
        }
      } catch (e) {
        this.quiz.questions = []
      }
    },
    submitAnswer(optionIndex: number) {
      const q = this.quiz.questions[this.quiz.currentIndex]
      if (!q) return
      const correct = optionIndex === q.correctIndex
      if (correct) {
        this.quiz.score += 10
        this.quiz.correctStreak += 1
        if (this.quiz.correctStreak >= 2 && this.quiz.difficulty !== 'hard') {
          this.quiz.difficulty = this.quiz.difficulty === 'easy' ? 'medium' : 'hard'
          this.quiz.correctStreak = 0
        }
      } else {
        this.quiz.lastMisconception = q.misconception || null
        this.quiz.correctStreak = 0
        if (this.quiz.difficulty === 'hard') this.quiz.difficulty = 'medium'
        else if (this.quiz.difficulty === 'medium') this.quiz.difficulty = 'easy'
      }
      // Advance to next question or finish
      if (this.quiz.currentIndex + 1 < this.quiz.questions.length && this.quiz.questions.length < 10) {
        this.quiz.currentIndex += 1
      } else {
        this.quiz.completed = true
        this.activeNav = 'results'
        const xp = this.quiz.score * 5
        this.awardXp(xp, `Completed Quiz on ${this.selectedTopic.id}`)
      }
    },
    // Simple badge unlock helper
    unlockBadge(badgeId: string) {
      if (!this.achievements.find((a: any) => a.id === badgeId)) {
        this.achievements.push({ id: badgeId, title: badgeId, description: '', icon: '', unlockedAt: new Date().toISOString(), rarity: 'Common' })
        this.persistToStorage()
      }
    }
  }
})
