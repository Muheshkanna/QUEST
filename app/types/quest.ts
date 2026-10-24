export interface StudentProfile {
  name: string
  title: string
  avatar: string
  level: number
  currentXp: number
  xpToNextLevel: number
  totalXp: number
  streakDays: number
  streakShields: number
  equippedTitle: string
}

export type RealmId = 'enchanted-forest' | 'temple-of-wisdom' | 'celestial-frontier'

export interface Realm {
  id: RealmId
  title: string
  subtitle: string
  loreTag: string
  description: string
  curriculum: string
  progressPercent: number
  totalQuests: number
  completedQuests: number
  themeColor: 'emerald' | 'gold' | 'violet'
  icon: string
  unlocked: boolean
  levelReq: number
}

export interface DailyTrial {
  id: string
  realmId: RealmId
  realmName: string
  title: string
  description: string
  xpReward: number
  difficulty: 'Apprentice' | 'Scholar' | 'Archmage'
  question: string
  options: string[]
  correctIndex: number
  explanation: string
  completed: boolean
}

export interface TopicMastery {
  id: string
  name: string
  realmId: RealmId
  masteryLevel: number // 0 to 100
  tier: 'Novice' | 'Adept' | 'Master' | 'Paragon'
  sparkCount: number
}

export interface Achievement {
  id: string
  title: string
  description: string
  icon: string
  unlockedAt?: string
  rarity: 'Common' | 'Rare' | 'Epic' | 'Legendary'
  progress?: { current: number; max: number }
}

export interface ActivityLog {
  id: string
  text: string
  xpGained: number
  timestamp: string
  type: 'quest' | 'streak' | 'achievement' | 'trial'
}
