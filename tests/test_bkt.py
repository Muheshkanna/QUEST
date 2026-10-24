import json
import pytest
from api._lib.schemas import Difficulty
from api._lib.bkt import update, mastery_label, recommend_next


with open("tests/fixtures/adaptive_cases.json", "r", encoding="utf-8") as f:
    _FIXTURE_DATA = json.load(f)


@pytest.mark.parametrize("c", _FIXTURE_DATA["bkt_updates"])
def test_bkt_update_case(c):
    p_next = update(c["p_known"], c["correct"], Difficulty(c["difficulty"]))
    assert round(p_next, 4) == c["expected_p"]


def test_bkt_monotonicity():
    """Correct answer should strictly increase mastery; wrong should strictly decrease."""
    p_init = 0.50
    for diff in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        p_after_correct = update(p_init, True, diff)
        p_after_wrong = update(p_init, False, diff)
        assert p_after_correct > p_init, f"Correct must increase p for {diff}"
        assert p_after_wrong < p_init, f"Wrong must decrease p for {diff}"


@pytest.mark.parametrize("c", _FIXTURE_DATA["mastery_labels"])
def test_mastery_label_case(c):
    assert mastery_label(c["p"]) == c["expected_label"]


def test_recommend_next():
    # Empty states
    assert recommend_next({}) is None

    # Picks unmastered topic with lowest mastery
    states = {
        "topic-1": 0.86,  # Mastered
        "topic-2": 0.35,  # Novice
        "topic-3": 0.65,  # Learning
    }
    assert recommend_next(states) == "topic-2"

    # Curriculum priority tiebreaker
    states_tied = {
        "topic-c": 0.50,
        "topic-a": 0.50,
        "topic-b": 0.50,
    }
    priority = ["topic-a", "topic-b", "topic-c"]
    assert recommend_next(states_tied, priority) == "topic-a"

    # All mastered: review lowest mastered
    states_all_mastered = {
        "topic-a": 0.95,
        "topic-b": 0.86,
        "topic-c": 0.92,
    }
    assert recommend_next(states_all_mastered) == "topic-b"
