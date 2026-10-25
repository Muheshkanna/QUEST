"""Generator for g5-fractions-multiply."""
import random
from fractions import Fraction
from . import get_topic_positions, build_options, get_distractors, fmt_frac

TOPIC = "g5-fractions-multiply"

STEMS = {
    "easy": [
        ("food",   "A recipe calls for {a}/{b} cup of flour. You are making {w} batches. How much flour in total?"),
        ("sports", "Each practice lap takes {a}/{b} of a mile. After {w} laps, how far did you run?"),
        ("school", "A student spends {a}/{b} of an hour on homework. Over {w} days, how many hours total?"),
        ("games",  "A potion needs {a}/{b} of a crystal per brew. Making {w} potions uses how many crystals?"),
        ("nature", "A garden row needs {a}/{b} of a bag of seeds. Planting {w} rows takes how many bags?"),
    ],
    "medium": [
        ("food",   "What is {a}/{b} × {c}/{d}?"),
        ("sports", "A runner covers {a}/{b} of a track in each sprint. After {c}/{d} of a full set, how much track?"),
        ("school", "A paint set uses {a}/{b} of a tube per project. Over {c}/{d} of a week, how many tubes?"),
        ("games",  "A spell uses {a}/{b} mana. At {c}/{d} power, how much mana is used?"),
        ("nature", "A tree grows {a}/{b} of a foot per month. Over {c}/{d} of a year, how much growth?"),
    ],
    "hard": [
        ("food",   "A farmer harvests {a}/{b} of a field per day. After {c}/{d} of a week, how much is harvested?"),
        ("sports", "An athlete lifts {a}/{b} of their max weight. At {c}/{d} effort, what fraction of max?"),
        ("school", "A textbook chapter is {a}/{b} of the book. Reading {c}/{d} of the chapter means what fraction of the whole book?"),
        ("games",  "A treasure chest holds {a}/{b} of the dungeon's gold. Taking {c}/{d} of the chest gives what fraction of total gold?"),
        ("nature", "A lake fills {a}/{b} of a reservoir. Draining {c}/{d} of the lake leaves what fraction of the reservoir?"),
    ],
}

ALL_RULES = [
    "added_fractions_instead",
    "cross_multiplies_instead_of_multiplying_straight",
    "multiplies_tops_adds_bottoms",
    "added_tops_multiplied_bottoms",
    "multiplies_both_by_whole_number",
]

def _params(rng, diff):
    """Generate fraction multiplication params.
    Easy: whole_number * fraction (w * a/b).
    Medium/Hard: fraction * fraction (a/b * c/d).
    """
    if diff == "easy":
        fracs = [(1, 3), (1, 4), (2, 5), (1, 6), (3, 4), (2, 3), (1, 5)]
        ws = [2, 3, 4, 5]
        for _ in range(100):
            a, b = rng.choice(fracs)
            w = rng.choice(ws)
            # For whole number: params are a, b, w (meaning w * a/b)
            # correct = w*a / b
            p = {"a": a, "b": b, "w": w, "c": w, "d": 1}
            return p
        return {"a": 1, "b": 3, "w": 3, "c": 3, "d": 1}
    else:
        if diff == "medium":
            fracs = [(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (1, 5), (2, 5)]
        else:
            fracs = [(2, 3), (3, 4), (3, 5), (4, 5), (2, 7), (5, 6), (3, 8)]
        for _ in range(100):
            a, b = rng.choice(fracs)
            c, d = rng.choice(fracs)
            # Ensure cross-multiply gives different result
            if (a * d != a * c) or (b * c != b * d):
                if (b + d) != (b * d):  # multiplies_tops_adds_bottoms differs
                    if (a + c) != (a * c):  # added_tops_multiplied_bottoms differs
                        return {"a": a, "b": b, "c": c, "d": d}
        return {"a": 2, "b": 3, "c": 1, "d": 4}

def _explanation(p, correct):
    if "w" in p and p.get("d", 1) == 1:
        w, a, b = p["w"], p["a"], p["b"]
        return (f"Multiply the whole number by the top of the fraction: "
                f"{w} × {a} = {w*a}. Keep the bottom the same: {b}. "
                f"The answer is {correct}.")
    else:
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]
        return (f"Multiply top × top: {a} × {c} = {a*c}. "
                f"Multiply bottom × bottom: {b} × {d} = {b*d}. "
                f"The answer is {correct}.")

def _hint(diff):
    if diff == "easy":
        return "Multiply the whole number by the top of the fraction. The bottom stays the same."
    elif diff == "medium":
        return "How do you combine the tops? How do you combine the bottoms?"
    else:
        return "Multiply straight across: top times top, bottom times bottom, then simplify."

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
            c = p.get("c", p.get("w", 1))
            d = p.get("d", 1)
            correct = Fraction(a * c, b * d)
            correct_text = fmt_frac(correct)

            offset = global_q_idx % len(ALL_RULES)
            rule_order = ALL_RULES[offset:] + ALL_RULES[:offset]

            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            ctx, tmpl = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
            if diff == "easy":
                stem_text = tmpl.format(a=a, b=b, w=p["w"])
                expr = f"({p['w']} * {a}) / {b}"
            else:
                stem_text = tmpl.format(a=a, b=b, c=c, d=d)
                expr = f"({a} / {b}) * ({c} / {d})"
            correct_pos = pos_map[diff][len(used)]
            options = build_options(correct_text, distractors, correct_pos)

            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "5.NR.3.4",
                "difficulty": diff,
                "verifier_type": "fraction_arithmetic",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": expr,
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
