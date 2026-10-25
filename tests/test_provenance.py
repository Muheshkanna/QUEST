"""Unit tests for STEP 3: Distractor provenance in verify_question."""
import pytest
from api._lib.schemas import Question, Option, Difficulty
from api._lib.verifier import verify_question


def make_sample_question(
    topic_id="g5-fractions-add",
    params=None,
    expression="1/4 + 1/8",
    options=None,
    correct_index=0,
):
    if params is None:
        params = {"a": 1, "b": 4, "c": 1, "d": 8}
    if options is None:
        options = [
            Option(id="A", text="3/8"),  # correct
            Option(id="B", text="1/6", misconception="added_tops_and_bottoms", misconception_id="added_tops_and_bottoms"),
            Option(id="C", text="1/4", misconception="renamed_bottom_kept_tops", misconception_id="renamed_bottom_kept_tops"),
            Option(id="D", text="1/32", misconception="multiplied_instead_of_adding", misconception_id="multiplied_instead_of_adding"),
        ]
    return Question(
        id=f"{topic_id}-test-1",
        topic_id=topic_id,
        difficulty=Difficulty.EASY,
        verifier_type="fraction_arithmetic",
        template_id=f"{topic_id}-easy-tpl",
        stem="What is 1/4 + 1/8?",
        expression=expression,
        params=params,
        options=options,
        correct_index=correct_index,
        explanation="1/4 + 1/8 = 2/8 + 1/8 = 3/8.",
        hint="Find a common denominator.",
    )


def test_provenance_correct_case_passes():
    """A valid generated question with params and valid rule options passes with verified provenance."""
    q = make_sample_question()
    res = verify_question(q)
    assert res.passed is True, f"Expected pass, got reasons: {res.reasons}"
    assert q.provenance == "verified"


def test_provenance_mismatched_tag_fails():
    """Mismatched tag: distractor text does not match the rule output."""
    opts = [
        Option(id="A", text="3/8"),
        Option(id="B", text="7/99", misconception="added_tops_and_bottoms", misconception_id="added_tops_and_bottoms"),  # wrong text!
        Option(id="C", text="1/4", misconception="renamed_bottom_kept_tops", misconception_id="renamed_bottom_kept_tops"),
        Option(id="D", text="1/32", misconception="multiplied_instead_of_adding", misconception_id="multiplied_instead_of_adding"),
    ]
    q = make_sample_question(options=opts)
    res = verify_question(q)
    assert res.passed is False
    assert any("expected" in r for r in res.reasons)
    assert q.provenance == "unchecked"


def test_provenance_filler_option_fails():
    """Filler option: wrong option with empty or missing misconception tag fails."""
    opts = [
        Option(id="A", text="3/8"),
        Option(id="B", text="1/6", misconception=None, misconception_id=None),  # filler!
        Option(id="C", text="1/4", misconception="renamed_bottom_kept_tops", misconception_id="renamed_bottom_kept_tops"),
        Option(id="D", text="1/32", misconception="multiplied_instead_of_adding", misconception_id="multiplied_instead_of_adding"),
    ]
    q = make_sample_question(options=opts)
    res = verify_question(q)
    assert res.passed is False
    assert any("missing a misconception tag" in r for r in res.reasons)


def test_provenance_non_applicable_tag_fails():
    """Non-applicable tag: rule's applies_when is false for params (e.g. b == d for renamed_bottom_kept_tops)."""
    # When b == 4 and d == 4, renamed_bottom_kept_tops does not apply
    params = {"a": 1, "b": 4, "c": 1, "d": 4}
    opts = [
        Option(id="A", text="1/2"),
        Option(id="B", text="1/4", misconception="added_tops_and_bottoms", misconception_id="added_tops_and_bottoms"),
        Option(id="C", text="1/2", misconception="renamed_bottom_kept_tops", misconception_id="renamed_bottom_kept_tops"),  # applies_when is False!
        Option(id="D", text="1/16", misconception="multiplied_instead_of_adding", misconception_id="multiplied_instead_of_adding"),
    ]
    q = make_sample_question(params=params, expression="1/4 + 1/4", options=opts)
    res = verify_question(q)
    assert res.passed is False
    assert any("applies_when is false" in r for r in res.reasons)


def test_provenance_unknown_id_fails():
    """Unknown id: misconception tag does not exist in registry."""
    opts = [
        Option(id="A", text="3/8"),
        Option(id="B", text="1/6", misconception="totally_unknown_rule_xyz", misconception_id="totally_unknown_rule_xyz"),
        Option(id="C", text="1/4", misconception="renamed_bottom_kept_tops", misconception_id="renamed_bottom_kept_tops"),
        Option(id="D", text="1/32", misconception="multiplied_instead_of_adding", misconception_id="multiplied_instead_of_adding"),
    ]
    q = make_sample_question(options=opts)
    res = verify_question(q)
    assert res.passed is False
    assert any("unknown misconception id" in r for r in res.reasons)
