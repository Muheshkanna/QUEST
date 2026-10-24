"""Adaptive engine logic for Math Quest.

Pure functions governing:
- 2-up, 1-down difficulty ladder
- Question selection with level fallback
- XP calculation with combo multipliers and retry penalties
"""

from typing import List, Optional, Tuple, Union
from api._lib.schemas import BankFile, Difficulty, Question


DIFFICULTY_LADDER = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

XP_BASE = {
    Difficulty.EASY: 10,
    Difficulty.MEDIUM: 20,
    Difficulty.HARD: 35,
}

MAX_COMBO_MULTIPLIER = 2.0


def update_difficulty(
    current: Difficulty,
    consecutive_correct: int,
    is_correct: bool,
) -> Tuple[Difficulty, int]:
    """Updates the difficulty level according to the 2-up, 1-down rule.

    - 2 correct in a row -> promote up 1 level (capped at HARD), reset streak to 0
    - 1 wrong -> demote down 1 level (clamped at EASY), reset streak to 0
    - 1 correct (when previous streak < 1) -> increment streak, stay at current level
    """
    idx = DIFFICULTY_LADDER.index(current)

    if is_correct:
        new_streak = consecutive_correct + 1
        if new_streak >= 2:
            new_idx = min(idx + 1, len(DIFFICULTY_LADDER) - 1)
            return DIFFICULTY_LADDER[new_idx], 0
        return current, new_streak
    else:
        new_idx = max(idx - 1, 0)
        return DIFFICULTY_LADDER[new_idx], 0


def compute_xp(
    difficulty: Union[Difficulty, str],
    combo: int = 1,
    attempt_number: int = 1,
) -> int:
    """Computes XP earned for answering a question.

    - Weights: Easy = 10, Medium = 20, Hard = 35
    - Combo multiplier: 1 + (combo - 1) * 0.1, capped at 2.0x (combo >= 1)
    - Retry penalty: attempt_number > 1 awards 50% (floor) of calculated XP
    """
    diff_enum = Difficulty(difficulty) if isinstance(difficulty, str) else difficulty
    base = XP_BASE.get(diff_enum, 10)

    # Combo scaling: combo 1 = 1.0x, combo 2 = 1.1x, combo 11+ = 2.0x
    multiplier = min(1.0 + max(0, combo - 1) * 0.1, MAX_COMBO_MULTIPLIER)
    total = int(round(base * multiplier))

    if attempt_number > 1:
        total = int(total * 0.5)

    return total


def choose_next_question(
    bank: BankFile,
    current_difficulty: Difficulty,
    seen_ids: List[str],
) -> Optional[Question]:
    """Selects the next question from bank matching current difficulty.

    If current difficulty questions are all seen/exhausted, falls back to
    adjacent difficulty levels in order of proximity (e.g. Medium -> Easy -> Hard,
    or Easy -> Medium -> Hard, or Hard -> Medium -> Easy).
    """
    seen_set = set(seen_ids)

    # Search order based on current difficulty
    if current_difficulty == Difficulty.EASY:
        fallback_order = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
    elif current_difficulty == Difficulty.HARD:
        fallback_order = [Difficulty.HARD, Difficulty.MEDIUM, Difficulty.EASY]
    else:
        fallback_order = [Difficulty.MEDIUM, Difficulty.EASY, Difficulty.HARD]

    for diff in fallback_order:
        candidates = [
            q for q in bank.questions
            if q.difficulty == diff and q.id not in seen_set
        ]
        if candidates:
            return candidates[0]

    return None
