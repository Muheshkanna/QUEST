import { ref, computed } from 'vue'
import type { StudentProfile, Realm, DailyTrial, TopicMastery, Achievement, ActivityLog } from '~/types/quest'
import {
  defaultStudent,
  defaultRealms,
  defaultDailyTrial,
  defaultTopicMasteries,
  defaultAchievements,
  defaultActivityLogs
} from './useQuestData'

const STORAGE_KEY = 'quest_command_center_state_v2'

export const useQuestState = () => {
  const student = ref<StudentProfile>({ ...defaultStudent })
  const realms = ref<Realm[]>([...defaultRealms])
  const dailyTrial = ref<DailyTrial>({ ...defaultDailyTrial })
  const topicMasteries = ref<TopicMastery[]>([...defaultTopicMasteries])
  const achievements = ref<Achievement[]>([...defaultAchievements])
  const activities = ref<ActivityLog[]>([...defaultActivityLogs])

  const selectedRealmId = ref<string>('temple-of-wisdom')
  const isLoaded = ref<boolean>(false)
  const notification = ref<{ title: string; message: string; xp?: number } | null>(null)

  // Hydrate safely on client
  const initFromStorage = () => {
    if (typeof window === 'undefined') return
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        if (parsed.student) student.value = parsed.student
        if (parsed.realms) realms.value = parsed.realms
        if (parsed.dailyTrial) {
          // Keep canonical mathematical explanation if trial is not finished, or preserve completed status
          dailyTrial.value = {
            ...defaultDailyTrial,
            completed: Boolean(parsed.dailyTrial.completed)
          }
        }
        if (parsed.topicMasteries) topicMasteries.value = parsed.topicMasteries
        if (parsed.achievements) achievements.value = parsed.achievements
        if (parsed.activities) activities.value = parsed.activities
      }
    } catch (e) {
      console.warn('Failed to parse quest storage', e)
    } finally {
      isLoaded.value = true
    }
  }

  const persistToStorage = () => {
    if (typeof window === 'undefined') return
    try {
      const payload = {
        student: student.value,
        realms: realms.value,
        dailyTrial: dailyTrial.value,
        topicMasteries: topicMasteries.value,
        achievements: achievements.value,
        activities: activities.value
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    } catch (e) {
      console.warn('Failed to save to storage', e)
    }
  }

  // Award XP and handle level up
  const awardXp = (amount: number, reason: string) => {
    student.value.currentXp += amount
    student.value.totalXp += amount

    // Check level up
    let leveledUp = false
    while (student.value.currentXp >= student.value.xpToNextLevel) {
      student.value.currentXp -= student.value.xpToNextLevel
      student.value.level += 1
      student.value.xpToNextLevel = Math.round(student.value.xpToNextLevel * 1.25)
      leveledUp = true
    }

    // Add activity log
    activities.value.unshift({
      id: 'log-' + Date.now(),
      text: reason,
      xpGained: amount,
      timestamp: 'Just now',
      type: leveledUp ? 'quest' : 'trial'
    })

    if (activities.value.length > 8) {
      activities.value = activities.value.slice(0, 8)
    }

    notification.value = {
      title: leveledUp ? `LEVEL UP! Attained Level ${student.value.level}` : 'Victory! XP Awarded',
      message: `${reason} (+${amount} XP)`,
      xp: amount
    }

    setTimeout(() => {
      notification.value = null
    }, 4500)

    persistToStorage()
  }

  // Complete the daily trial safely: idempotently checks dailyTrial.completed
  const submitDailyTrial = (selectedOptionIndex: number): { success: boolean; explanation: string } => {
    if (dailyTrial.value.completed) {
      return { success: true, explanation: dailyTrial.value.explanation }
    }

    if (selectedOptionIndex === dailyTrial.value.correctIndex) {
      dailyTrial.value.completed = true
      awardXp(dailyTrial.value.xpReward, `Solved Daily Trial: "${dailyTrial.value.title}"`)
      persistToStorage()
      return { success: true, explanation: dailyTrial.value.explanation }
    } else {
      return {
        success: false,
        explanation: 'The runes resist. Review the sequence formula (multiply by 2, then add 1) and test another value!'
      }
    }
  }

  // Continue Adventure: advances quest on the active realm
  const continueAdventure = () => {
    const activeRealm = realms.value.find((r) => r.id === selectedRealmId.value) || realms.value[0]
    const xpGain = 120
    if (activeRealm.completedQuests < activeRealm.totalQuests) {
      activeRealm.completedQuests += 1
      activeRealm.progressPercent = Math.min(100, Math.round((activeRealm.completedQuests / activeRealm.totalQuests) * 100))
    }
    awardXp(xpGain, `Conquered chamber milestone in ${activeRealm.title}`)
    persistToStorage()
  }

  // Reset state to defaults
  const resetDemoState = () => {
    student.value = { ...defaultStudent }
    realms.value = [...defaultRealms]
    dailyTrial.value = { ...defaultDailyTrial }
    topicMasteries.value = [...defaultTopicMasteries]
    achievements.value = [...defaultAchievements]
    activities.value = [...defaultActivityLogs]
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem('quest_command_center_state_v1')
    }
    notification.value = {
      title: 'State Purged',
      message: 'Demo state reset to original default lore.'
    }
    setTimeout(() => {
      notification.value = null
    }, 3000)
  }

  const selectedRealm = computed(() => {
    return realms.value.find((r) => r.id === selectedRealmId.value) || realms.value[0]
  })

  return {
    student,
    realms,
    dailyTrial,
    topicMasteries,
    achievements,
    activities,
    selectedRealmId,
    selectedRealm,
    notification,
    isLoaded,
    initFromStorage,
    persistToStorage,
    awardXp,
    submitDailyTrial,
    continueAdventure,
    resetDemoState
  }
}
