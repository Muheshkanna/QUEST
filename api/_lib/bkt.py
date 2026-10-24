"""Bayesian Knowledge Tracing (BKT) engine for Math Quest.

Models student mastery of individual topics with standard BKT equations:
- P(L0): Initial knowledge probability (prior)
- P(T): Transition probability (probability of learning at each opportunity)
- P(G): Guess probability (getting it right without knowing)
- P(S): Slip probability (getting it wrong despite knowing)

Difficulty-tuned slip and guess parameters:
- Easy: P(G) = 0.30, P(S) = 0.08 (easier to guess, rarer to slip)
- Medium: P(G) = 0.25, P(S) = 0.10 (standard baseline)
- Hard: P(G) = 0.15, P(S) = 0.15 (harder to guess, easier to slip)
"""

from typing import Dict, List, Optional, Tuple, Union
from api._lib.schemas import Difficulty


# Documented default BKT parameters
DEFAULT_P_INIT = 0.20
DEFAULT_P_LEARN = 0.15

BKT_DIFFICULTY_PARAMS: Dict[Difficulty, Dict[str, float]] = {
    Difficulty.EASY: {"guess": 0.30, "slip": 0.08},
    Difficulty.MEDIUM: {"guess": 0.25, "slip": 0.10},
    Difficulty.HARD: {"guess": 0.15, "slip": 0.15},
}

# Mastery thresholds
MASTERY_THRESHOLDS = [
    (0.85, "Mastered"),
    (0.70, "Proficient"),
    (0.40, "Learning"),
    (0.00, "Novice"),
]


def update(
    p_known: float,
    correct: bool,
    difficulty: Union[Difficulty, str] = Difficulty.MEDIUM,
    p_learn: float = DEFAULT_P_LEARN,
) -> float:
    """Updates the mastery probability P(L_t) -> P(L_{t+1}) given student observation.

    Parameters:
        p_known: Current probability of mastery P(L_t), bounded in [0.001, 0.999]
        correct: Whether the student answered correctly
        difficulty: Difficulty of the question ('easy', 'medium', 'hard')
        p_learn: Probability of learning between attempts

    Returns:
        Updated probability P(L_{t+1}) rounded to 4 decimal places.
    """
    diff_enum = Difficulty(difficulty) if isinstance(difficulty, str) else difficulty
    params = BKT_DIFFICULTY_PARAMS.get(diff_enum, BKT_DIFFICULTY_PARAMS[Difficulty.MEDIUM])

    p_g = params["guess"]
    p_s = params["slip"]

    # Clamp prior to avoid numerical instability
    p_l = max(0.001, min(0.999, float(p_known)))

    if correct:
        # P(L|obs=correct) = P(L) * (1 - P(S)) / [ P(L) * (1 - P(S)) + (1 - P(L)) * P(G) ]
        numerator = p_l * (1.0 - p_s)
        denominator = numerator + (1.0 - p_l) * p_g
    else:
        # P(L|obs=wrong) = P(L) * P(S) / [ P(L) * P(S) + (1 - P(L)) * (1 - P(G)) ]
        numerator = p_l * p_s
        denominator = numerator + (1.0 - p_l) * (1.0 - p_g)

    p_posterior = numerator / denominator if denominator > 0 else p_l

    # P(L_{t+1}) = P(L|obs) + (1 - P(L|obs)) * P(T)
    p_next = p_posterior + (1.0 - p_posterior) * p_learn

    return round(max(0.001, min(0.999, p_next)), 4)


def mastery_label(p: float) -> str:
    """Returns a categorical mastery level based on mastery probability.

    - >= 0.85 -> Mastered
    - >= 0.70 -> Proficient
    - >= 0.40 -> Learning
    - < 0.40  -> Novice
    """
    p_clamped = max(0.0, min(1.0, float(p)))
    for threshold, label in MASTERY_THRESHOLDS:
        if p_clamped >= threshold:
            return label
    return "Novice"


def recommend_next(
    topic_states: Dict[str, float],
    priority_order: Optional[List[str]] = None,
) -> Optional[str]:
    """Recommends the next topic to study based on mastery states.

    Prioritizes:
    1. Topics that are not yet 'Mastered' (p < 0.85), sorted by lowest mastery first
    2. If priority_order is provided, breaks ties using curriculum order
    3. If all topics are mastered, recommends the one with the lowest score for review
    """
    if not topic_states:
        return None

    order_map = {tid: i for i, tid in enumerate(priority_order or [])}

    # Sort key: (is_mastered, mastery_level, priority_index)
    def sort_key(item: Tuple[str, float]):
        tid, p = item
        is_mastered = 1 if p >= 0.85 else 0
        p_rounded = round(p, 3)
        seq_idx = order_map.get(tid, 9999)
        return (is_mastered, p_rounded, seq_idx)

    sorted_topics = sorted(topic_states.items(), key=sort_key)
    return sorted_topics[0][0]
