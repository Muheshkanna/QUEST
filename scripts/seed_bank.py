"""Deterministic Seed Question Generator for Math Quest.

Generates at least 6 verified questions per difficulty level (18+ questions per topic)
for ALL 20 topics aligned with Georgia Mathematics Standards.
Uses a seeded PRNG for reproducible, deterministic output without LLM calls.
All questions pass api._lib.verifier.verify_question.
"""

from __future__ import annotations
import json
import os
import random
import sys
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List, Tuple

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api._lib.schemas import BankFile, Difficulty, Option, Question
from api._lib.verifier import verify_question, normalize_option


def create_question_entry(
    topic: Dict[str, Any],
    difficulty: Difficulty,
    stem: str,
    expression: str,
    options: List[Option],
    correct_index: int,
    explanation: str,
    hint: str,
    q_id: str,
    params: Optional[Dict[str, Any]] = None,
    template_id: Optional[str] = None,
) -> Question:
    q = Question(
        id=q_id,
        topic_id=topic["id"],
        standard=topic["standard"],
        difficulty=difficulty,
        verifier_type=topic["verifier_type"],
        stem=stem,
        expression=expression,
        options=options,
        correct_index=correct_index,
        explanation=explanation,
        hint=hint,
        model="template-seed",
        prompt_version="seed-v1",
        verified=True,
        params=params,
        template_id=template_id,
    )
    result = verify_question(q)
    if not result.passed:
        raise ValueError(f"Failed verification for {q.id} in {topic['id']}: {result.reasons}\nExpr: {expression}\nOptions: {[o.text for o in options]}")
    return q
# Duplicate block removed


def build_options_with_misconceptions(
    correct_str: str,
    distractors: List[Tuple[str, str]],  # (text, misconception_tag)
    rng: random.Random,
) -> Tuple[List[Option], int]:
    """Given correct text and candidate distractors with misconception tags,
    ensures 3 unique distractors, shuffles them with the correct option,
    and returns (options, correct_index).
    """
    correct_norm, _ = normalize_option(correct_str)
    unique_distractors: List[Tuple[str, str]] = []
    seen_norm = {correct_norm}

    for text, tag in distractors:
        norm, _ = normalize_option(text)
        if norm not in seen_norm:
            seen_norm.add(norm)
            unique_distractors.append((text, tag))
        if len(unique_distractors) == 3:
            break

    # If duplicate values or collisions occurred, generate computed variations
    attempt = 1
    default_tag = distractors[0][1] if distractors else "calculation_error"
    while len(unique_distractors) < 3 and attempt < 30:
        _, frac = normalize_option(correct_str)
        if frac is not None:
            # Fraction/number variation
            if frac.denominator == 1:
                # Integer
                cand = str(frac.numerator + (attempt if attempt % 2 == 1 else -attempt))
            else:
                # Fraction
                cand_num = max(1, frac.numerator + (attempt if attempt % 2 == 1 else -attempt))
                cand = f"{cand_num}/{frac.denominator}"
        else:
            cand = f"{correct_str} (Alt {attempt})"

        cand_norm, _ = normalize_option(cand)
        if cand_norm not in seen_norm:
            seen_norm.add(cand_norm)
            tag = distractors[len(unique_distractors) % len(distractors)][1] if distractors else default_tag
            unique_distractors.append((cand, tag))
        attempt += 1

    if len(unique_distractors) < 3:
        raise ValueError(f"Could not find 3 distinct distractors for '{correct_str}'. Found: {unique_distractors}")

    # Build items: (text, tag, is_correct)
    items = [(correct_str, None, True)] + [(d[0], d[1], False) for d in unique_distractors]
    rng.shuffle(items)

    correct_index = -1
    options = []
    for idx, (txt, tag, is_corr) in enumerate(items):
        opt_id = chr(ord("A") + idx)
        if is_corr:
            correct_index = idx
            options.append(Option(id=opt_id, text=txt, misconception=None))
        else:
            options.append(Option(id=opt_id, text=txt, misconception=tag))

    return options, correct_index


# =====================================================================
# TOPIC SPECIFIC GENERATORS
# =====================================================================

def gen_g5_place_value(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    contexts = [
        ("ancient magic crystals", "crystals"),
        ("enchanted tree seeds", "seeds"),
        ("glowing starlight embers", "embers"),
        ("royal vault gold coins", "coins"),
        ("forest spirit dew drops", "dew drops"),
        ("celestial library scrolls", "scrolls"),
    ]
    for i in range(count):
        ctx_title, item = contexts[i % len(contexts)]
        if diff == Difficulty.EASY:
            base = rng.choice([15, 24, 38, 42, 65, 87])
            power = rng.choice([10, 100])
            ans = base * power
            expr = f"{base} * {power}"
            stem = f"The woodland scholars discovered {base} chests of {ctx_title}. Each chest contains {power} {item}. How many {item} are there in total?"
            dists = [
                (str(base + power), "confuses_ten_times_with_add_ten"),
                (str(base) + str(power), "additive_power_of_ten"),
                (str(base * (power // 10)), "decimal_point_shift_reversed"),
            ]
            hint = f"Multiplying by {power} shifts each digit {1 if power == 10 else 2} place values to the left."
            explanation = f"{base} groups of {power} equals {base} * {power} = {ans}."
        elif diff == Difficulty.MEDIUM:
            base = rng.choice([120, 250, 480, 560, 720])
            power = rng.choice([100, 1000])
            ans = base * power
            expr = f"{base} * {power}"
            stem = f"A caravan transports {base} pouches of {ctx_title}, each holding {power} {item}. What is the total count of {item}?"
            dists = [
                (str(base + power), "confuses_ten_times_with_add_ten"),
                (str(base) + str(power), "additive_power_of_ten"),
                (str(ans // 10), "decimal_point_shift_reversed"),
            ]
            hint = "Count how many zeros are added when multiplying whole numbers by a power of 10."
            explanation = f"Multiplying {base} by {power} shifts the place values, giving {ans}."
        else: # HARD
            base = rng.choice([3500, 4200, 6800, 8400])
            divisor = rng.choice([10, 100])
            ans = base // divisor
            expr = f"{base} // {divisor}"
            stem = f"An observatory gathers {base} {item} and divides them equally across {divisor} star-chambers. How many {item} are in each chamber?"
            dists = [
                (str(base * divisor), "decimal_point_shift_reversed"),
                (str(base - divisor), "confuses_ten_times_with_add_ten"),
                (str(ans // 10), "additive_power_of_ten"),
            ]
            hint = f"Dividing by {divisor} shifts the place value of each digit {1 if divisor == 10 else 2} spots to the right."
            explanation = f"{base} divided equally by {divisor} is {ans}."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_decimal_ops(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            a = round(rng.uniform(1.1, 4.9), 1)
            b = round(rng.uniform(1.1, 4.9), 1)
            ans = round(a + b, 1)
            expr = f"{a} + {b}"
            stem = f"A magical potion needs {a} liters of sun-water and {b} liters of moon-dew. What is the total volume in liters?"
            dists = [
                (str(round(a + b + 0.1, 1)), "carries_over_decimal_point_incorrectly"),
                (str(round(abs(a - b), 1)), "unaligned_decimals"),
                (str(round(a + b + 1.0, 1)), "ignores_empty_place_value"),
            ]
            hint = "Line up the decimal points and add each column from tenths to ones."
            explanation = f"{a} + {b} = {ans} liters."
        elif diff == Difficulty.MEDIUM:
            a = round(rng.uniform(5.25, 9.75), 2)
            b = round(rng.uniform(1.1, 3.8), 1)
            ans = round(a + b, 2)
            expr = f"{a} + {b}"
            stem = f"During a trail run, an explorer traveled {a} miles in the morning and {b} miles in the afternoon. What was the total distance in miles?"
            dists = [
                (str(round(a + (b / 10), 2)), "unaligned_decimals"),
                (str(round(a + b - 0.1, 2)), "ignores_empty_place_value"),
                (str(round(a + b + 0.09, 2)), "carries_over_decimal_point_incorrectly"),
            ]
            hint = f"Remember that {b} is the same as {b:.2f} when lining up decimals."
            explanation = f"Lining up the hundredths place: {a:.2f} + {b:.2f} = {ans:.2f} miles."
        else: # HARD
            a = round(rng.uniform(8.1, 15.5), 1)
            b = round(rng.uniform(2.25, 5.75), 2)
            ans = round(a - b, 2)
            expr = f"{a} - {b}"
            stem = f"A spool has {a} meters of ribbon. A craftsperson cuts {b} meters for a banner. How many meters of ribbon remain?"
            dists = [
                (str(round(a - int(b) + (b - int(b)), 2)), "ignores_empty_place_value"),
                (str(round(a + b, 2)), "unaligned_decimals"),
                (str(round(ans + 0.1, 2)), "carries_over_decimal_point_incorrectly"),
            ]
            hint = f"Write {a} as {a:.2f} before subtracting {b} so you can regroup properly."
            explanation = f"{a:.2f} - {b} = {ans:.2f} meters."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_decimal_compare_round(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            a = round(rng.uniform(0.1, 0.9), 1)
            b = round(rng.uniform(0.1, 0.9), 1)
            while a == b:
                b = round(rng.uniform(0.1, 0.9), 1)
            expr = f"compare({a}, {b})"
            ans = ">" if a > b else "<"
            stem = f"Which comparison symbol makes the statement true: {a} ___ {b}?"
            dists = [
                ("=" if ans != "=" else "<", "confuses_tenths_and_hundredths"),
                ("<" if ans == ">" else ">", "longer_decimal_is_larger"),
                ("none", "round_down_without_truncation_rule"),
            ]
            hint = "Look at the tenths place to compare the two values."
            explanation = f"Since {a} is {'greater than' if a > b else 'less than'} {b}, the correct symbol is '{ans}'."
        elif diff == Difficulty.MEDIUM:
            # comparing tenths with hundredths/thousandths (e.g. 0.4 vs 0.35 or 0.5 vs 0.125)
            a_tenth = rng.choice([3, 4, 5, 6, 7])
            a = a_tenth / 10
            b = (a_tenth * 10 - rng.choice([2, 5, 8])) / 100
            expr = f"compare({a}, {b})"
            ans = ">"
            stem = f"Which symbol correctly completes the comparison: {a} ___ {b}?"
            dists = [
                ("<", "longer_decimal_is_larger"),
                ("=", "confuses_tenths_and_hundredths"),
                ("none", "round_down_without_truncation_rule"),
            ]
            hint = f"Remember that {a} can be written as {a:.2f}. Compare tenths first."
            explanation = f"{a:.2f} is greater than {b}, so the correct symbol is '{ans}'."
        else: # HARD - Rounding decimals to hundredths
            val = round(rng.uniform(2.115, 8.895), 3)
            rounded = round(val, 2)
            expr = f"round_to({val}, 2)"
            stem = f"What is {val} rounded to the nearest hundredth?"
            ans = f"{rounded:.2f}"
            truncated = f"{float(f'{val:.2f}'):.2f}"
            # Ensure 3 distinct distractors
            cand1 = truncated if truncated != ans else f"{rounded - 0.01:.2f}"
            cand2 = f"{rounded + 0.01:.2f}"
            cand3 = f"{rounded + 0.10:.2f}"
            dists = [
                (cand1, "round_down_without_truncation_rule"),
                (cand2, "confuses_tenths_and_hundredths"),
                (cand3, "longer_decimal_is_larger"),
            ]
            hint = "Look at the thousandths place (the third digit after the decimal point). If it is 5 or more, round up."
            explanation = f"The thousandths digit tells us whether to round up. {val} rounded to hundredths is {ans}."

        opts, c_idx = build_options_with_misconceptions(ans, dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_fractions_add(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY: # same denominators
            den = rng.choice([5, 6, 7, 8, 9, 10])
            n1 = rng.randint(1, den - 3)
            n2 = rng.randint(1, den - n1 - 1)
            ans_frac = Fraction(n1 + n2, den)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"{n1}/{den} + {n2}/{den}"
            stem = f"A recipe calls for {n1}/{den} cup of honey and {n2}/{den} cup of warm milk. How much liquid is added in total?"
            dists = [
                (f"{n1 + n2}/{den + den}", "add_denominators"),
                (f"{n1}/{den}", "find_common_denom_without_renaming_numerators"),
                (f"{abs(n1 - n2)}/{den}", "subtracts_smaller_from_larger_regardless_of_order"),
            ]
            hint = "When fractions share the same denominator, keep the denominator and add the numerators."
            explanation = f"{n1}/{den} + {n2}/{den} = {n1 + n2}/{den} = {ans_str}."
        elif diff == Difficulty.MEDIUM: # one denominator multiple of other
            den1 = rng.choice([2, 3, 4, 5])
            factor = rng.choice([2, 3])
            den2 = den1 * factor
            n1 = 1
            n2 = 1
            ans_frac = Fraction(n1, den1) + Fraction(n2, den2)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"{n1}/{den1} + {n2}/{den2}"
            stem = f"During garden work, Maya raked {n1}/{den1} of the lawn in the morning and {n2}/{den2} of the lawn after lunch. What fraction of the lawn did she rake altogether?"
            dists = [
                (f"{n1 + n2}/{den1 + den2}", "add_denominators"),
                (f"{n1 + n2}/{den2}", "find_common_denom_without_renaming_numerators"),
                (f"1/{den1 + den2}", "subtracts_smaller_from_larger_regardless_of_order"),
            ]
            hint = f"Convert {n1}/{den1} to an equivalent fraction with a denominator of {den2}."
            explanation = f"{n1}/{den1} = {n1*factor}/{den2}. Adding {n2}/{den2} gives {ans_str}."
        else: # HARD - unlike denominators
            den1, den2 = rng.choice([(2, 3), (3, 4), (3, 5), (4, 5)])
            n1, n2 = 1, 1
            ans_frac = Fraction(n1, den1) + Fraction(n2, den2)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"{n1}/{den1} + {n2}/{den2}"
            stem = f"An artisan mixed {n1}/{den1} quart of indigo dye with {n2}/{den2} quart of violet dye. What is the total volume of dye in quarts?"
            dists = [
                (f"{n1 + n2}/{den1 + den2}", "add_denominators"),
                (f"{n1 + n2}/{den1 * den2}", "find_common_denom_without_renaming_numerators"),
                (f"{abs(n1 - n2)}/{den1 * den2}", "subtracts_smaller_from_larger_regardless_of_order"),
            ]
            hint = f"Find a common denominator for {den1} and {den2} by multiplying them together."
            explanation = f"The common denominator is {den1*den2}. Finding equivalent fractions gives {ans_str}."

        opts, c_idx = build_options_with_misconceptions(ans_str, dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_fractions_multiply(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            w = rng.choice([2, 3, 4])
            num, den = 1, rng.choice([3, 4, 5, 6])
            ans_frac = Fraction(w * num, den)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"{w} * {num}/{den}"
            stem = f"A baker needs {num}/{den} cup of brown sugar for each loaf of banana bread. How much brown sugar is needed for {w} loaves?"
            dists = [
                (f"{w * num}/{w * den}", "multiplies_both_by_whole_number"),
                (f"{w + num}/{den}", "believes_multiplication_always_increases"),
                (f"{num}/{w * den}", "cross_multiplies_instead_of_multiplying_straight"),
            ]
            hint = f"Think of {w} * ({num}/{den}) as adding {num}/{den} together {w} times."
            explanation = f"{w} * {num}/{den} = {w * num}/{den} = {ans_str}."
        elif diff == Difficulty.MEDIUM:
            w = rng.choice([4, 6, 8, 9, 10])
            num, den = 2, 3
            ans_frac = Fraction(w * num, den)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"{w} * {num}/{den}"
            stem = f"A running coach has students run {num}/{den} of a mile {w} times during practice. What is the total distance run in miles?"
            dists = [
                (f"{w * num}/{w * den}", "multiplies_both_by_whole_number"),
                (f"{w * den}/{num}", "cross_multiplies_instead_of_multiplying_straight"),
                (f"{w + num}/{den}", "believes_multiplication_always_increases"),
            ]
            hint = f"Multiply the whole number {w} by the numerator {num}, then keep the denominator {den}."
            explanation = f"{w} * {num}/{den} = {w * num}/{den} = {ans_str}."
        else: # HARD
            w = rng.choice([5, 7, 12])
            num, den = rng.choice([(3, 4), (2, 5), (3, 8)])
            ans_frac = Fraction(w * num, den)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"{w} * {num}/{den}"
            stem = f"A science kit experiment uses {num}/{den} ounce of mineral powder per trial. How many ounces of powder are required for {w} trials?"
            dists = [
                (f"{w * num}/{w * den}", "multiplies_both_by_whole_number"),
                (f"{w}/{den}", "cross_multiplies_instead_of_multiplying_straight"),
                (f"{w * 2}/{den}", "believes_multiplication_always_increases"),
            ]
            hint = f"Convert {w} to a fraction {w}/1 and multiply straight across."
            explanation = f"({w}/1) * ({num}/{den}) = {ans_str} ounces."

        opts, c_idx = build_options_with_misconceptions(ans_str, dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_fractions_divide_unit(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            w = rng.choice([2, 3, 4])
            den = rng.choice([2, 3, 4])
            # whole / (1/den)
            ans = w * den
            expr = f"{w} // (1/{den})"
            stem = f"Chef Marcus has {w} large pizzas. If each serving is 1/{den} of a pizza, how many servings can he make?"
            dists = [
                (f"1/{ans}", "confuses_division_order"),
                (f"{w}/{den}", "multiplies_instead_of_dividing"),
                (str(w + den), "fractional_quotient_confused_with_remainder"),
            ]
            hint = f"Ask yourself: How many 1/{den} slices fit into 1 whole? Then multiply that by {w}."
            explanation = f"{w} divided by 1/{den} equals {w} * {den} = {ans} servings."
        elif diff == Difficulty.MEDIUM:
            # (1/den) / w -> 1 / (den * w)
            den = rng.choice([3, 4, 5])
            w = rng.choice([2, 3])
            ans_frac = Fraction(1, den * w)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"(1/{den}) / {w}"
            stem = f"A painter shares 1/{den} gallon of primer equally among {w} small model houses. What fraction of a gallon does each house get?"
            dists = [
                (str(den * w), "confuses_division_order"),
                (f"{w}/{den}", "multiplies_instead_of_dividing"),
                (f"1/{den + w}", "fractional_quotient_confused_with_remainder"),
            ]
            hint = f"When dividing 1/{den} into {w} equal pieces, each piece gets smaller. Multiply the denominator by {w}."
            explanation = f"(1/{den}) / {w} = 1 / ({den} * {w}) = {ans_str} gallon."
        else: # HARD
            w = rng.choice([5, 6, 8])
            den = rng.choice([3, 4, 6])
            ans = w * den
            expr = f"{w} // (1/{den})"
            stem = f"A seamstress has a roll with {w} yards of satin ribbon. Each craft rosette requires 1/{den} yard of ribbon. How many rosettes can she complete?"
            dists = [
                (f"1/{ans}", "confuses_division_order"),
                (f"{w}/{den}", "multiplies_instead_of_dividing"),
                (str(w * 2), "fractional_quotient_confused_with_remainder"),
            ]
            hint = f"Each whole yard yields {den} pieces. Multiply {w} by {den}."
            explanation = f"{w} divided by 1/{den} = {w} * {den} = {ans} rosettes."

        opts, c_idx = build_options_with_misconceptions(str(ans if diff != Difficulty.MEDIUM else ans_str), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_volume(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            l, w, h = rng.choice([(2, 3, 4), (2, 2, 5), (3, 3, 3), (2, 4, 5)])
            ans = l * w * h
            expr = f"volume_box({l}, {w}, {h})"
            stem = f"A rectangular jewelry box has a length of {l} cm, a width of {w} cm, and a height of {h} cm. What is its volume in cubic centimeters?"
            dists = [
                (str(l + w + h), "adds_dimensions_instead_of_multiplying"),
                (str(l * w), "forgets_height_layering"),
                (str(2 * (l * w + l * h + w * h)), "confuses_surface_area_with_volume"),
            ]
            hint = "Volume is calculated by multiplying length * width * height."
            explanation = f"Volume = {l} * {w} * {h} = {ans} cubic centimeters."
        elif diff == Difficulty.MEDIUM:
            l, w, h = rng.choice([(4, 5, 6), (5, 6, 8), (3, 7, 4), (6, 6, 4)])
            ans = l * w * h
            expr = f"volume_box({l}, {w}, {h})"
            stem = f"An aquarium shaped like a rectangular prism measures {l} feet long, {w} feet wide, and {h} feet high. What is its total volume in cubic feet?"
            dists = [
                (str(l + w + h), "adds_dimensions_instead_of_multiplying"),
                (str(l * w), "forgets_height_layering"),
                (str(2 * (l * w + l * h + w * h)), "confuses_surface_area_with_volume"),
            ]
            hint = f"First find the base area ({l} * {w}), then multiply by the height ({h})."
            explanation = f"Base area = {l * w}. Multiplying by height {h} gives {ans} cubic feet."
        else: # HARD
            l, w, h = rng.choice([(8, 10, 12), (7, 9, 15), (6, 12, 10)])
            ans = l * w * h
            expr = f"volume_box({l}, {w}, {h})"
            stem = f"A storage crate is packed solid with 1-meter unit cubes. The crate is {l} meters long, {w} meters wide, and {h} meters tall. How many unit cubes pack the crate with no gaps?"
            dists = [
                (str(l + w + h), "adds_dimensions_instead_of_multiplying"),
                (str(l * w), "forgets_height_layering"),
                (str(2 * (l * w + l * h + w * h)), "confuses_surface_area_with_volume"),
            ]
            hint = "Multiply the three dimensions to find the total number of unit cubes."
            explanation = f"Total cubes = {l} * {w} * {h} = {ans} unit cubes."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_multiply(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            a = rng.choice([23, 34, 45, 52, 61])
            b = rng.choice([12, 15, 21, 24])
            ans = a * b
            expr = f"{a} * {b}"
            stem = f"A bookstore received {b} boxes of adventure novels. Each box holds {a} books. How many novels were received in total?"
            dists = [
                (str(ans - 100), "forgets_tens_place_zero"),
                (str(a + b), "miscalculates_regrouping_additions"),
                (str(ans + 50), "aligns_partial_products_incorrectly"),
            ]
            hint = f"Multiply {a} by the ones digit of {b}, then by the tens digit, and add the partial products."
            explanation = f"{a} * {b} = {ans} books."
        elif diff == Difficulty.MEDIUM:
            a = rng.choice([142, 215, 324, 412])
            b = rng.choice([23, 32, 41, 18])
            ans = a * b
            expr = f"{a} * {b}"
            stem = f"A community theater sold {b} tickets for each of its {a} weekend performances this season. What was the total number of tickets sold?"
            dists = [
                (str(ans - 200), "forgets_tens_place_zero"),
                (str(a * (b % 10)), "aligns_partial_products_incorrectly"),
                (str(ans + 120), "miscalculates_regrouping_additions"),
            ]
            hint = "Be sure to put a 0 in the ones place when multiplying by the tens digit."
            explanation = f"{a} * {b} = {ans} tickets."
        else: # HARD
            a = rng.choice([528, 642, 735, 814])
            b = rng.choice([35, 48, 62, 74])
            ans = a * b
            expr = f"{a} * {b}"
            stem = f"An apple orchard packs {a} crates of apples each harvest week for {b} weeks. What is the total count of crates packed?"
            dists = [
                (str(ans - 500), "forgets_tens_place_zero"),
                (str(ans + 250), "aligns_partial_products_incorrectly"),
                (str(ans - 1000), "miscalculates_regrouping_additions"),
            ]
            hint = "Carefully add partial products after multiplying by both digits."
            explanation = f"{a} crates * {b} weeks = {ans} total crates."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_divide(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            divisor = rng.choice([4, 5, 6, 7])
            quotient = rng.choice([12, 14, 15, 18])
            rem = rng.randint(1, divisor - 1)
            dividend = quotient * divisor + rem
            ans_str = f"{quotient} R {rem}"
            expr = f"divmod_rem({dividend}, {divisor})"
            stem = f"A camp counselor has {dividend} stickers to give out equally among {divisor} campers. How many stickers does each camper get and how many are left over?"
            dists = [
                (f"{quotient} R {rem + 1}", "subtraction_substep_error"),
                (f"{quotient + 1} R 0", "ignores_remainder_context"),
                (f"{quotient - 1} R {rem + divisor}", "misplaces_quotient_digit_column"),
            ]
            hint = f"Find how many times {divisor} goes into {dividend}. The leftover amount is the remainder."
            explanation = f"{dividend} / {divisor} = {quotient} with {rem} leftover ({ans_str})."
        elif diff == Difficulty.MEDIUM:
            divisor = rng.choice([12, 14, 15, 16])
            quotient = rng.choice([21, 24, 28, 32])
            rem = rng.randint(1, divisor - 1)
            dividend = quotient * divisor + rem
            ans_str = f"{quotient} R {rem}"
            expr = f"divmod_rem({dividend}, {divisor})"
            stem = f"A packaging machine sorts {dividend} pencils into packs of {divisor}. How many full packs are filled, and what is the remainder?"
            dists = [
                (f"{quotient} R {rem + 2}", "subtraction_substep_error"),
                (f"{quotient - 1} R {rem}", "misplaces_quotient_digit_column"),
                (f"{quotient + 1} R 0", "ignores_remainder_context"),
            ]
            hint = f"Use long division to divide {dividend} by {divisor}."
            explanation = f"{dividend} = ({divisor} * {quotient}) + {rem}, so the answer is {ans_str}."
        else: # HARD
            divisor = rng.choice([22, 25, 34, 45])
            quotient = rng.choice([35, 42, 56, 64])
            rem = rng.randint(1, divisor - 1)
            dividend = quotient * divisor + rem
            ans_str = f"{quotient} R {rem}"
            expr = f"divmod_rem({dividend}, {divisor})"
            stem = f"A charity event collects {dividend} cans of soup to pack into relief crates of {divisor} cans each. What is the quotient and remainder?"
            dists = [
                (f"{quotient} R {rem + 3}", "subtraction_substep_error"),
                (f"{quotient + 1} R {rem}", "misplaces_quotient_digit_column"),
                (f"{quotient} R 0", "ignores_remainder_context"),
            ]
            hint = f"Divide step by step: estimate how many times {divisor} fits into each place value."
            explanation = f"{dividend} divided by {divisor} gives a quotient of {quotient} and remainder {rem} ({ans_str})."

        opts, c_idx = build_options_with_misconceptions(ans_str, dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g5_order_ops(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            a, b, c = rng.choice([(3, 4, 5), (2, 6, 3), (4, 5, 2), (5, 3, 4)])
            ans = a + b * c
            expr = f"{a} + {b} * {c}"
            stem = f"Evaluate the numerical expression: {a} + {b} * {c}"
            dists = [
                (str((a + b) * c), "left_to_right_disregards_precedence"),
                (str(ans + 2), "addition_before_subtraction_dogma"),
                (str(a * b + c), "ignores_parentheses_grouping"),
            ]
            hint = "In order of operations, perform multiplication before addition."
            explanation = f"Multiply first: {b} * {c} = {b * c}. Then add: {a} + {b * c} = {ans}."
        elif diff == Difficulty.MEDIUM:
            a, b, c, d = rng.choice([(18, 6, 2, 4), (24, 4, 3, 5), (30, 5, 2, 6)])
            ans = (a // b) + (c * d)
            expr = f"{a} // {b} + {c} * {d}"
            stem = f"What is the value of the expression: {a} // {b} + {c} * {d}?"
            dists = [
                (str(((a // b) + c) * d), "left_to_right_disregards_precedence"),
                (str(ans - 3), "addition_before_subtraction_dogma"),
                (str(ans + 5), "ignores_parentheses_grouping"),
            ]
            hint = "Evaluate division and multiplication from left to right before adding."
            explanation = f"{a} // {b} = {a // b}, and {c} * {d} = {c * d}. Then {a // b} + {c * d} = {ans}."
        else: # HARD
            a, b, c, d = rng.choice([(4, 3, 2, 5), (5, 2, 4, 3), (6, 4, 1, 2)])
            # a * (b + c) - d
            ans = a * (b + c) - d
            expr = f"{a} * ({b} + {c}) - {d}"
            stem = f"Evaluate the following expression with parentheses: {a} * ({b} + {c}) - {d}"
            dists = [
                (str(a * b + c - d), "ignores_parentheses_grouping"),
                (str(a * (b + c + d)), "left_to_right_disregards_precedence"),
                (str(ans + d * 2), "addition_before_subtraction_dogma"),
            ]
            hint = "Always evaluate grouped expressions inside parentheses first."
            explanation = f"First parentheses: {b} + {c} = {b + c}. Then multiply: {a} * {b + c} = {a * (b + c)}. Finally subtract {d}: {ans}."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_ratios(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            factor = rng.choice([2, 3, 4, 5])
            a, b = rng.choice([(2, 3), (3, 4), (1, 3), (2, 5)])
            sa, sb = a * factor, b * factor
            ans_str = f"{a}:{b}"
            expr = f"ratio_simplify({sa}, {sb})"
            stem = f"In an art class, the ratio of blue brushes to red brushes is {sa} to {sb}. What is this ratio in simplest form?"
            dists = [
                (f"{a + 1}:{b + 1}", "additive_ratio_scaling"),
                (f"{b}:{a}", "inverts_ratio_terms_order"),
                (f"{a}:{a + b}", "part_to_part_vs_part_to_whole"),
            ]
            hint = f"Find the greatest common factor of {sa} and {sb} to simplify the ratio."
            explanation = f"Dividing both terms by {factor} gives {ans_str}."
        elif diff == Difficulty.MEDIUM:
            a, b = rng.choice([(3, 5), (4, 7), (2, 3), (5, 6)])
            factor = rng.choice([3, 4, 6])
            sa, sb = a * factor, b * factor
            ans_str = f"{a}:{b}"
            expr = f"ratio_simplify({sa}, {sb})"
            stem = f"A school choir has {sa} sopranos and {sb} altos. Which ratio shows the simplified relationship of sopranos to altos?"
            dists = [
                (f"{sa + 2}:{sb + 2}", "additive_ratio_scaling"),
                (f"{b}:{a}", "inverts_ratio_terms_order"),
                (f"{a}:{a + b}", "part_to_part_vs_part_to_whole"),
            ]
            hint = f"Divide both numbers by their common divisor {factor}."
            explanation = f"Both {sa} and {sb} divide by {factor}, resulting in the ratio {ans_str}."
        else: # HARD
            a, b = rng.choice([(5, 8), (7, 9), (6, 11), (4, 9)])
            factor = rng.choice([5, 7, 8])
            sa, sb = a * factor, b * factor
            ans_str = f"{a}:{b}"
            expr = f"ratio_simplify({sa}, {sb})"
            stem = f"A wildlife sanctuary tracks {sa} eagles and {sb} hawks. What is the simplified ratio of eagles to hawks?"
            dists = [
                (f"{a + 2}:{b + 2}", "additive_ratio_scaling"),
                (f"{b}:{a}", "inverts_ratio_terms_order"),
                (f"{a}:{a + b}", "part_to_part_vs_part_to_whole"),
            ]
            hint = f"Find the greatest common factor of {sa} and {sb}."
            explanation = f"Simplifying {sa}:{sb} gives {ans_str}."

        opts, c_idx = build_options_with_misconceptions(ans_str, dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_unit_rates(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            rate = rng.choice([12, 15, 20, 25])
            hours = rng.choice([2, 3, 4])
            total = rate * hours
            ans = rate
            expr = f"unit_rate({total}, {hours})"
            stem = f"Elena earned ${total} for babysitting for {hours} hours. What is her hourly pay rate in dollars per hour?"
            dists = [
                (str(total + hours), "divides_in_reversed_order"),
                (str(rate * 2), "forgets_unit_rate_denominator_is_one"),
                (str(rate - 4), "misinterprets_speed_units"),
            ]
            hint = f"Divide the total earnings (${total}) by the number of hours ({hours})."
            explanation = f"${total} / {hours} hours = ${ans} per hour."
        elif diff == Difficulty.MEDIUM:
            rate = rng.choice([45, 50, 55, 60, 65])
            hours = rng.choice([3, 4, 5])
            dist_val = rate * hours
            ans = rate
            expr = f"unit_rate({dist_val}, {hours})"
            stem = f"A train travels {dist_val} miles in {hours} hours at a constant speed. What is the train's speed in miles per hour?"
            dists = [
                (str(round(hours / dist_val, 2)), "divides_in_reversed_order"),
                (str(ans - 10), "misinterprets_speed_units"),
                (str(ans + 15), "forgets_unit_rate_denominator_is_one"),
            ]
            hint = "Unit rate of speed is total distance divided by total time."
            explanation = f"{dist_val} miles / {hours} hours = {ans} miles per hour."
        else: # HARD
            rate = rng.choice([16, 24, 32, 48])
            packs = rng.choice([4, 6, 8])
            total_items = rate * packs
            ans = rate
            expr = f"unit_rate({total_items}, {packs})"
            stem = f"A school supply store packages {total_items} colored markers across {packs} equal containers. How many markers are in each single container?"
            dists = [
                (str(round(packs / total_items, 2)), "divides_in_reversed_order"),
                (str(ans + 8), "forgets_unit_rate_denominator_is_one"),
                (str(ans - 6), "misinterprets_speed_units"),
            ]
            hint = f"Divide {total_items} markers by {packs} containers."
            explanation = f"{total_items} / {packs} = {ans} markers per container."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_percents(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            pct = rng.choice([10, 20, 25, 50])
            total = rng.choice([40, 60, 80, 100, 120])
            ans = int((pct / 100) * total)
            expr = f"percent_of({pct}, {total})"
            stem = f"In a survey of {total} fifth and sixth graders, {pct}% said math was their favorite quest. How many students chose math?"
            dists = [
                (str(pct * total), "multiplies_percent_directly_without_hundredth_conversion"),
                (str(int((pct / 10) * total)), "decimal_place_percent_shift"),
                (str(total - ans), "confuses_percent_of_vs_percent_change"),
            ]
            hint = f"Find {pct}% by writing it as a fraction ({pct}/100) and multiplying by {total}."
            explanation = f"{pct}% of {total} = ({pct}/100) * {total} = {ans} students."
        elif diff == Difficulty.MEDIUM:
            pct, total = rng.choice([(15, 60), (30, 80), (40, 120), (75, 40), (25, 80), (35, 60), (45, 80)])
            ans = int((pct * total) // 100)
            expr = f"percent_of({pct}, {total})"
            stem = f"A scout troop hiked {pct}% of a {total}-mile mountain loop trail. How many miles have they completed so far?"
            dists = [
                (str(int(ans * 10)), "decimal_place_percent_shift"),
                (str(pct * total), "multiplies_percent_directly_without_hundredth_conversion"),
                (str(total - ans), "confuses_percent_of_vs_percent_change"),
            ]
            hint = f"Multiply {total} by the decimal equivalent of {pct}% (which is {pct/100:.2f})."
            explanation = f"{pct/100:.2f} * {total} = {ans} miles."
        else: # HARD
            pct, total = rng.choice([(35, 140), (45, 160), (65, 180), (85, 240), (15, 140), (55, 120)])
            ans = int((pct * total) // 100)
            expr = f"percent_of({pct}, {total})"
            stem = f"A wildlife sanctuary houses {total} rescued birds. If {pct}% of them are birds of prey, how many birds of prey are in the sanctuary?"
            dists = [
                (str(int(ans * 10)), "decimal_place_percent_shift"),
                (str(total - ans), "confuses_percent_of_vs_percent_change"),
                (str(pct + total), "multiplies_percent_directly_without_hundredth_conversion"),
            ]
            hint = f"Convert {pct}% to {pct}/100 and multiply by {total}."
            explanation = f"({pct}/100) * {total} = {ans} birds of prey."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_fraction_division(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            n1, d1 = 3, 4
            n2, d2 = 1, 4
            ans_frac = Fraction(n1, d1) / Fraction(n2, d2)
            ans_str = str(ans_frac.numerator)
            expr = f"({n1}/{d1}) / ({n2}/{d2})"
            stem = f"How many {n2}/{d2}-pound bags of sunflower seeds can be filled from {n1}/{d1} pound of seeds?"
            dists = [
                (f"1/{ans_str}", "inverts_dividend_instead_of_divisor"),
                (f"{n1 * n2}/{d1 * d2}", "divides_numerators_and_denominators_directly"),
                (f"{d1 * d2}/{n1 * n2}", "inverts_both_fractions"),
            ]
            hint = f"Keep the first fraction, flip the second to {d2}/{n2}, and multiply."
            explanation = f"({n1}/{d1}) / ({n2}/{d2}) = ({n1}/{d1}) * ({d2}/{n2}) = {ans_str}."
        elif diff == Difficulty.MEDIUM:
            n1, d1 = rng.choice([(2, 3), (3, 5), (4, 5)])
            n2, d2 = rng.choice([(1, 2), (2, 3), (3, 4)])
            while Fraction(n1, d1) == Fraction(n2, d2):
                n2, d2 = (1, 3)
            ans_frac = Fraction(n1, d1) / Fraction(n2, d2)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"({n1}/{d1}) / ({n2}/{d2})"
            stem = f"Evaluate the fraction division: ({n1}/{d1}) / ({n2}/{d2})"
            inv_frac = Fraction(d1, n1) * Fraction(n2, d2)
            dists = [
                (f"{inv_frac.numerator}/{inv_frac.denominator}", "inverts_dividend_instead_of_divisor"),
                (f"{n1 * n2}/{d1 * d2}", "divides_numerators_and_denominators_directly"),
                (f"{d1 * n2}/{n1 * d2}", "inverts_both_fractions"),
            ]
            hint = "Multiply the first fraction by the reciprocal of the second fraction."
            explanation = f"({n1}/{d1}) * ({d2}/{n2}) = {ans_str}."
        else: # HARD
            n1, d1 = rng.choice([(5, 6), (7, 8), (4, 9)])
            n2, d2 = rng.choice([(2, 3), (3, 4), (5, 8)])
            while Fraction(n1, d1) == Fraction(n2, d2):
                n2, d2 = (1, 2)
            ans_frac = Fraction(n1, d1) / Fraction(n2, d2)
            ans_str = f"{ans_frac.numerator}/{ans_frac.denominator}"
            expr = f"({n1}/{d1}) / ({n2}/{d2})"
            stem = f"A recipe calls for {n1}/{d1} cup of cocoa powder. A measuring spoon holds {n2}/{d2} cup. How many scoops are required?"
            inv_frac = Fraction(d1, n1) * Fraction(n2, d2)
            dists = [
                (f"{inv_frac.numerator}/{inv_frac.denominator}", "inverts_dividend_instead_of_divisor"),
                (f"{n1 * n2}/{d1 * d2}", "divides_numerators_and_denominators_directly"),
                (f"{d1 * n2}/{n1 * d2}", "inverts_both_fractions"),
            ]
            hint = f"Multiply {n1}/{d1} by the reciprocal {d2}/{n2}."
            explanation = f"({n1}/{d1}) / ({n2}/{d2}) = {ans_str} scoops."

        opts, c_idx = build_options_with_misconceptions(ans_str, dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_decimals(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            a = round(rng.uniform(1.2, 4.8), 1)
            b = round(rng.uniform(0.2, 0.9), 1)
            ans = round(a * b, 2)
            expr = f"{a} * {b}"
            stem = f"A fabric ribbon costs ${a} per yard. How much does {b} yards of ribbon cost?"
            dists = [
                (str(round(ans * 10, 1)), "miscounts_decimal_places_in_product"),
                (str(round(ans / 10, 3)), "drops_zeros_before_decimal_place"),
                (str(round(a + b, 2)), "fails_to_shift_divisor_decimal"),
            ]
            hint = f"Multiply as whole numbers ({int(a*10)} * {int(b*10)}), then place the decimal point 2 places from the right."
            explanation = f"{a} * {b} = ${ans:.2f}."
        elif diff == Difficulty.MEDIUM:
            a = round(rng.uniform(12.5, 35.5), 1)
            b = rng.choice([0.5, 0.25, 0.2])
            ans = round(a / b, 1)
            expr = f"{a} / {b}"
            stem = f"A board of timber {a} feet long is sawed into equal planks that are each {b} feet long. How many planks are obtained?"
            dists = [
                (str(round(ans / 10, 2)), "fails_to_shift_divisor_decimal"),
                (str(round(a * b, 2)), "miscounts_decimal_places_in_product"),
                (str(round(ans + 5, 1)), "drops_zeros_before_decimal_place"),
            ]
            hint = f"Shift the decimal point in both {b} and {a} to make the divisor a whole number."
            explanation = f"{a} divided by {b} = {ans:.0f} planks."
        else: # HARD
            a = round(rng.uniform(3.25, 7.75), 2)
            b = round(rng.uniform(1.2, 3.4), 1)
            ans = round(a * b, 3)
            expr = f"{a} * {b}"
            stem = f"A chemist weighs {b} vials of reagent, each containing {a} grams. What is the combined mass in grams?"
            dists = [
                (str(round(ans * 10, 2)), "miscounts_decimal_places_in_product"),
                (str(round(ans / 10, 4)), "drops_zeros_before_decimal_place"),
                (str(round(a + b, 2)), "fails_to_shift_divisor_decimal"),
            ]
            hint = "Count total decimal places: 2 in the first number + 1 in the second = 3 decimal places in the product."
            explanation = f"{a} * {b} = {ans} grams."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_integers(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            a = -rng.randint(2, 9)
            b = rng.randint(1, 8)
            ans = "<"
            expr = f"compare({a}, {b})"
            stem = f"Which symbol makes this integer comparison true: {a} ___ {b}?"
            dists = [
                (">", "larger_magnitude_negative_is_greater"),
                ("=", "confuses_absolute_value_with_opposite"),
                ("none", "misplaces_negative_numbers_on_numberline"),
            ]
            hint = "Negative numbers are always to the left of positive numbers on a number line."
            explanation = f"Any negative integer is less than any positive integer, so {a} < {b}."
        elif diff == Difficulty.MEDIUM:
            n1 = rng.randint(2, 9)
            n2 = rng.randint(n1 + 1, n1 + 6)
            a = -n2 # smaller
            b = -n1 # larger
            ans = "<"
            expr = f"compare({a}, {b})"
            stem = f"Which comparison symbol correctly compares the two temperatures: {a}°F ___ {b}°F?"
            dists = [
                (">", "larger_magnitude_negative_is_greater"),
                ("=", "confuses_absolute_value_with_opposite"),
                ("none", "misplaces_negative_numbers_on_numberline"),
            ]
            hint = "On a vertical thermometer or number line, numbers further down are colder (lesser)."
            explanation = f"{a} is further to the left of zero than {b}, so {a} < {b}."
        else: # HARD
            n1 = rng.randint(3, 12)
            n2 = rng.randint(1, n1 - 1)
            a = -n2 # larger
            b = -n1 # smaller
            ans = ">"
            expr = f"compare({a}, {b})"
            stem = f"A submarine dives from depth {a} meters to {b} meters. Which symbol accurately shows {a} ___ {b}?"
            dists = [
                ("<", "larger_magnitude_negative_is_greater"),
                ("=", "confuses_absolute_value_with_opposite"),
                ("none", "misplaces_negative_numbers_on_numberline"),
            ]
            hint = f"Because {n2} is closer to 0 than {n1}, -{n2} is greater than -{n1}."
            explanation = f"-{n2} is greater than -{n1}, so the correct symbol is '{ans}'."

        opts, c_idx = build_options_with_misconceptions(ans, dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_equiv_expressions(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            factor = rng.choice([2, 3, 4, 5])
            c = rng.choice([3, 4, 6])
            expr_orig = f"{factor} * (x + {c})"
            expr_equiv = f"{factor} * x + {factor * c}"
            expr = f"check_equiv('{expr_orig}', '{expr_equiv}')"
            stem = f"Are the expressions {factor}(x + {c}) and {factor}x + {factor * c} equivalent for all values of x?"
            dists = [
                ("not equivalent", "incomplete_distribution"),
                ("equal only when x=0", "combines_unlike_terms"),
                ("cannot be determined", "sign_error_distributing_negative"),
            ]
            hint = f"Use the distributive property: multiply {factor} by both terms inside parentheses."
            explanation = f"Distributing {factor} across (x + {c}) gives {factor}x + {factor * c}, so they are equivalent."
        elif diff == Difficulty.MEDIUM:
            a = rng.choice([3, 4, 5])
            b = rng.choice([2, 3, 4])
            const = rng.choice([6, 8, 10])
            expr_orig = f"{a} * x + {b} * x + {const}"
            expr_equiv = f"{a + b} * x + {const}"
            expr = f"check_equiv('{expr_orig}', '{expr_equiv}')"
            stem = f"Are the expressions ({a}x + {b}x + {const}) and ({a + b}x + {const}) equivalent?"
            dists = [
                ("not equivalent", "combines_unlike_terms"),
                ("equal only when x=1", "incomplete_distribution"),
                ("cannot be determined", "sign_error_distributing_negative"),
            ]
            hint = f"Combine the like terms {a}x and {b}x."
            explanation = f"{a}x + {b}x combines to {a + b}x, so the expressions are equivalent."
        else: # HARD
            c = rng.choice([2, 3])
            m = rng.choice([4, 5])
            k = rng.choice([2, 3])
            expr_orig = f"{c} * ({m} * x + {k})"
            expr_equiv = f"{c * m} * x + {c * k}"
            expr = f"check_equiv('{expr_orig}', '{expr_equiv}')"
            stem = f"Apply the distributive property: Are {c}({m}x + {k}) and {c * m}x + {c * k} equivalent?"
            dists = [
                ("not equivalent", "incomplete_distribution"),
                ("equal only when x=0", "combines_unlike_terms"),
                ("cannot be determined", "sign_error_distributing_negative"),
            ]
            hint = f"Multiply the outside factor {c} by both {m}x and {k}."
            explanation = f"{c} * {m}x = {c * m}x and {c} * {k} = {c * k}, making them equivalent."

        opts, c_idx = build_options_with_misconceptions("equivalent", dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_equations(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            const = rng.choice([5, 7, 9, 12])
            ans = rng.choice([8, 11, 14, 15])
            total = ans + const
            expr = f"solve_linear('x + {const} = {total}')"
            stem = f"Solve the one-step addition equation for x: x + {const} = {total}"
            dists = [
                (str(total + const), "performs_same_operation_instead_of_inverse"),
                (str(total), "operates_on_one_side_only"),
                (str(abs(total - const * 2)), "multiplies_instead_of_dividing_coefficients"),
            ]
            hint = f"Subtract {const} from both sides to isolate the variable x."
            explanation = f"Subtracting {const} from {total} gives x = {ans}."
        elif diff == Difficulty.MEDIUM:
            coeff = rng.choice([3, 4, 5, 6])
            ans = rng.choice([6, 7, 8, 9])
            total = coeff * ans
            expr = f"solve_linear('{coeff}x = {total}')"
            stem = f"Find the value of x that solves the equation: {coeff}x = {total}"
            dists = [
                (str(total * coeff), "multiplies_instead_of_dividing_coefficients"),
                (str(total - coeff), "performs_same_operation_instead_of_inverse"),
                (str(total), "operates_on_one_side_only"),
            ]
            hint = f"Divide both sides by the coefficient {coeff}."
            explanation = f"Dividing {total} by {coeff} yields x = {ans}."
        else: # HARD
            const = rng.choice([14, 18, 25, 32])
            ans = rng.choice([16, 24, 35, 42])
            total = ans - const
            expr = f"solve_linear('x - {const} = {total}')"
            stem = f"A storage chest has x coins. After removing {const} coins for supplies, {total} coins remain. Solve x - {const} = {total}:"
            dists = [
                (str(total - const), "performs_same_operation_instead_of_inverse"),
                (str(total), "operates_on_one_side_only"),
                (str(ans + 10), "multiplies_instead_of_dividing_coefficients"),
            ]
            hint = f"Add {const} to both sides to find the original amount."
            explanation = f"x = {total} + {const} = {ans}."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_mean_median(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            # Mean of 4 simple values with exact integer mean
            mean_val = rng.choice([10, 12, 15, 20])
            d1 = rng.choice([2, 4])
            nums = [mean_val - d1, mean_val - 1, mean_val + 1, mean_val + d1]
            rng.shuffle(nums)
            nums_str = ", ".join(map(str, nums))
            ans = mean_val
            expr = f"mean({nums_str})"
            stem = f"Four students earned scores of {nums_str} points in a ring-toss game. What is the mean score?"
            dists = [
                (str(sum(nums)), "divides_sum_by_arbitrary_number"),
                (str(sorted(nums)[1]), "finds_median_without_ordering_data"),
                (str(mean_val + 2), "confuses_mean_with_median"),
            ]
            hint = f"Add all 4 scores together, then divide the total sum by 4."
            explanation = f"Sum = {sum(nums)}. Dividing by 4 gives a mean score of {ans}."
        elif diff == Difficulty.MEDIUM:
            # Median of 5 values (odd count)
            sorted_nums = sorted([rng.randint(5, 35) for _ in range(5)])
            while len(set(sorted_nums)) < 4:
                sorted_nums = sorted([rng.randint(5, 35) for _ in range(5)])
            med_val = sorted_nums[2]
            shuffled = list(sorted_nums)
            rng.shuffle(shuffled)
            nums_str = ", ".join(map(str, shuffled))
            ans = med_val
            expr = f"median({nums_str})"
            stem = f"Find the median of the following five recorded trail distances: {nums_str}"
            dists = [
                (str(shuffled[2] if shuffled[2] != med_val else shuffled[0]), "finds_median_without_ordering_data"),
                (str(round(sum(sorted_nums) / 5)), "confuses_mean_with_median"),
                (str(sorted_nums[1]), "divides_sum_by_arbitrary_number"),
            ]
            hint = "Arrange the 5 numbers in order from least to greatest and select the middle number."
            explanation = f"Ordered values: {', '.join(map(str, sorted_nums))}. The middle value is {ans}."
        else: # HARD
            # Mean of 5 values summing to a multiple of 5
            target_mean = rng.choice([25, 30, 40, 50])
            offset1 = rng.choice([6, 8, 10])
            offset2 = rng.choice([2, 4])
            nums = [target_mean - offset1, target_mean - offset2, target_mean, target_mean + offset2, target_mean + offset1]
            rng.shuffle(nums)
            nums_str = ", ".join(map(str, nums))
            ans = target_mean
            expr = f"mean({nums_str})"
            stem = f"During a science project, seedlings grew {nums_str} millimeters. What is the mean growth in millimeters?"
            dists = [
                (str(sum(nums)), "divides_sum_by_arbitrary_number"),
                (str(sorted(nums)[1]), "finds_median_without_ordering_data"),
                (str(target_mean + 5), "confuses_mean_with_median"),
            ]
            hint = "Find the sum of all 5 numbers and divide by 5."
            explanation = f"Total growth = {sum(nums)} mm. Dividing by 5 yields a mean of {ans} mm."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


def gen_g6_exponents(topic: Dict[str, Any], diff: Difficulty, count: int, rng: random.Random) -> List[Question]:
    questions = []
    for i in range(count):
        if diff == Difficulty.EASY:
            base = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10])
            exp_val = 2
            ans = base ** exp_val
            expr = f"{base} ** {exp_val}"
            stem = f"Evaluate the exponential expression: {base}²"
            dists = [
                (str(base * exp_val), "multiplies_base_by_exponent"),
                (str(base + exp_val), "evaluates_exponent_zero_as_zero"),
                (str(exp_val ** base if base <= 4 else ans + 4), "confuses_exponent_order"),
            ]
            hint = f"{base}² means {base} multiplied by itself ({base} * {base})."
            explanation = f"{base}² = {base} * {base} = {ans}."
        elif diff == Difficulty.MEDIUM:
            base = rng.choice([2, 3, 4, 5])
            exp_val = 3
            ans = base ** exp_val
            expr = f"{base} ** {exp_val}"
            stem = f"What is the value of {base}³?"
            dists = [
                (str(base * exp_val), "multiplies_base_by_exponent"),
                (str(exp_val ** base if exp_val ** base != ans else ans + 6), "confuses_exponent_order"),
                (str(base * 2), "evaluates_exponent_zero_as_zero"),
            ]
            hint = f"Multiply the base {base} by itself 3 times ({base} * {base} * {base})."
            explanation = f"{base}³ = {base} * {base} * {base} = {ans}."
        else: # HARD
            base = rng.choice([2, 3])
            exp_val = rng.choice([4, 5])
            ans = base ** exp_val
            expr = f"{base} ** {exp_val}"
            stem = f"Evaluate the power: {base}^{exp_val}"
            dists = [
                (str(base * exp_val), "multiplies_base_by_exponent"),
                (str(exp_val ** base if exp_val ** base != ans else ans + 8), "confuses_exponent_order"),
                (str(base ** (exp_val - 1)), "evaluates_exponent_zero_as_zero"),
            ]
            hint = f"Compute {base} multiplied by itself {exp_val} times."
            explanation = f"{base}^{exp_val} = {ans}."

        opts, c_idx = build_options_with_misconceptions(str(ans), dists, rng)
        questions.append(create_question_entry(topic, diff, stem, expr, opts, c_idx, explanation, hint, f"{topic['id']}-{diff.value}-{i+1}"))
    return questions


# Dispatcher map
GENERATOR_MAP = {
    "g5-place-value": gen_g5_place_value,
    "g5-decimal-ops": gen_g5_decimal_ops,
    "g5-decimal-compare-round": gen_g5_decimal_compare_round,
    "g5-fractions-add": gen_g5_fractions_add,
    "g5-fractions-multiply": gen_g5_fractions_multiply,
    "g5-fractions-divide-unit": gen_g5_fractions_divide_unit,
    "g5-volume": gen_g5_volume,
    "g5-multiply": gen_g5_multiply,
    "g5-divide": gen_g5_divide,
    "g5-order-ops": gen_g5_order_ops,
    "g6-ratios": gen_g6_ratios,
    "g6-unit-rates": gen_g6_unit_rates,
    "g6-percents": gen_g6_percents,
    "g6-fraction-division": gen_g6_fraction_division,
    "g6-decimals": gen_g6_decimals,
    "g6-integers": gen_g6_integers,
    "g6-equiv-expressions": gen_g6_equiv_expressions,
    "g6-equations": gen_g6_equations,
    "g6-mean-median": gen_g6_mean_median,
    "g6-exponents": gen_g6_exponents,
}


def seed_all_topics(seed: int = 42, count_per_level: int = 6) -> Dict[str, BankFile]:
    rng = random.Random(seed)
    with open("data/topics.json", "r", encoding="utf-8") as f:
        topics = json.load(f)

    os.makedirs("data/bank", exist_ok=True)
    banks: Dict[str, BankFile] = {}

    for t in topics:
        tid = t["id"]
        generator_func = GENERATOR_MAP.get(tid)
        if not generator_func:
            raise KeyError(f"Missing generator function for topic {tid}")

        all_questions: List[Question] = []
        for diff in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
            qs = generator_func(t, diff, count_per_level, rng)
            all_questions.extend(qs)

        bank = BankFile(
            topic_id=tid,
            version="1.0.0",
            questions=all_questions,
        )

        # Output bank file with metadata
        bank_data = {
            "topic_id": tid,
            "version": bank.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": "template-seed",
            "prompt_version": "seed-v1",
            "counts_per_level": {
                "easy": count_per_level,
                "medium": count_per_level,
                "hard": count_per_level,
                "total": len(all_questions),
            },
            "questions": [q.model_dump() for q in all_questions],
        }

        out_path = os.path.join("data/bank", f"{tid}.json")
        with open(out_path, "w", encoding="utf-8") as out_f:
            json.dump(bank_data, out_f, indent=2)

        banks[tid] = bank

    return banks


if __name__ == "__main__":
    print("Seeding question banks for all 20 Georgia Math Standards topics...")
    banks = seed_all_topics(seed=42, count_per_level=6)
    total_q = sum(len(b.questions) for b in banks.values())
    print(f"Successfully generated {total_q} verified questions across {len(banks)} topics (18 questions per topic).")
