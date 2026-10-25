"""Generator for g6-equations.
easy   = a*x = b  (form ax_b)
medium = x + a = b  (form xpa_b)
hard   = a*x + b = c  (form axpb_c)
"""
import random
from fractions import Fraction
from . import get_topic_positions, build_options, get_distractors, fmt_frac, fmt_num

TOPIC = "g6-equations"

STEMS = {
    "easy": [
        ("food",   "{a} equally-sized boxes of cereal weigh {b} ounces in total. Write and solve: {a}x = {b}. How much does one box weigh?"),
        ("sports", "A team scored {b} points total, with each player scoring {a} points. Write {a}x = {b}. How many players scored?"),
        ("school", "There are {b} pencils shared equally among {a} students. Write {a}x = {b}. How many pencils does each student get?"),
        ("games",  "Each level in a game gives {a} coins, and you have {b} coins. Write {a}x = {b}. How many levels have you completed?"),
        ("nature", "{a} identical pots hold {b} litres of water total. Write {a}x = {b}. How much water is in each pot?"),
    ],
    "medium": [
        ("food",   "After baking {a} muffins, a bakery now has {b} muffins in total. Write x + {a} = {b}. How many muffins were there at first?"),
        ("sports", "A runner has logged {b} miles this season, including {a} miles this week. Write x + {a} = {b}. How many miles did they run before this week?"),
        ("school", "A classroom library has {b} books after adding {a} new books. Write x + {a} = {b}. How many books were in the library originally?"),
        ("games",  "A player earned {a} extra coins from a bonus and now has {b} total. Write x + {a} = {b}. How many coins did they have before the bonus?"),
        ("nature", "A wildlife rescue cared for {a} new birds and now has {b} birds. Write x + {a} = {b}. How many birds were there before?"),
    ],
    "hard": [
        ("food",   "A recipe uses {a} cups of sugar per batch, plus {b} extra cups for frosting, totaling {c} cups. Write {a}x + {b} = {c}. How many batches were made?"),
        ("sports", "A team scores {a} points per game and earned {b} bonus points, reaching {c} total. Write {a}x + {b} = {c}. How many games did they play?"),
        ("school", "A printer prints {a} pages per minute. After an initial test of {b} pages it printed {c} pages total. Write {a}x + {b} = {c}. How many minutes did the main job take?"),
        ("games",  "A hero earns {a} gold per dungeon and starts with {b} gold. They now have {c} gold. Write {a}x + {b} = {c}. How many dungeons did they complete?"),
        ("nature", "Each bucket holds {a} litres of rain water. After {b} extra litres trickled in, there are {c} litres. Write {a}x + {b} = {c}. How many buckets filled up?"),
    ],
}

EASY_RULES = [
    "ignored_the_coefficient",
    "divided_the_wrong_way",
    "subtracted_instead_of_dividing",
    "multiplied_instead_of_dividing",
]
MEDIUM_RULES = [
    "ignored_the_added_value",
    "used_added_value_as_answer",
    "added_instead_of_subtracting",
    "subtracted_the_wrong_way",
]
HARD_RULES = [
    "undid_multiplication_first",
    "added_the_constant",
    "ignored_the_constant_term",
]

def _easy_params(rng):
    for _ in range(100):
        a = rng.randint(2, 12)
        b = a * rng.randint(2, 12)
        ans = b // a
        if Fraction(a, b) != Fraction(b, a) and ans > 1 and b != ans:
            return {"form": "ax_b", "a": a, "b": b}
    return {"form": "ax_b", "a": 6, "b": 54}

def _medium_params(rng):
    for _ in range(100):
        a = rng.randint(10, 40)
        b = rng.randint(a + 5, 80)
        ans = b - a
        if ans > 0 and a != b and a != ans:
            return {"form": "xpa_b", "a": a, "b": b}
    return {"form": "xpa_b", "a": 15, "b": 47}

def _hard_params(rng):
    for _ in range(100):
        a = rng.randint(2, 8)
        x_ans = rng.randint(2, 10)
        b = rng.randint(1, 15)
        c = a * x_ans + b
        correct = Fraction(c - b, a)
        d1 = Fraction(c, a) - b
        d2 = Fraction(c + b, a)
        d3 = Fraction(c, a)
        if len({str(correct), str(d1), str(d2), str(d3)}) == 4:
            return {"form": "axpb_c", "a": a, "b": b, "c": c}
    return {"form": "axpb_c", "a": 2, "b": 3, "c": 11}

def _correct_text(p):
    f = p["form"]
    if f == "ax_b":
        return fmt_frac(Fraction(p["b"], p["a"]))
    elif f == "xpa_b":
        return fmt_num(p["b"] - p["a"])
    else:
        return fmt_frac(Fraction(p["c"] - p["b"], p["a"]))

def _expr(p):
    f = p["form"]
    if f == "ax_b": return f"solve_linear('{p['a']}x = {p['b']}')"
    elif f == "xpa_b": return f"solve_linear('x + {p['a']} = {p['b']}')"
    else: return f"solve_linear('{p['a']}x + {p['b']} = {p['c']}')"

def _explanation(p):
    f = p["form"]
    if f == "ax_b":
        ans = fmt_frac(Fraction(p["b"], p["a"]))
        return (f"To find x, divide both sides by {p['a']}. "
                f"{p['b']} ÷ {p['a']} = {ans}. "
                f"Check: {p['a']} × {ans} = {p['b']}. ✓")
    elif f == "xpa_b":
        ans = p["b"] - p["a"]
        return (f"Subtract {p['a']} from both sides to isolate x. "
                f"{p['b']} − {p['a']} = {ans}. "
                f"Check: {ans} + {p['a']} = {p['b']}. ✓")
    else:
        ans = fmt_frac(Fraction(p["c"] - p["b"], p["a"]))
        mid = p["c"] - p["b"]
        return (f"Subtract {p['b']} from both sides first: {p['c']} − {p['b']} = {mid}. "
                f"Then divide by {p['a']}: {mid} ÷ {p['a']} = {ans}. ✓")

def _hint(p, diff):
    f = p["form"]
    if diff == "easy":
        return f"What is the opposite operation of multiplying by {p['a']}? Do that to both sides."
    elif diff == "medium":
        return f"How can you isolate x by undoing the addition of {p['a']}?"
    else:
        return "Work in reverse order: remove the number added on the outside first, then divide by the multiplier."

def generate(seed: int = 42):
    rng = random.Random(seed)
    pos_map = get_topic_positions(TOPIC, seed)
    questions = []
    param_fns = {"easy": _easy_params, "medium": _medium_params, "hard": _hard_params}
    rule_sets = {"easy": EASY_RULES, "medium": MEDIUM_RULES, "hard": HARD_RULES}

    for diff in ("easy", "medium", "hard"):
        stem_list = list(STEMS[diff])
        rng.shuffle(stem_list)
        pool_rules = rule_sets[diff]
        used = []
        attempts = 0
        while len(used) < 6 and attempts < 300:
            attempts += 1
            p = param_fns[diff](rng)
            correct_text = _correct_text(p)

            # Rotate rule order per question
            rot_idx = len(used) % len(pool_rules)
            rule_order = pool_rules[rot_idx:] + pool_rules[:rot_idx]

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
                "standard": "6.PAR.7.2",
                "difficulty": diff,
                "verifier_type": "equation_solving",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": _expr(p),
                "options": options,
                "correct_index": correct_pos,
                "answer": correct_text,
                "hint": _hint(p, diff),
                "explanation": _explanation(p),
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
        questions.extend(used)
    return questions
