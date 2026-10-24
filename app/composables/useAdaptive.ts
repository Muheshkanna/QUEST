export type Difficulty = 'easy' | 'medium' | 'hard'

export interface BKTParams {
  guess: number
  slip: number
}

export const DIFFICULTY_LADDER: Difficulty[] = ['easy', 'medium', 'hard']

export const XP_BASE: Record<Difficulty, number> = {
  easy: 10,
  medium: 20,
  hard: 35
}

export const MAX_COMBO_MULTIPLIER = 2.0
export const DEFAULT_P_INIT = 0.20
export const DEFAULT_P_LEARN = 0.15

export const BKT_DIFFICULTY_PARAMS: Record<Difficulty, BKTParams> = {
  easy: { guess: 0.30, slip: 0.08 },
  medium: { guess: 0.25, slip: 0.10 },
  hard: { guess: 0.15, slip: 0.15 }
}

export const MASTERY_THRESHOLDS: [number, string][] = [
  [0.85, 'Mastered'],
  [0.70, 'Proficient'],
  [0.40, 'Learning'],
  [0.00, 'Novice']
]

/**
 * Updates difficulty according to 2-up, 1-down rule.
 * 2 correct in a row -> promote up (capped at hard)
 * 1 wrong -> demote down (clamped at easy)
 */
export function updateDifficulty(
  current: Difficulty,
  consecutiveCorrect: number,
  isCorrect: boolean
): { difficulty: Difficulty; consecutiveCorrect: number } {
  const idx = DIFFICULTY_LADDER.indexOf(current)

  if (isCorrect) {
    const newStreak = consecutiveCorrect + 1
    if (newStreak >= 2) {
      const nextIdx = Math.min(idx + 1, DIFFICULTY_LADDER.length - 1)
      return { difficulty: DIFFICULTY_LADDER[nextIdx], consecutiveCorrect: 0 }
    }
    return { difficulty: current, consecutiveCorrect: newStreak }
  } else {
    const nextIdx = Math.max(idx - 1, 0)
    return { difficulty: DIFFICULTY_LADDER[nextIdx], consecutiveCorrect: 0 }
  }
}

/**
 * Computes XP earned for answering a question.
 * Easy=10, Medium=20, Hard=35
 * Combo multiplier = min(1 + (combo - 1) * 0.1, 2.0)
 * Attempt > 1 -> 50% XP
 */
export function computeXp(
  difficulty: Difficulty,
  combo = 1,
  attemptNumber = 1
): number {
  const base = XP_BASE[difficulty] ?? 10
  const multiplier = Math.min(1.0 + Math.max(0, combo - 1) * 0.1, MAX_COMBO_MULTIPLIER)
  let total = Math.round(base * multiplier)

  if (attemptNumber > 1) {
    total = Math.floor(total * 0.5)
  }

  return total
}

/**
 * Updates BKT mastery probability given student observation.
 * Returns probability rounded to 4 decimal places.
 */
export function updateBkt(
  pKnown: number,
  correct: boolean,
  difficulty: Difficulty = 'medium',
  pLearn = DEFAULT_P_LEARN
): number {
  const params = BKT_DIFFICULTY_PARAMS[difficulty] || BKT_DIFFICULTY_PARAMS.medium
  const pG = params.guess
  const pS = params.slip

  // Clamp prior to avoid 0/1 singularity
  const pL = Math.max(0.001, Math.min(0.999, pKnown))

  let pPosterior: number
  if (correct) {
    const numerator = pL * (1.0 - pS)
    const denominator = numerator + (1.0 - pL) * pG
    pPosterior = denominator > 0 ? numerator / denominator : pL
  } else {
    const numerator = pL * pS
    const denominator = numerator + (1.0 - pL) * (1.0 - pG)
    pPosterior = denominator > 0 ? numerator / denominator : pL
  }

  const pNext = pPosterior + (1.0 - pPosterior) * pLearn
  const clamped = Math.max(0.001, Math.min(0.999, pNext))
  return Number(clamped.toFixed(4))
}

/**
 * Returns categorical mastery label from probability.
 */
export function masteryLabel(p: number): string {
  const pClamped = Math.max(0, Math.min(1, p))
  for (const [threshold, label] of MASTERY_THRESHOLDS) {
    if (pClamped >= threshold) {
      return label
    }
  }
  return 'Novice'
}

/**
 * Recommend next topic from topic state record { [topicId]: probability }.
 */
export function recommendNextTopic(
  topicStates: Record<string, number>,
  priorityOrder: string[] = []
): string | null {
  const entries = Object.entries(topicStates)
  if (entries.length === 0) return null

  const orderMap = new Map(priorityOrder.map((id, index) => [id, index]))

  entries.sort(([aId, aScore], [bId, bScore]) => {
    const aMastered = aScore >= 0.85 ? 1 : 0
    const bMastered = bScore >= 0.85 ? 1 : 0
    if (aMastered !== bMastered) return aMastered - bMastered

    const diff = aScore - bScore
    if (Math.abs(diff) > 0.0001) return diff

    const aOrder = orderMap.get(aId) ?? 9999
    const bOrder = orderMap.get(bId) ?? 9999
    return aOrder - bOrder
  })

  return entries[0][0]
}

export function useAdaptive() {
  return {
    updateDifficulty,
    computeXp,
    updateBkt,
    masteryLabel,
    recommendNextTopic,
    DIFFICULTY_LADDER,
    DEFAULT_P_INIT,
    DEFAULT_P_LEARN
  }
}
