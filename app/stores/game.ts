import { defineStore } from 'pinia'
import { defaultStudent, defaultRealms, defaultDailyTrial, defaultTopicMasteries, defaultAchievements, defaultActivityLogs } from '../composables/useQuestData'

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
    pendingNav: null as string | null,
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
      // Clear legacy keys
      localStorage.removeItem('quest_command_center_state_v1')
      localStorage.removeItem('quest_state')
      try {
        const stored = localStorage.getItem(STORAGE_KEY)
        if (stored) {
          const parsed = JSON.parse(stored)
          // Always merge with defaults so no field is ever undefined
          if (parsed.student && typeof parsed.student === 'object') {
            this.student = { ...defaultStudent, ...parsed.student }
          }
          if (Array.isArray(parsed.realms)) this.realms = parsed.realms
          if (parsed.dailyTrial) this.dailyTrial = { ...defaultDailyTrial, completed: Boolean(parsed.dailyTrial.completed) }
          if (Array.isArray(parsed.topicMasteries)) {
            // Filter out corrupt entries missing topicId
            this.topicMasteries = parsed.topicMasteries.filter((m: any) => m && typeof m.topicId === 'string')
          }
          if (Array.isArray(parsed.achievements)) this.achievements = parsed.achievements
          if (Array.isArray(parsed.activities)) this.activities = parsed.activities
        }
      } catch (e) {
        console.warn('Quest storage corrupt — resetting', e)
        localStorage.removeItem(STORAGE_KEY)
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

      // Automatically sync name, grade, and progression to SQLite database
      if (this.student?.name && this.student.name.trim()) {
        fetch('/api/user', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.student.name.trim(),
            grade: this.student.grade || 5,
            level: this.student.level || 1,
            currentXp: this.student.currentXp || 0,
            xpToNextLevel: this.student.xpToNextLevel || 1000,
            totalXp: this.student.totalXp || 0,
            streakDays: this.student.streakDays || 0,
            streakShields: this.student.streakShields || 0,
            equippedTitle: this.student.equippedTitle || 'Seeker Initiate',
            state: {
              topicMasteries: this.topicMasteries,
              achievements: this.achievements,
              activities: this.activities
            }
          })
        }).catch(() => {})
      }
    },
    async loadUserFromDb(name: string): Promise<{ exists: boolean; user: any | null }> {
      const clean = name.trim()
      if (!clean) return { exists: false, user: null }
      try {
        const res = await fetch(`/api/user?name=${encodeURIComponent(clean)}`)
        if (res.ok) {
          const data = await res.json()
          if (data.exists && data.user) {
            const u = data.user
            this.student.name = u.name
            this.student.grade = u.grade === 6 ? 6 : 5
            this.student.level = u.level || 1
            this.student.currentXp = u.currentXp || 0
            this.student.xpToNextLevel = u.xpToNextLevel || 1000
            this.student.totalXp = u.totalXp || 0
            this.student.streakDays = u.streakDays || 0
            this.student.streakShields = u.streakShields || 0
            this.student.equippedTitle = u.equippedTitle || 'Seeker Initiate'
            if (u.state) {
              if (Array.isArray(u.state.topicMasteries)) this.topicMasteries = u.state.topicMasteries
              if (Array.isArray(u.state.achievements)) this.achievements = u.state.achievements
              if (Array.isArray(u.state.activities)) this.activities = u.state.activities
            }
            if (typeof window !== 'undefined') {
              const STORAGE_KEY = 'quest_command_center_state_v2'
              const payload = {
                student: this.student,
                realms: this.realms,
                dailyTrial: this.dailyTrial,
                topicMasteries: this.topicMasteries,
                achievements: this.achievements,
                activities: this.activities
              }
              localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
            }
            return { exists: true, user: u }
          }
        }
      } catch (err) {
        console.warn('Failed to load user from database', err)
      }
      return { exists: false, user: null }
    },
    async loginUser(name: string, password: string): Promise<{ success: boolean; user?: any; error?: string }> {
      try {
        const res = await fetch('/api/user/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name.trim(), password })
        })
        const data = await res.json()
        if (res.ok && data.success && data.user) {
          const u = data.user
          this.student.name = u.name
          this.student.grade = u.grade === 6 ? 6 : 5
          this.student.level = u.level || 1
          this.student.currentXp = u.currentXp || 0
          this.student.xpToNextLevel = u.xpToNextLevel || 1000
          this.student.totalXp = u.totalXp || 0
          this.student.streakDays = u.streakDays || 0
          this.student.streakShields = u.streakShields || 0
          this.student.equippedTitle = u.equippedTitle || 'Seeker Initiate'
          if (u.state) {
            if (Array.isArray(u.state.topicMasteries)) this.topicMasteries = u.state.topicMasteries
            if (Array.isArray(u.state.achievements)) this.achievements = u.state.achievements
            if (Array.isArray(u.state.activities)) this.activities = u.state.activities
          }
          this.persistToStorage()
          return { success: true, user: u }
        }
        return { success: false, error: data.error?.message || 'Invalid scholar credentials' }
      } catch (err: any) {
        return { success: false, error: err.message || 'Login failed. Please check network connection.' }
      }
    },
    async registerUser(name: string, password: string, grade: 5 | 6): Promise<{ success: boolean; user?: any; error?: string }> {
      try {
        const res = await fetch('/api/user/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name.trim(), password, grade })
        })
        const data = await res.json()
        if (res.ok && data.success && data.user) {
          const u = data.user
          this.student.name = u.name
          this.student.grade = grade
          this.student.level = 1
          this.student.currentXp = 0
          this.student.xpToNextLevel = 1000
          this.student.totalXp = 0
          this.student.streakDays = 0
          this.student.streakShields = 0
          this.student.equippedTitle = 'Seeker Initiate'
          this.topicMasteries = []
          this.achievements = []
          this.activities = []
          this.persistToStorage()
          return { success: true, user: u }
        }
        return { success: false, error: data.error?.message || 'Registration failed' }
      } catch (err: any) {
        return { success: false, error: err.message || 'Registration failed. Please check network connection.' }
      }
    },
    switchScholar() {
      this.student.name = ''
      if (typeof window !== 'undefined') {
        const STORAGE_KEY = 'quest_command_center_state_v2'
        localStorage.removeItem(STORAGE_KEY)
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
    continueAdventure(topicId?: string) {
      // Stores the nav target; page watches quiz.completed and navigates
      this.pendingNav = topicId ? `/lesson/${topicId}` : '/map'
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
    async startQuiz(topicId: string) {
      this.activeNav = 'quiz'
      this.selectedTopic = { id: topicId }
      this.quiz = { questions: [], currentIndex: 0, correctStreak: 0, difficulty: 'medium', score: 0, lastMisconception: null, completed: false }
      try {
        const res = await fetch(`/api/questions?topic=${topicId}`)
        if (res.ok) {
          const data = await res.json()
          const raw = Array.isArray(data.questions) ? data.questions : []
          this.quiz.questions = raw.map((q: any) => ({
            ...q,
            stem: q.stem || q.question || '',
            question: q.stem || q.question || '',
            correctIndex: q.correct_index !== undefined ? q.correct_index : (q.correctIndex ?? 0),
            correct_index: q.correct_index !== undefined ? q.correct_index : (q.correctIndex ?? 0),
            options: (q.options || []).map((opt: any, idx: number) => {
              if (typeof opt === 'string') {
                return { id: ['A', 'B', 'C', 'D'][idx], text: opt, misconception_id: null }
              }
              return {
                id: opt.id || ['A', 'B', 'C', 'D'][idx],
                text: opt.text !== undefined ? String(opt.text) : String(opt),
                misconception_id: opt.misconception_id || opt.misconception || null
              }
            })
          })).slice(0, 10)
        }
      } catch (e) {
        this.quiz.questions = []
      }
    },
    submitAnswer(optionIndex: number) {
      const q = this.quiz.questions[this.quiz.currentIndex]
      if (!q) return
      const targetCorrectIdx = q.correct_index !== undefined ? q.correct_index : q.correctIndex
      const correct = optionIndex === targetCorrectIdx
      if (correct) {
        this.quiz.score += 10
        this.quiz.correctStreak += 1
        if (this.quiz.correctStreak >= 2 && this.quiz.difficulty !== 'hard') {
          this.quiz.difficulty = this.quiz.difficulty === 'easy' ? 'medium' : 'hard'
          this.quiz.correctStreak = 0
        }
      } else {
        const chosenOpt = q.options?.[optionIndex]
        const misc = (typeof chosenOpt === 'object' && chosenOpt ? (chosenOpt.misconception_id || chosenOpt.misconception) : null) || q.misconception || null
        this.quiz.lastMisconception = misc
        this.quiz.correctStreak = 0
        if (this.quiz.difficulty === 'hard') this.quiz.difficulty = 'medium'
        else if (this.quiz.difficulty === 'medium') this.quiz.difficulty = 'easy'
      }
      if (this.quiz.currentIndex + 1 < this.quiz.questions.length) {
        this.quiz.currentIndex += 1
        this.quiz.lastMisconception = null
      } else {
        this.quiz.completed = true
        const xp = this.quiz.score * 5
        const topicTitle = this.selectedTopic?.id ?? 'topic'
        this.awardXp(xp, `Completed Quiz on ${topicTitle}`)
        this.checkBadges(topicTitle)
        this.persistToStorage()
      }
    },
    checkBadges(topicId: string) {
      // Badge 1: First Quest — complete any quiz
      this.unlockBadge('first-quest')
      // Badge 2: Perfect Score
      if (this.quiz.score >= 100) this.unlockBadge('perfect-score')
      // Badge 3: Fraction Master
      if (topicId.includes('fraction')) this.unlockBadge('fraction-master')
      // Badge 4: Speed Demon — answered 10 questions (score > 50 means got more than half right)
      if (this.quiz.score > 50) this.unlockBadge('scholar')
      // Badge 5: Veteran — 5+ quizzes completed
      const quizCount = (this.topicMasteries?.length || 0) + 1
      if (quizCount >= 5) this.unlockBadge('veteran')
      // Badge 6: Completionist — check if all topics for grade are done
      // (simplified: if bestScore exists for 10+ topics)
      if (this.topicMasteries.filter((m: any) => m.bestScore >= 50).length >= 10) this.unlockBadge('completionist')
      // Update topic mastery
      const existing = this.topicMasteries.find((m: any) => m.topicId === topicId)
      if (existing) {
        if (this.quiz.score > existing.bestScore) existing.bestScore = this.quiz.score
        existing.attempts += 1
      } else {
        this.topicMasteries.push({ topicId, attempts: 1, bestScore: this.quiz.score })
      }
    },
    unlockBadge(badgeId: string) {
      if (!this.achievements.find((a: any) => a.id === badgeId)) {
        this.achievements.push({ id: badgeId, title: badgeId, description: '', icon: '', unlockedAt: new Date().toISOString(), rarity: 'Common' })
        this.persistToStorage()
      }
    }
  }
})
