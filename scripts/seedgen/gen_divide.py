"""Generator for g5-divide (n / d = q R r, r != 0).
easy   = 2-digit by 1-digit
medium = 3-digit by 2-digit (d not a multiple of 10)
hard   = 4-digit by 2-digit with context (d not a multiple of 10)
Every question includes rounded_quotient_up_kept_remainder.
"""
import random
from . import get_topic_positions, build_options, get_distractors, fmt_num

TOPIC = "g5-divide"

STEMS = {
    "easy": [
        ("food",   "{n} grapes are shared equally among {d} kids. How many does each kid get, and how many are left over?"),
        ("sports", "{n} team stickers are divided equally into {d} boxes. How many stickers are in each box, and how many are left over?"),
        ("school", "{n} books are placed equally on {d} shelves. How many books per shelf, and how many are left over?"),
        ("games",  "{n} game tokens are split into groups of {d}. How many full groups are there, and how many tokens remain?"),
        ("nature", "{n} leaves are bundled in groups of {d}. How many bundles fit, and how many leaves are left over?"),
    ],
    "medium": [
        ("food",   "A bakery made {n} cookies. Each tray holds {d} cookies. How many full trays are packed, and how many cookies remain?"),
        ("sports", "{n} fans are seated in rows of {d}. How many full rows are there, and how many fans are in a partially filled row?"),
        ("school", "A school printed {n} worksheets in packs of {d}. How many full packs are there, and how many sheets are left over?"),
        ("games",  "{n} gold coins are stored in chests holding {d} coins each. How many full chests are filled, and how many coins remain?"),
        ("nature", "{n} tree seedlings are bundled in groups of {d}. How many full bundles are there, and how many seedlings are left?"),
    ],
    "hard": [
        ("food",   "A fruit orchard packed {n} apples into crates of {d} apples each. How many full crates were packed, and how many apples were left over?"),
        ("sports", "An arena distributed {n} programs equally into {d} concession stands. How many full bundles per stand, and how many remain?"),
        ("school", "A district warehouse received {n} notebooks to pack into boxes of {d}. How many full boxes are packed, and how many are left over?"),
        ("games",  "A dungeon crawler requires {n} experience points divided across {d} quest chapters. How many points per full chapter, and what is the remainder?"),
        ("nature", "Scientists tracked {n} bird migration sightings across {d} observation zones. How many sightings per zone on average, and how many were leftover?"),
    ],
}

OTHER_RULES = [
    "misplaced_quotient_digit",
    "stopped_subtracting_too_early",
    "dropped_the_remainder",
    "swapped_quotient_and_remainder",
]

def _make_params(rng, n_lo, n_hi, d_lo, d_hi):
    for _ in range(300):
        d = rng.randint(d_lo, d_hi)
        if d % 10 == 0 or d == 0:
            continue
        n = rng.randint(n_lo, n_hi)
        q = n // d
        r = n % d
        # require non-zero remainder and valid quotient
        if r == 0 or q == 0:
            continue
        # ensure swapped quotient and remainder is distinct
        if q == r:
            continue
        return {"n": n, "d": d, "q": q, "r": r}
    return {"n": 451, "d": 16, "q": 28, "r": 3}

def _correct_text(p):
    return f"{p['q']} R {p['r']}"

def _explanation(p):
    n, d, q, r = p["n"], p["d"], p["q"], p["r"]
    product = d * q
    return (f"Divide {n} by {d}. "
            f"{d} goes into {n} exactly {q} times because {d} × {q} = {product}. "
            f"The leftover amount is {n} − {product} = {r}. "
            f"So the answer is {q} R {r}.")

def _hint(p, diff):
    d, n = p["d"], p["n"]
    if diff == "easy":
        return f"Find the biggest multiple of {d} that fits inside {n}. The leftover amount is your remainder."
    elif diff == "medium":
        return f"How many full groups of {d} can you make from {n}? The leftover is the remainder."
    else:
        return f"Use place-value division step by step. Remember that your remainder must be smaller than {d}."

def generate(seed: int = 42):
    rng = random.Random(seed)
    pos_map = get_topic_positions(TOPIC, seed)
    questions = []
    global_q_idx = 0
    ranges = {
        "easy":   (10, 99, 2, 9),
        "medium": (100, 999, 11, 99),
        "hard":   (1000, 9999, 11, 99),
    }

    for diff in ("easy", "medium", "hard"):
        stem_list = list(STEMS[diff])
        rng.shuffle(stem_list)
        n_lo, n_hi, d_lo, d_hi = ranges[diff]
        used = []
        attempts = 0
        while len(used) < 6 and attempts < 400:
            attempts += 1
            p = _make_params(rng, n_lo, n_hi, d_lo, d_hi)
            correct_text = _correct_text(p)

            # Every question includes rounded_quotient_up_kept_remainder
            # plus rotating candidate pool from the remaining 4 rules
            offset = global_q_idx % len(OTHER_RULES)
            rot_others = OTHER_RULES[offset:] + OTHER_RULES[:offset]
            rule_order = ["rounded_quotient_up_kept_remainder"] + rot_others

            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            # Ensure rounded_quotient_up_kept_remainder is among the chosen distractors
            if not any(d["rule_id"] == "rounded_quotient_up_kept_remainder" for d in distractors):
                continue

            ctx, tmpl = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
            stem_text = tmpl.format(**p)
            correct_pos = pos_map[diff][len(used)]
            options = build_options(correct_text, distractors, correct_pos)

            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "5.NR.2.2",
                "difficulty": diff,
                "verifier_type": "division_with_remainder",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": f"divmod_rem({p['n']}, {p['d']})",
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
            global_q_idx += 1
        questions.extend(used)
    return questions
