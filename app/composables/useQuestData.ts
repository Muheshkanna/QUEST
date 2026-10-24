import type { StudentProfile, Realm, DailyTrial, TopicMastery, Achievement, ActivityLog } from '~/types/quest'

export const defaultStudent: StudentProfile = {
  name: 'Kaelen Vance',
  title: 'Arcanist of Axioms',
  avatar: '🛡️',
  level: 7,
  currentXp: 3450,
  xpToNextLevel: 5000,
  totalXp: 18450,
  streakDays: 14,
  streakShields: 2,
  equippedTitle: 'Seeker of Primes'
}

export const defaultRealms: Realm[] = [
  {
    id: 'enchanted-forest',
    title: 'The Enchanted Forest',
    subtitle: 'Verdant Archives of the First Sprouts',
    loreTag: 'Living Arithmetic & Natural Growth',
    description: 'Master the delicate balances of fractions, decimals, and proportions woven into the roots of ancient trees.',
    curriculum: 'Fractions, Decimals, Ratios & Percentages',
    progressPercent: 68,
    totalQuests: 24,
    completedQuests: 16,
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
    progressPercent: 45,
    totalQuests: 30,
    completedQuests: 14,
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
    progressPercent: 20,
    totalQuests: 28,
    completedQuests: 6,
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
  correctIndex: 2, // The answer is 63. Rule: multiply by 2, then add 1.
  explanation: 'The sequence follows the rule: multiply by 2, then add 1. Specifically: 3×2+1=7, 7×2+1=15, 15×2+1=31, and 31×2+1=63.',
  completed: false
}

export const defaultTopicMasteries: TopicMastery[] = [
  { id: 'tm-1', name: 'Fractional Alchemy', realmId: 'enchanted-forest', masteryLevel: 88, tier: 'Master', sparkCount: 22 },
  { id: 'tm-2', name: 'Decimal Leylines', realmId: 'enchanted-forest', masteryLevel: 74, tier: 'Adept', sparkCount: 15 },
  { id: 'tm-3', name: 'Axiomatic Geometry', realmId: 'temple-of-wisdom', masteryLevel: 62, tier: 'Adept', sparkCount: 12 },
  { id: 'tm-4', name: 'Fibonacci Spire Puzzles', realmId: 'temple-of-wisdom', masteryLevel: 91, tier: 'Master', sparkCount: 28 },
  { id: 'tm-5', name: 'Orbital Kinematics', realmId: 'celestial-frontier', masteryLevel: 35, tier: 'Novice', sparkCount: 7 },
  { id: 'tm-6', name: 'Spectral Polynomials', realmId: 'celestial-frontier', masteryLevel: 18, tier: 'Novice', sparkCount: 4 }
]

export const defaultAchievements: Achievement[] = [
  {
    id: 'ach-1',
    title: 'Axiom Pathfinder',
    description: 'Solve 10 geometric riddle seals without error.',
    icon: '📜',
    unlockedAt: '2 days ago',
    rarity: 'Rare'
  },
  {
    id: 'ach-2',
    title: '14-Sun Astral Orbit',
    description: 'Maintain an unbroken daily learning streak for two weeks.',
    icon: '🔥',
    unlockedAt: 'Today',
    rarity: 'Epic'
  },
  {
    id: 'ach-3',
    title: 'First Forest Sprout',
    description: 'Complete your introductory fraction crucible in the Enchanted Forest.',
    icon: '🌱',
    unlockedAt: '1 week ago',
    rarity: 'Common'
  },
  {
    id: 'ach-4',
    title: 'Starlight Architect',
    description: 'Synthesize 5 celestial equations under astral time pressure.',
    icon: '👑',
    rarity: 'Legendary',
    progress: { current: 3, max: 5 }
  }
]

export const defaultActivityLogs: ActivityLog[] = [
  {
    id: 'log-1',
    text: 'Completed Trial: "The Pythagorean Sigil" in Temple of Wisdom',
    xpGained: 250,
    timestamp: '2 hours ago',
    type: 'trial'
  },
  {
    id: 'log-2',
    text: 'Attained Level 7: Arcanist of Axioms',
    xpGained: 1000,
    timestamp: 'Yesterday',
    type: 'quest'
  },
  {
    id: 'log-3',
    text: 'Mastery tier reached: Fractional Alchemy (Master)',
    xpGained: 400,
    timestamp: '2 days ago',
    type: 'achievement'
  }
]
