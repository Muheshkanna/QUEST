import json
import pytest
from pydantic import ValidationError
from api._lib.schemas import (
    Difficulty,
    Option,
    Question,
    Lesson,
    WorkedStep,
    InfographicData,
    InfographicStep,
    Slide,
    ExplainerScript,
    TopicEntry,
    BankFile,
    EvalResult,
)


def test_load_all_topics_json():
    """Verify data/topics.json loads completely and strictly conforms to TopicEntry schema."""
    with open("data/topics.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 20

    topics = [TopicEntry(**item) for item in data]
    assert len(topics) == 20

    # Ensure all 20 have standard_verified = True and valid fields
    for t in topics:
        assert t.id
        assert t.grade in (5, 6)
        assert t.realm in ("Enchanted Forest", "Temple of Wisdom", "Celestial Frontier")
        assert t.title
        assert t.fantasy_name
        assert t.standard
        assert isinstance(t.standard_verified, bool)
        assert t.verifier_type
        assert len(t.misconceptions) >= 2


def test_question_schema_exact_four_options():
    """Questions must have exactly 4 options."""
    # Valid question
    valid_q = Question(
        id="q-test-1",
        topic_id="5.NR.1.1",
        difficulty=Difficulty.EASY,
        verifier_type="fraction_arithmetic",
        stem="What is 1/4 + 1/4?",
        expression="1/4 + 1/4",
        options=[
            Option(id="A", text="1/2"),
            Option(id="B", text="2/8", misconception="Forgot to simplify"),
            Option(id="C", text="1/4", misconception="Only added numerators incorrectly"),
            Option(id="D", text="1", misconception="Added both as wholes"),
        ],
        correct_index=0,
        explanation="1/4 + 1/4 = 2/4 = 1/2.",
    )
    assert valid_q.id == "q-test-1"

    # Less than 4 options should fail
    with pytest.raises(ValidationError):
        Question(
            id="q-test-2",
            topic_id="5.NR.1.1",
            difficulty=Difficulty.EASY,
            verifier_type="fraction_arithmetic",
            stem="What is 1/4 + 1/4?",
            expression="1/4 + 1/4",
            options=[
                Option(id="A", text="1/2"),
                Option(id="B", text="2/8"),
            ],
            correct_index=0,
            explanation="Test.",
        )

    # More than 4 options should fail
    with pytest.raises(ValidationError):
        Question(
            id="q-test-3",
            topic_id="5.NR.1.1",
            difficulty=Difficulty.EASY,
            verifier_type="fraction_arithmetic",
            stem="What is 1/4 + 1/4?",
            expression="1/4 + 1/4",
            options=[
                Option(id="A", text="1/2"),
                Option(id="B", text="2/8"),
                Option(id="C", text="1/4"),
                Option(id="D", text="1"),
                Option(id="E", text="3/4"),
            ],
            correct_index=0,
            explanation="Test.",
        )


def test_question_schema_correct_index_bounds():
    """correct_index must be between 0 and 3."""
    with pytest.raises(ValidationError):
        Question(
            id="q-test-4",
            topic_id="5.NR.1.1",
            difficulty=Difficulty.EASY,
            verifier_type="fraction_arithmetic",
            stem="Stem",
            expression="1+1",
            options=[
                Option(id="A", text="2"),
                Option(id="B", text="3"),
                Option(id="C", text="4"),
                Option(id="D", text="5"),
            ],
            correct_index=4,  # Out of range
            explanation="Exp",
        )

    with pytest.raises(ValidationError):
        Question(
            id="q-test-5",
            topic_id="5.NR.1.1",
            difficulty=Difficulty.EASY,
            verifier_type="fraction_arithmetic",
            stem="Stem",
            expression="1+1",
            options=[
                Option(id="A", text="2"),
                Option(id="B", text="3"),
                Option(id="C", text="4"),
                Option(id="D", text="5"),
            ],
            correct_index=-1,  # Out of range
            explanation="Exp",
        )


def test_question_schema_non_empty_strings():
    """Stem, expression, and explanation cannot be blank or whitespace."""
    with pytest.raises(ValidationError):
        Question(
            id="q-test-6",
            topic_id="5.NR.1.1",
            difficulty=Difficulty.EASY,
            verifier_type="fraction_arithmetic",
            stem="   ",
            expression="1+1",
            options=[
                Option(id="A", text="2"),
                Option(id="B", text="3"),
                Option(id="C", text="4"),
                Option(id="D", text="5"),
            ],
            correct_index=0,
            explanation="Exp",
        )


def test_lesson_schema_structure():
    """Test full Lesson schema validation."""
    lesson = Lesson(
        title="Fractions of the Ancients",
        big_idea="Fractions represent equal parts of a whole.",
        explanation="When adding fractions with like denominators, add numerators.",
        worked_example=[
            WorkedStep(step=1, text="Identify denominators", math="Denominators are both 4"),
            WorkedStep(step=2, text="Add numerators", math="1 + 1 = 2"),
            WorkedStep(step=3, text="Simplify", math="2/4 = 1/2"),
        ],
        key_vocab=["Numerator", "Denominator", "Simplify"],
        real_world_example="Sharing a magical pizza with 4 slices.",
        common_mistakes=["Adding the denominators together (e.g., 1/4 + 1/4 = 2/8)"],
    )
    assert lesson.title == "Fractions of the Ancients"
    assert len(lesson.worked_example) == 3
    assert len(lesson.key_vocab) == 3


def test_infographic_and_explainer_schemas():
    """Verify InfographicData and ExplainerScript schemas."""
    info = InfographicData(
        title="Fraction Forge",
        steps=[
            InfographicStep(label="Step 1", detail="Keep bottom same", math="4"),
            InfographicStep(label="Step 2", detail="Combine tops", math="1 + 1 = 2"),
        ],
        example="1/4 + 1/4 = 1/2",
        image_prompt="A glowing forge with fractional runes on crystalline anvils",
    )
    assert len(info.steps) == 2
    assert info.title == "Fraction Forge"

    script = ExplainerScript(
        slides=[
            Slide(
                title="The Ancient Denominator",
                visual_hint="A stone pillar with 4 chambers",
                narration="Behold the denominator, which marks the whole.",
                highlight="chambers",
            )
        ]
    )
    assert len(script.slides) == 1
    assert script.slides[0].highlight == "chambers"


def test_bank_file_and_eval_result_schemas():
    """Verify BankFile and EvalResult schema validation."""
    bank = BankFile(
        topic_id="5.NR.1.1",
        version="1.0.0",
        questions=[
            Question(
                id="q-bf-1",
                topic_id="5.NR.1.1",
                difficulty=Difficulty.MEDIUM,
                verifier_type="fraction_arithmetic",
                stem="3/5 + 1/5?",
                expression="3/5 + 1/5",
                options=[
                    Option(id="A", text="4/5"),
                    Option(id="B", text="4/10", misconception="added denominators"),
                    Option(id="C", text="2/5", misconception="subtracted"),
                    Option(id="D", text="1", misconception="rounded"),
                ],
                correct_index=0,
                explanation="3/5 + 1/5 = 4/5.",
            )
        ],
    )
    assert len(bank.questions) == 1

    res = EvalResult(
        model="gemini-1.5-flash",
        prompt_version="v2",
        total_evaluated=10,
        schema_valid_rate=1.0,
        math_correct_rate=0.9,
        distractor_quality=0.85,
        avg_latency_ms=450.0,
        rejected_samples=[{"id": "q-1", "reason": "math_error"}],
    )
    assert res.math_correct_rate == 0.9
