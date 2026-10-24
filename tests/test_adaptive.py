import json
import pytest
from api._lib.schemas import BankFile, Difficulty, Option, Question
from api._lib.adaptive import update_difficulty, compute_xp, choose_next_question


with open("tests/fixtures/adaptive_cases.json", "r", encoding="utf-8") as f:
    _FIXTURE_DATA = json.load(f)


@pytest.mark.parametrize("c", _FIXTURE_DATA["adaptive_ladder"])
def test_adaptive_ladder_case(c):
    start_diff = Difficulty(c["start"])
    res_diff, res_streak = update_difficulty(start_diff, c["streak"], c["correct"])
    assert res_diff.value == c["expected_diff"]
    assert res_streak == c["expected_streak"]


def test_adaptive_ladder_clamping():
    # Consecutive wrongs at easy remain at easy
    diff, streak = update_difficulty(Difficulty.EASY, 0, False)
    assert diff == Difficulty.EASY
    assert streak == 0

    # Multiple correct at hard remain at hard
    diff, streak = update_difficulty(Difficulty.HARD, 1, True)
    assert diff == Difficulty.HARD
    assert streak == 0


@pytest.mark.parametrize("c", _FIXTURE_DATA["xp_calculations"])
def test_xp_calculation_case(c):
    xp = compute_xp(c["difficulty"], c["combo"], c["attempt"])
    assert xp == c["expected_xp"]


def test_xp_edge_cases():
    # Combo multiplier capped at 2.0x (base 35 * 2.0 = 70)
    assert compute_xp(Difficulty.HARD, combo=50, attempt_number=1) == 70
    # Retry on hard with high combo: 70 // 2 = 35
    assert compute_xp(Difficulty.HARD, combo=50, attempt_number=2) == 35
    # Negative/zero combo handles cleanly (defaults to 1.0x)
    assert compute_xp(Difficulty.MEDIUM, combo=0, attempt_number=1) == 20


def test_choose_next_question_same_difficulty():
    q1 = Question(
        id="q1", topic_id="t1", difficulty=Difficulty.MEDIUM, verifier_type="v",
        stem="s", expression="1+1",
        options=[Option(id="A", text="2"), Option(id="B", text="3", misconception="m"),
                 Option(id="C", text="4", misconception="m"), Option(id="D", text="5", misconception="m")],
        correct_index=0, explanation="e"
    )
    q2 = Question(
        id="q2", topic_id="t1", difficulty=Difficulty.MEDIUM, verifier_type="v",
        stem="s2", expression="2+2",
        options=[Option(id="A", text="4"), Option(id="B", text="3", misconception="m"),
                 Option(id="C", text="5", misconception="m"), Option(id="D", text="6", misconception="m")],
        correct_index=0, explanation="e"
    )
    bank = BankFile(topic_id="t1", questions=[q1, q2])

    next_q = choose_next_question(bank, Difficulty.MEDIUM, seen_ids=[])
    assert next_q is not None
    assert next_q.id == "q1"

    next_q2 = choose_next_question(bank, Difficulty.MEDIUM, seen_ids=["q1"])
    assert next_q2 is not None
    assert next_q2.id == "q2"


def test_choose_next_question_fallback():
    # Only easy and hard available
    q_easy = Question(
        id="qe", topic_id="t1", difficulty=Difficulty.EASY, verifier_type="v",
        stem="se", expression="1+1",
        options=[Option(id="A", text="2"), Option(id="B", text="3", misconception="m"),
                 Option(id="C", text="4", misconception="m"), Option(id="D", text="5", misconception="m")],
        correct_index=0, explanation="e"
    )
    q_hard = Question(
        id="qh", topic_id="t1", difficulty=Difficulty.HARD, verifier_type="v",
        stem="sh", expression="3+3",
        options=[Option(id="A", text="6"), Option(id="B", text="3", misconception="m"),
                 Option(id="C", text="4", misconception="m"), Option(id="D", text="5", misconception="m")],
        correct_index=0, explanation="e"
    )
    bank = BankFile(topic_id="t1", questions=[q_easy, q_hard])

    # Medium requested, but none exist; medium falls back to easy first
    picked = choose_next_question(bank, Difficulty.MEDIUM, seen_ids=[])
    assert picked is not None
    assert picked.id == "qe"

    # If easy seen, medium falls back to hard
    picked2 = choose_next_question(bank, Difficulty.MEDIUM, seen_ids=["qe"])
    assert picked2 is not None
    assert picked2.id == "qh"

    # If all seen, returns None
    picked3 = choose_next_question(bank, Difficulty.MEDIUM, seen_ids=["qe", "qh"])
    assert picked3 is None
