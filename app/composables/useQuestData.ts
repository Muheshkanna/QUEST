import type { StudentProfile, Realm, DailyTrial, TopicMastery, Achievement, ActivityLog } from '~/types/quest'

export const defaultStudent: StudentProfile = {
  name: '',
  title: '',
  avatar: '',
  level: 1,
  currentXp: 0,
  xpToNextLevel: 1000,
  totalXp: 0,
  streakDays: 0,
  streakShields: 0,
  equippedTitle: '',
  grade: 5
}

export const defaultRealms: Realm[] = [
  {
    id: 'enchanted-forest',
    title: 'The Enchanted Forest',
    subtitle: 'Verdant Archives of the First Sprouts',
    loreTag: 'Living Arithmetic & Natural Growth',
    description: 'Master the delicate balances of fractions, decimals, and proportions woven into the roots of ancient trees.',
    curriculum: 'Fractions, Decimals, Ratios & Percentages',
    progressPercent: 0,
    totalQuests: 24,
    completedQuests: 0,
    themeColor: 'emerald',
    icon: '🌿',
    unlocked: true,
    levelReq: 1
  },
  {
    id: 'temple-of-wisdom',
    title: 'The Temple of Wisdom',
    subtitle: 'The Sunken Halls of Axioms',
    loreTag: 'Architectural Logic & Pure Geometry',
    description: 'Decipher sacred geometry, polygonal symmetry, and hidden sequence keys left by the first grand architect.',
    curriculum: 'Geometry, Angle Laws, Coordinate Planes & Number Patterns',
    progressPercent: 0,
    totalQuests: 30,
    completedQuests: 0,
    themeColor: 'gold',
    icon: '🏛️',
    unlocked: true,
    levelReq: 3
  },
  {
    id: 'celestial-frontier',
    title: 'The Celestial Frontier',
    subtitle: 'The Astral Forge of Stellar Architects',
    loreTag: 'Cosmic Equations & Infinite Dimensions',
    description: 'Chart stellar trajectories through algebraic functions, exponents, and cosmic coordinate systems.',
    curriculum: 'Algebraic Equations, Linear Graphs, Exponents & Complex Logic',
    progressPercent: 0,
    totalQuests: 28,
    completedQuests: 0,
    themeColor: 'violet',
    icon: '✨',
    unlocked: true,
    levelReq: 5
  }
]

export const defaultDailyTrial: DailyTrial = {
  id: 'trial-2026-10-24',
  realmId: 'temple-of-wisdom',
  realmName: 'Temple of Wisdom',
  title: 'Trial of the Hidden Pattern',
  description: 'An ancient keystone requires the missing term to balance its numerical sequence.',
  xpReward: 350,
  difficulty: 'Scholar',
  question: 'In the sequence: 3, 7, 15, 31, __, what is the next harmonious value?',
  options: ['47', '55', '63', '65'],
  correctIndex: 2,
  explanation: 'The sequence follows the rule: multiply by 2, then add 1. Specifically: 3×2+1=7, 7×2+1=15, 15×2+1=31, and 31×2+1=63.',
  completed: false
}

export const defaultTopicMasteries: TopicMastery[] = []

export const defaultAchievements: Achievement[] = []

export const defaultActivityLogs: ActivityLog[] = []
