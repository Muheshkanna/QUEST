"""Generator for g6-fraction-division.
a/b / c/d with a/b != c/d.
easy = divide by a unit fraction (c/d = 1/k)
medium = both fractions proper
hard = word problems with larger fractions
"""
import random
from fractions import Fraction
from . import get_topic_positions, build_options, get_distractors, fmt_frac

TOPIC = "g6-fraction-division"

STEMS = {
    "easy": [
        ("food",   "A baker has {a}/{b} of a kilogram of icing. Each cupcake requires {c}/{d} of a kilogram. How many cupcakes can be frosted?"),
        ("sports", "A runner has {a}/{b} of an energy bar. Each bite is {c}/{d} of a bar. How many bites can the runner take?"),
        ("school", "A teacher has {a}/{b} of a poster board. Each student badge requires {c}/{d} of a board. How many badges can be made?"),
        ("games",  "A wizard holds {a}/{b} of a mana crystal. Each spell cast consumes {c}/{d} of a crystal. How many spells can be cast?"),
        ("nature", "A garden path covers {a}/{b} of a lawn. Stepping stones each cover {c}/{d} of the lawn. How many stepping stones fit along the path?"),
    ],
    "medium": [
        ("food",   "A soup recipe requires {c}/{d} of a cup of broth per bowl. If a pot holds {a}/{b} of a cup, how many bowls can be served?"),
        ("sports", "A practice lap is {c}/{d} of a mile. An athlete completed {a}/{b} of a mile. How many practice laps is that?"),
        ("school", "An art project uses {c}/{d} of a bottle of glue per craft. A student has {a}/{b} of a bottle. How many crafts can be made?"),
        ("games",  "A blacksmith needs {c}/{d} of an ingot to forge an arrow. The forge has {a}/{b} of an ingot. How many arrows can be forged?"),
        ("nature", "A bird feeder holds {a}/{b} of a pound of seed. Each feeding scoop is {c}/{d} of a pound. How many scoops can be poured?"),
    ],
    "hard": [
        ("food",   "A pastry chef has {a}/{b} of a block of butter. A delicate pastry batch takes {c}/{d} of a block. How many batches can be baked?"),
        ("sports", "A sprint interval is {c}/{d} of a stadium circuit. A training session covered {a}/{b} of a circuit. How many intervals were completed?"),
        ("school", "A science lab has {a}/{b} of a litre of reagent. Each test tube requires {c}/{d} of a litre. How many test tubes can be prepared?"),
        ("games",  "A portal gate consumes {c}/{d} of a power cell per transit. The terminal retains {a}/{b} of a power cell. How many transits can occur?"),
        ("nature", "A park trail spans {a}/{b} of a mountain pass. Distance markers are placed every {c}/{d} of a pass. How many intervals fit along the trail?"),
    ],
}

ALL_RULES = [
    "multiplied_without_flipping",
    "flipped_the_first_fraction",
    "flipped_both_fractions",
    "added_instead_of_dividing",
]

def _params(rng, diff):
    if diff == "easy":
        # divide by unit fraction
        as_ = [(1, 2), (2, 3), (3, 4), (3, 5), (4, 5), (5, 6)]
        cs_ = [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6)]
        for _ in range(200):
            a, b = rng.choice(as_)
            c, d = rng.choice(cs_)
            if Fraction(a, b) == Fraction(c, d):
                continue
            corr = Fraction(a * d, b * c)
            r1 = Fraction(a * c, b * d)
            r2 = Fraction(b * c, a * d)
            r3 = Fraction(b * d, a * c)
            r4 = Fraction(a, b) + Fraction(c, d)
            if len({corr, r1, r2, r3, r4}) == 5:
                return {"a": a, "b": b, "c": c, "d": d}
        return {"a": 2, "b": 3, "c": 1, "d": 4}

    elif diff == "medium":
        # both fractions proper, non-unit
        fracs = [(2, 3), (3, 4), (2, 5), (3, 5), (4, 5), (1, 3), (1, 4)]
        for _ in range(300):
            a, b = rng.choice(fracs)
            c, d = rng.choice(fracs)
            if Fraction(a, b) == Fraction(c, d):
                continue
            corr = Fraction(a * d, b * c)
            r1 = Fraction(a * c, b * d)
            r2 = Fraction(b * c, a * d)
            r3 = Fraction(b * d, a * c)
            r4 = Fraction(a, b) + Fraction(c, d)
            if len({corr, r1, r2, r3, r4}) == 5:
                return {"a": a, "b": b, "c": c, "d": d}
        return {"a": 3, "b": 4, "c": 2, "d": 5}

    else:
        # larger proper fractions
        fracs = [(3, 4), (3, 5), (4, 5), (5, 6), (3, 8), (5, 8), (2, 7), (4, 7)]
        for _ in range(300):
            a, b = rng.choice(fracs)
            c, d = rng.choice(fracs)
            if Fraction(a, b) == Fraction(c, d):
                continue
            corr = Fraction(a * d, b * c)
            r1 = Fraction(a * c, b * d)
            r2 = Fraction(b * c, a * d)
            r3 = Fraction(b * d, a * c)
            r4 = Fraction(a, b) + Fraction(c, d)
            if len({corr, r1, r2, r3, r4}) == 5:
                return {"a": a, "b": b, "c": c, "d": d}
        return {"a": 4, "b": 5, "c": 3, "d": 8}

def _explanation(p, correct):
    a, b, c, d = p["a"], p["b"], p["c"], p["d"]
    recip = f"{d}/{c}" if c != 1 else str(d)
    return (f"To divide by a fraction, multiply by its reciprocal: flip the second fraction. "
            f"{a}/{b} ÷ {c}/{d} = {a}/{b} × {recip} = {correct}.")

def _hint(diff):
    if diff == "easy":
        return "Keep the first fraction, change division to multiplication, and flip the second fraction."
    elif diff == "medium":
        return "To divide by a fraction, multiply by its reciprocal: invert the second fraction."
    else:
        return "Multiply the first fraction by the reciprocal of the second fraction, then simplify."

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
        while len(used) < 6 and attempts < 400:
            attempts += 1
            p = _params(rng, diff)
            a, b, c, d = p["a"], p["b"], p["c"], p["d"]
            correct = Fraction(a * d, b * c)
            correct_text = fmt_frac(correct)

            offset = global_q_idx % len(ALL_RULES)
            rule_order = ALL_RULES[offset:] + ALL_RULES[:offset]

            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            ctx, tmpl = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
            stem_text = tmpl.format(**p)
            expr = f"({a} / {b}) / ({c} / {d})"
            correct_pos = pos_map[diff][len(used)]
            options = build_options(correct_text, distractors, correct_pos)

            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "6.NR.1.2",
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
