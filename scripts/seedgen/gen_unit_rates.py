"""Generator for g6-unit-rates."""
import random
from fractions import Fraction
from . import get_topic_positions, build_options, get_distractors, fmt_num, fmt_frac

TOPIC = "g6-unit-rates"

STEMS = {
    "easy": [
        ("food",   "A baker makes {a} cookies in {b} batches. How many cookies per batch?"),
        ("sports", "A swimmer covers {a} metres in {b} minutes. What is the speed in metres per minute?"),
        ("school", "A student reads {a} pages in {b} hours. How many pages per hour?"),
        ("games",  "A player earns {a} gold in {b} quests. How much gold per quest?"),
        ("nature", "A bird flies {a} miles in {b} hours. What is the speed in miles per hour?"),
    ],
    "medium": [
        ("food",   "A farm produces {a} kilograms of apples over {b} weeks. What is the weekly rate?"),
        ("sports", "An athlete runs {a} laps in {b} practice sessions. How many laps per session?"),
        ("school", "A printer prints {a} pages in {b} minutes. How many pages per minute?"),
        ("games",  "A team completes {a} levels in {b} days. How many levels per day?"),
        ("nature", "A river flows {a} gallons past a point in {b} seconds. What is the flow rate per second?"),
    ],
    "hard": [
        ("food",   "A factory packages {a} bottles in {b} hours. What is the rate per hour?"),
        ("sports", "A cyclist rides {a} kilometres in {b} hours. What is the speed in km per hour?"),
        ("school", "A class completes {a} math problems across {b} study sessions. How many problems per session?"),
        ("games",  "A guild earns {a} experience points in {b} raids. What is the rate per raid?"),
        ("nature", "A weather station records {a} millimetres of rain over {b} days. What is the daily rainfall?"),
    ],
}

ALL_RULES = [
    "divides_in_reversed_order",
    "multiplied_instead_of_dividing",
    "forgets_unit_rate_denominator_is_one",
    "subtracts_quantities",
    "adds_quantities",
]

def _params(rng, diff):
    if diff == "easy":
        as_ = [24, 36, 48, 60, 72]
        bs = [2, 3, 4, 6]
    elif diff == "medium":
        as_ = [72, 96, 120, 150, 180]
        bs = [3, 4, 5, 6, 8]
    else:
        as_ = [144, 180, 240, 300, 360]
        bs = [4, 5, 6, 8, 9, 12]
    for _ in range(100):
        a = rng.choice(as_)
        b = rng.choice(bs)
        if a % b == 0 and a != b and b > 1:
            correct = a // b
            # Ensure multiplies_instead_of_dividing produces different result
            if a * b != correct:
                return {"a": a, "b": b}
    return {"a": 180, "b": 3}

def _explanation(p, correct):
    a, b = p["a"], p["b"]
    return (f"To find the unit rate, divide the total by the number of groups. "
            f"{a} ÷ {b} = {correct}.")

def _hint(diff):
    if diff == "easy":
        return "Divide the total amount by how many groups there are."
    elif diff == "medium":
        return "What single number tells you the amount for just one group?"
    else:
        return "Find how much happens in exactly 1 unit by dividing the total."

def generate(seed: int = 42):
    rng = random.Random(seed)
    pos_map = get_topic_positions(TOPIC, seed)
    questions = []
    global_q_idx = 0
    for diff in ("easy", "medium", "hard"):
        stem_list = list(STEMS[diff])
        rng.shuffle(stem_list)
        used = []
        attempts = 0
        while len(used) < 6 and attempts < 300:
            attempts += 1
            p = _params(rng, diff)
            a, b = p["a"], p["b"]
            correct_val = a // b
            correct_text = fmt_num(correct_val)

            offset = global_q_idx % len(ALL_RULES)
            rule_order = ALL_RULES[offset:] + ALL_RULES[:offset]

            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            ctx, tmpl = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
            stem_text = tmpl.format(**p)
            correct_pos = pos_map[diff][len(used)]
            options = build_options(correct_text, distractors, correct_pos)

            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "6.NR.4.4",
                "difficulty": diff,
                "verifier_type": "rate_division",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": f"{a} / {b}",
                "options": options,
                "correct_index": correct_pos,
                "answer": correct_text,
                "hint": _hint(diff),
                "explanation": _explanation(p, correct_text),
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
            global_q_idx += 1
        questions.extend(used)
    return questions
