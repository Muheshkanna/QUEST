import { describe, it, expect } from 'vitest'
import fixtures from './fixtures/adaptive_cases.json'
import {
  updateDifficulty,
  computeXp,
  updateBkt,
  masteryLabel,
  recommendNextTopic,
  type Difficulty
} from '../app/composables/useAdaptive'

describe('useAdaptive - Parity with Python Implementation', () => {
  describe('Adaptive Difficulty Ladder', () => {
    fixtures.adaptive_ladder.forEach((caseItem, idx) => {
      it(`case #${idx}: from ${caseItem.start} (streak ${caseItem.streak}, correct=${caseItem.correct}) -> ${caseItem.expected_diff}`, () => {
        const res = updateDifficulty(
          caseItem.start as Difficulty,
          caseItem.streak,
          caseItem.correct
        )
        expect(res.difficulty).toBe(caseItem.expected_diff)
        expect(res.consecutiveCorrect).toBe(caseItem.expected_streak)
      })
    })
  })

  describe('XP Calculations', () => {
    fixtures.xp_calculations.forEach((caseItem, idx) => {
      it(`case #${idx}: ${caseItem.difficulty} (combo ${caseItem.combo}, attempt ${caseItem.attempt}) -> ${caseItem.expected_xp} XP`, () => {
        const xp = computeXp(
          caseItem.difficulty as Difficulty,
          caseItem.combo,
          caseItem.attempt
        )
        expect(xp).toBe(caseItem.expected_xp)
      })
    })
  })

  describe('BKT Posterior Updates', () => {
    fixtures.bkt_updates.forEach((caseItem, idx) => {
      it(`case #${idx}: p=${caseItem.p_known}, correct=${caseItem.correct}, diff=${caseItem.difficulty} -> ${caseItem.expected_p}`, () => {
        const pNext = updateBkt(
          caseItem.p_known,
          caseItem.correct,
          caseItem.difficulty as Difficulty
        )
        expect(pNext).toBeCloseTo(caseItem.expected_p, 4)
      })
    })
  })

  describe('Mastery Labels', () => {
    fixtures.mastery_labels.forEach((caseItem, idx) => {
      it(`case #${idx}: p=${caseItem.p} -> ${caseItem.expected_label}`, () => {
        expect(masteryLabel(caseItem.p)).toBe(caseItem.expected_label)
      })
    })
  })

  describe('Topic Recommendations', () => {
    it('recommends unmastered topic with lowest score first', () => {
      const topicStates = {
        'topic-a': 0.88,
        'topic-b': 0.35,
        'topic-c': 0.60
      }
      expect(recommendNextTopic(topicStates)).toBe('topic-b')
    })

    it('breaks ties using curriculum sequence order', () => {
      const topicStates = {
        'topic-c': 0.50,
        'topic-a': 0.50,
        'topic-b': 0.50
      }
      const priority = ['topic-a', 'topic-b', 'topic-c']
      expect(recommendNextTopic(topicStates, priority)).toBe('topic-a')
    })

    it('returns lowest mastered topic when all are mastered', () => {
      const topicStates = {
        'topic-a': 0.95,
        'topic-b': 0.86,
        'topic-c': 0.90
      }
      expect(recommendNextTopic(topicStates)).toBe('topic-b')
    })

    it('returns null for empty states', () => {
      expect(recommendNextTopic({})).toBeNull()
    })
  })
})
