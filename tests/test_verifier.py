import pytest
from fractions import Fraction
from api._lib.schemas import Difficulty, Lesson, Option, Question, WorkedStep
from api._lib.verifier import (
    evaluate_expression,
    normalize_option,
    verify_lesson,
    verify_question,
    VerificationError,
    solve_linear,
    ratio_simplify,
    unit_rate,
    percent_of,
    volume_box,
    compare,
    math_mean,
    math_median,
    math_mode,
    math_gcd,
    math_lcm,
)


# ==========================================
# 1. OPTION NORMALIZER TESTS
# ==========================================

def test_normalize_plain_numbers():
    assert normalize_option("42") == ("frac:42/1", Fraction(42, 1))
    assert normalize_option("-15") == ("frac:-15/1", Fraction(-15, 1))
    assert normalize_option("1,000") == ("frac:1000/1", Fraction(1000, 1))
    assert normalize_option("2,500,000") == ("frac:2500000/1", Fraction(2500000, 1))


def test_normalize_decimals():
    assert normalize_option("0.75") == ("frac:3/4", Fraction(3, 4))
    assert normalize_option("0.35") == ("frac:7/20", Fraction(7, 20))
    assert normalize_option("-0.5") == ("frac:-1/2", Fraction(-1, 2))


def test_normalize_fractions():
    assert normalize_option("5/12") == ("frac:5/12", Fraction(5, 12))
    assert normalize_option("10/24") == ("frac:5/12", Fraction(5, 12))
    assert normalize_option("-3/4") == ("frac:-3/4", Fraction(-3, 4))


def test_normalize_mixed_numbers():
    assert normalize_option("2 1/4") == ("frac:9/4", Fraction(9, 4))
    assert normalize_option("3 1/2") == ("frac:7/2", Fraction(7, 2))
    assert normalize_option("-1 1/2") == ("frac:-3/2", Fraction(-3, 2))


def test_normalize_percentages():
    assert normalize_option("25%") == ("frac:1/4", Fraction(1, 4))
    assert normalize_option("50%") == ("frac:1/2", Fraction(1, 2))
    assert normalize_option("100%") == ("frac:1/1", Fraction(1, 1))


def test_normalize_ratios():
    assert normalize_option("3:4") == ("ratio:3:4", Fraction(3, 4))
    assert normalize_option("6:8") == ("ratio:3:4", Fraction(3, 4))
    assert normalize_option("10:5") == ("ratio:2:1", Fraction(2, 1))


def test_normalize_currency_and_units():
    assert normalize_option("$1.50") == ("frac:3/2", Fraction(3, 2))
    assert normalize_option("$42") == ("frac:42/1", Fraction(42, 1))
    assert normalize_option("15 cm³") == ("frac:15/1", Fraction(15, 1))
    assert normalize_option("24 m^2") == ("frac:24/1", Fraction(24, 1))
    assert normalize_option("100 kg") == ("frac:100/1", Fraction(100, 1))


def test_normalize_text_fallback():
    assert normalize_option("equal") == ("=", None)
    assert normalize_option("Greater Than") == (">", None)
    assert normalize_option("equivalent") == ("equivalent", None)


# ==========================================
# 2. SAFE EXPRESSION EVALUATOR & AST DEFENSES
# ==========================================

def test_evaluator_basic_math():
    assert evaluate_expression("3 + 4 * 2") == Fraction(11, 1)
    assert evaluate_expression("(3 + 4) * 2") == Fraction(14, 1)
    assert evaluate_expression("1/4 + 1/4") == Fraction(1, 2)
    assert evaluate_expression("0.5 * 4") == Fraction(2, 1)
    assert evaluate_expression("2 ** 4") == Fraction(16, 1)
    assert evaluate_expression("-5 + 12") == Fraction(7, 1)
    assert evaluate_expression("17 % 5") == Fraction(2, 1)
    assert evaluate_expression("17 // 5") == Fraction(3, 1)


def test_evaluator_percent_of():
    assert evaluate_expression("25% of 80") == Fraction(20, 1)
    assert evaluate_expression("10% of 250") == Fraction(25, 1)


def test_evaluator_whitelisted_helpers():
    assert evaluate_expression("mean(2, 4, 6, 8)") == Fraction(5, 1)
    assert evaluate_expression("median(3, 1, 9, 7, 5)") == Fraction(5, 1)
    assert evaluate_expression("mode(1, 2, 2, 3)") == Fraction(2, 1)
    assert evaluate_expression("gcd(24, 36)") == Fraction(12, 1)
    assert evaluate_expression("lcm(4, 6)") == Fraction(12, 1)
    assert evaluate_expression("solve_linear('3x + 5 = 20')") == Fraction(5, 1)
    assert evaluate_expression("volume_box(3, 4, 5)") == Fraction(60, 1)
    assert evaluate_expression("unit_rate(120, 3)") == Fraction(40, 1)
    assert evaluate_expression("ratio_simplify(6, 8)") == "3:4"
    assert evaluate_expression("round_to(3.14159, 2)") == Fraction(314, 100)
    assert evaluate_expression("floor(3.8)") == Fraction(3, 1)
    assert evaluate_expression("ceil(3.2)") == Fraction(4, 1)
    assert evaluate_expression("abs(-15)") == Fraction(15, 1)


def test_evaluator_dos_and_security_guards():
    # Disallow __import__
    with pytest.raises(VerificationError):
        evaluate_expression("__import__('os').system('dir')")

    # Disallow attribute access
    with pytest.raises(VerificationError):
        evaluate_expression("''.__class__.__mro__")

    # Disallow huge exponents
    with pytest.raises(VerificationError):
        evaluate_expression("2 ** 1000")

    # Disallow very long expression
    long_expr = "1 + " * 300 + "1"
    with pytest.raises(VerificationError):
        evaluate_expression(long_expr)

    # Disallow function calls outside whitelist
    with pytest.raises(VerificationError):
        evaluate_expression("eval('2+2')")

    # Disallow division by zero
    with pytest.raises(VerificationError):
        evaluate_expression("5 / 0")


# ==========================================
# 3. VERIFY QUESTION RULES & EDGE CASES
# ==========================================

def test_regression_sequence_question():
    """Verify Georgia sequence question regression:
    Stem: 'Each number is double the last, plus 1: 3, 7, 15, 31, ... What comes next?'
    Expression: '31*2+1'
    Answer: 63
    """
    q = Question(
        id="q-reg-seq",
        topic_id="5.PAR.3.1",
        difficulty=Difficulty.MEDIUM,
        verifier_type="expression_evaluation",
        stem="Each number is double the last, plus 1: 3, 7, 15, 31, ... What comes next?",
        expression="31*2+1",
        options=[
            Option(id="A", text="62", misconception="Forgot to add 1"),
            Option(id="B", text="63"),  # correct answer
            Option(id="C", text="64", misconception="Added 2 instead of 1"),
            Option(id="D", text="59", misconception="Subtracted instead of adding"),
        ],
        correct_index=1,
        explanation="Following the pattern, 31 * 2 + 1 = 62 + 1 = 63.",
    )
    result = verify_question(q)
    assert result.passed is True
    assert result.reasons == []


def test_verify_question_wrong_correct_index_fails():
    q = Question(
        id="q-bad-idx",
        topic_id="5.NR.1.1",
        difficulty=Difficulty.EASY,
        verifier_type="fraction_arithmetic",
        stem="What is 1/2 + 1/2?",
        expression="1/2 + 1/2",
        options=[
            Option(id="A", text="1"),
            Option(id="B", text="2", misconception="m1"),
            Option(id="C", text="3", misconception="m2"),
            Option(id="D", text="4", misconception="m3"),
        ],
        correct_index=2,  # Points to '3', but answer is '1' (index 0)
        explanation="1/2 + 1/2 = 1.",
    )
    result = verify_question(q)
    assert result.passed is False
    assert any("correct_index" in r for r in result.reasons)


def test_verify_question_duplicate_options_after_normalization_fails():
    """Two options that normalize to the same number (e.g. 1/2 and 0.5) must fail."""
    q = Question(
        id="q-dup-opts",
        topic_id="5.NR.1.1",
        difficulty=Difficulty.EASY,
        verifier_type="fraction_arithmetic",
        stem="What is 1/4 + 1/4?",
        expression="1/4 + 1/4",
        options=[
            Option(id="A", text="1/2"),
            Option(id="B", text="0.5", misconception="Same value decimal format"),
            Option(id="C", text="3/4", misconception="m2"),
            Option(id="D", text="1", misconception="m3"),
        ],
        correct_index=0,
        explanation="1/4 + 1/4 = 1/2.",
    )
    result = verify_question(q)
    assert result.passed is False
    assert any("not distinct" in r for r in result.reasons)


def test_verify_question_no_matching_option_fails():
    q = Question(
        id="q-no-match",
        topic_id="5.NR.1.1",
        difficulty=Difficulty.EASY,
        verifier_type="fraction_arithmetic",
        stem="What is 1/2 + 1/2?",
        expression="1/2 + 1/2",
        options=[
            Option(id="A", text="5", misconception="m1"),
            Option(id="B", text="2", misconception="m2"),
            Option(id="C", text="3", misconception="m3"),
            Option(id="D", text="4", misconception="m4"),
        ],
        correct_index=0,
        explanation="1/2 + 1/2 = 1.",
    )
    result = verify_question(q)
    assert result.passed is False
    assert any("No option matched" in r for r in result.reasons)


def test_verify_question_missing_misconception_tag_fails():
    q = Question(
        id="q-no-misc",
        topic_id="5.NR.1.1",
        difficulty=Difficulty.EASY,
        verifier_type="fraction_arithmetic",
        stem="What is 1/2 + 1/2?",
        expression="1/2 + 1/2",
        options=[
            Option(id="A", text="1"),
            Option(id="B", text="2"),  # Missing misconception!
            Option(id="C", text="3", misconception="m2"),
            Option(id="D", text="4", misconception="m3"),
        ],
        correct_index=0,
        explanation="1/2 + 1/2 = 1.",
    )
    result = verify_question(q)
    assert result.passed is False
    assert any("missing a misconception tag" in r for r in result.reasons)


def test_verify_question_unresolved_placeholder_fails():
    q = Question(
        id="q-placeholder",
        topic_id="5.NR.1.1",
        difficulty=Difficulty.EASY,
        verifier_type="fraction_arithmetic",
        stem="What is {var_x} + 2?",
        expression="1 + 2",
        options=[
            Option(id="A", text="3"),
            Option(id="B", text="2", misconception="m1"),
            Option(id="C", text="4", misconception="m2"),
            Option(id="D", text="5", misconception="m3"),
        ],
        correct_index=0,
        explanation="1 + 2 = 3.",
    )
    result = verify_question(q)
    assert result.passed is False
    assert any("unresolved placeholder" in r for r in result.reasons)


# ==========================================
# 4. VERIFY LESSON TESTS
# ==========================================

def test_verify_lesson_passing():
    lesson = Lesson(
        title="Sum of Fractions",
        big_idea="Combining parts of a whole.",
        explanation="When denominators are common, sum numerators.",
        worked_example=[
            WorkedStep(step=1, text="Setup", math="1/4 + 2/4"),
            WorkedStep(step=2, text="Calculate numerator", math="1 + 2 = 3"),
            WorkedStep(step=3, text="Final fraction", math="3/4"),
        ],
        key_vocab=["Numerator", "Denominator"],
        real_world_example="Sharing slices of bread.",
        common_mistakes=["Adding denominators"],
    )
    res = verify_lesson(lesson)
    assert res.passed is True
    assert res.reasons == []


def test_verify_lesson_broken_math():
    lesson = Lesson(
        title="Sum of Fractions",
        big_idea="Combining parts of a whole.",
        explanation="When denominators are common, sum numerators.",
        worked_example=[
            WorkedStep(step=1, text="Setup", math="1/0"),  # Syntax/division by zero
            WorkedStep(step=2, text="Final fraction", math="3/4"),
        ],
        key_vocab=["Numerator", "Denominator"],
        real_world_example="Sharing slices.",
        common_mistakes=["Adding denominators"],
    )
    res = verify_lesson(lesson)
    assert res.passed is False
    assert len(res.reasons) > 0


# ==========================================
# 5. ALL 15 TOPIC VERIFIER TYPES: PASS & FAIL
# ==========================================

ALL_VERIFIER_TEST_CASES = [
    {
        "verifier_type": "fraction_arithmetic",
        "expr_pass": "1/3 + 1/6",
        "opts_pass": ["1/2", "2/9", "1/6", "5/6"],
        "expr_fail": "1/3 + 1/6",
        "opts_fail": ["3/4", "2/9", "1/6", "5/6"],  # Answer is 1/2, not 3/4
    },
    {
        "verifier_type": "decimal_arithmetic",
        "expr_pass": "2.4 + 1.35",
        "opts_pass": ["3.75", "3.49", "4.0", "3.79"],
        "expr_fail": "2.4 + 1.35",
        "opts_fail": ["5.0", "3.49", "4.0", "3.79"],
    },
    {
        "verifier_type": "decimal_comparison",
        "expr_pass": "compare(0.45, 0.5)",
        "opts_pass": ["<", ">", "=", "none"],
        "expr_fail": "compare(0.45, 0.5)",
        "opts_fail": [">", "<", "=", "none"],  # Incorrectly claims 0.45 > 0.5 at index 0
    },
    {
        "verifier_type": "volume_geometry",
        "expr_pass": "volume_box(4, 5, 6)",
        "opts_pass": ["120", "15", "60", "24"],
        "expr_fail": "volume_box(4, 5, 6)",
        "opts_fail": ["100", "15", "60", "24"],
    },
    {
        "verifier_type": "division_with_remainder",
        "expr_pass": "29 // 4",
        "opts_pass": ["7", "6", "8", "5"],
        "expr_fail": "29 // 4",
        "opts_fail": ["6", "7", "8", "5"],  # 29 // 4 is 7
    },
    {
        "verifier_type": "rate_division",
        "expr_pass": "unit_rate(180, 3)",
        "opts_pass": ["60", "50", "90", "183"],
        "expr_fail": "unit_rate(180, 3)",
        "opts_fail": ["45", "50", "90", "183"],
    },
    {
        "verifier_type": "percent_calculation",
        "expr_pass": "percent_of(20, 150)",
        "opts_pass": ["30", "20", "40", "25"],
        "expr_fail": "percent_of(20, 150)",
        "opts_fail": ["15", "20", "40", "25"],
    },
    {
        "verifier_type": "equation_solving",
        "expr_pass": "solve_linear('4x - 8 = 16')",
        "opts_pass": ["6", "4", "2", "8"],
        "expr_fail": "solve_linear('4x - 8 = 16')",
        "opts_fail": ["2", "4", "5", "8"],
    },
    {
        "verifier_type": "statistical_center",
        "expr_pass": "mean(10, 20, 30, 40)",
        "opts_pass": ["25", "20", "30", "100"],
        "expr_fail": "mean(10, 20, 30, 40)",
        "opts_fail": ["20", "22", "30", "100"],
    },
    {
        "verifier_type": "integer_arithmetic",
        "expr_pass": "-12 + 5",
        "opts_pass": ["-7", "7", "-17", "17"],
        "expr_fail": "-12 + 5",
        "opts_fail": ["7", "-5", "-17", "17"],
    },
    {
        "verifier_type": "integer_comparison",
        "expr_pass": "compare(-8, -3)",
        "opts_pass": ["<", ">", "=", "none"],
        "expr_fail": "compare(-8, -3)",
        "opts_fail": [">", "<", "=", "none"],
    },
    {
        "verifier_type": "ratio_comparison",
        "expr_pass": "ratio_simplify(12, 18)",
        "opts_pass": ["2:3", "3:2", "1:2", "3:4"],
        "expr_fail": "ratio_simplify(12, 18)",
        "opts_fail": ["3:4", "3:2", "1:2", "1:3"],
    },
    {
        "verifier_type": "exponent_evaluation",
        "expr_pass": "3 ** 3",
        "opts_pass": ["27", "9", "81", "6"],
        "expr_fail": "3 ** 3",
        "opts_fail": ["9", "18", "81", "6"],
    },
    {
        "verifier_type": "expression_equivalence",
        "expr_pass": "ratio_simplify(4, 12)",
        "opts_pass": ["1:3", "1:4", "2:5", "3:4"],
        "expr_fail": "ratio_simplify(4, 12)",
        "opts_fail": ["1:2", "1:4", "2:5", "3:4"],
    },
    {
        "verifier_type": "expression_evaluation",
        "expr_pass": "5 * 4 - 3",
        "opts_pass": ["17", "5", "20", "23"],
        "expr_fail": "5 * 4 - 3",
        "opts_fail": ["5", "10", "20", "23"],
    },
]


@pytest.mark.parametrize("case", ALL_VERIFIER_TEST_CASES, ids=lambda c: c["verifier_type"])
def test_all_15_verifier_types_pass_and_fail(case):
    v_type = case["verifier_type"]

    # Passing question
    q_pass = Question(
        id=f"q-pass-{v_type}",
        topic_id="test.topic",
        difficulty=Difficulty.MEDIUM,
        verifier_type=v_type,
        stem=f"Test question for {v_type}",
        expression=case["expr_pass"],
        options=[
            Option(id="A", text=case["opts_pass"][0]),
            Option(id="B", text=case["opts_pass"][1], misconception="Wrong 1"),
            Option(id="C", text=case["opts_pass"][2], misconception="Wrong 2"),
            Option(id="D", text=case["opts_pass"][3], misconception="Wrong 3"),
        ],
        correct_index=0,
        explanation="Step-by-step correct calculation.",
    )
    res_pass = verify_question(q_pass)
    assert res_pass.passed is True, f"Failed passing test for {v_type}: {res_pass.reasons}"

    # Failing question
    q_fail = Question(
        id=f"q-fail-{v_type}",
        topic_id="test.topic",
        difficulty=Difficulty.MEDIUM,
        verifier_type=v_type,
        stem=f"Test question for {v_type}",
        expression=case["expr_fail"],
        options=[
            Option(id="A", text=case["opts_fail"][0]),
            Option(id="B", text=case["opts_fail"][1], misconception="Wrong 1"),
            Option(id="C", text=case["opts_fail"][2], misconception="Wrong 2"),
            Option(id="D", text=case["opts_fail"][3], misconception="Wrong 3"),
        ],
        correct_index=0,
        explanation="Step-by-step calculation.",
    )
    res_fail = verify_question(q_fail)
    assert res_fail.passed is False, f"Failed failing test for {v_type}: should have rejected"


def test_divmod_rem_and_equiv_verifiers():
    # Test divmod_rem question
    q_div = Question(
        id="q-divmod-test",
        topic_id="g5-divide",
        difficulty=Difficulty.MEDIUM,
        verifier_type="division_with_remainder",
        stem="Divide 125 by 6. What is the quotient and remainder?",
        expression="divmod_rem(125, 6)",
        options=[
            Option(id="A", text="20 R 5"),
            Option(id="B", text="20 R 3", misconception="calculation_error"),
            Option(id="C", text="21 R 1", misconception="rounded_wrong"),
            Option(id="D", text="19 R 5", misconception="underestimated_quotient"),
        ],
        correct_index=0,
        explanation="125 = 6 * 20 + 5, so the quotient is 20 with remainder 5.",
    )
    assert verify_question(q_div).passed is True

    # Test check_equiv question
    q_eq = Question(
        id="q-equiv-test",
        topic_id="g6-equiv-expressions",
        difficulty=Difficulty.MEDIUM,
        verifier_type="expression_equivalence",
        stem="Are 3 * (2 * x + 4) and 6 * x + 12 equivalent?",
        expression="check_equiv('3 * (2 * x + 4)', '6 * x + 12')",
        options=[
            Option(id="A", text="equivalent"),
            Option(id="B", text="not equivalent", misconception="distributed_only_to_first_term"),
            Option(id="C", text="equal only when x=0", misconception="tested_single_point"),
            Option(id="D", text="cannot be determined", misconception="confused_equivalence"),
        ],
        correct_index=0,
        explanation="Distributing 3 across (2x + 4) gives 6x + 12, so the expressions are equivalent.",
    )
    assert verify_question(q_eq).passed is True
