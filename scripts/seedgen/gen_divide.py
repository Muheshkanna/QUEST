"""Generator for g5-divide (n / d = q R r, r != 0).
easy   = 2-digit by 1-digit
medium = 3-digit by 2-digit
hard   = 4-digit by 2-digit with context
"""
import random
from . import get_correct_position, build_options, get_distractors, fmt_num

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
        ("food",   "A baker made {n} cookies. Each tray holds {d} cookies. How many full trays are there, and how many cookies are left over?"),
        ("sports", "{n} fans are seated in rows of {d}. How many full rows are there, and how many fans don't fill a row?"),
        ("school", "A school printed {n} worksheets. Each pack holds {d} sheets. How many full packs are there, and how many sheets remain?"),
        ("games",  "{n} gold coins are divided into chests of {d} each. How many full chests fit, and how many coins are left over?"),
        ("nature", "{n} seeds are packed {d} per envelope. How many full envelopes, and how many seeds are left unpacked?"),
    ],
    "hard": [
        ("food",   "A factory produced {n} jars of jam. Each shipping crate holds {d} jars. How many full crates are packed, and how many jars remain?"),
        ("sports", "An arena sold {n} tickets. Each section holds {d} fans. How many full sections are filled, and how many fans are in a partially filled section?"),
        ("school", "A library has {n} books to sort. Each shelf holds {d} books. How many shelves are completely full, and how many books go on a partially filled shelf?"),
        ("games",  "{n} monster health points are reduced in rounds of {d}. How many full rounds to reduce it, and how many HP are left after the last full round?"),
        ("nature", "{n} snowflakes fell on {d}-snowflake squares drawn in sand. How many full squares, and how many snowflakes are left over?"),
    ],
}

RULE_ORDER = ["dropped_the_remainder","swapped_quotient_and_remainder","stopped_subtracting_too_early","misplaced_quotient_digit","rounded_quotient_up_kept_remainder"]

def _make_params(rng, n_lo, n_hi, d_lo, d_hi):
    for _ in range(300):
        n = rng.randint(n_lo, n_hi)
        d = rng.randint(d_lo, d_hi)
        if d == 0:
            continue
        q = n // d
        r = n % d
        if r == 0 or q == 0:
            continue
        return {"n": n, "d": d, "q": q, "r": r}
    return {"n": 451, "d": 16, "q": 28, "r": 3}

def _correct_text(p):
    return f"{p['q']} R {p['r']}"

def _explanation(p):
    return (f"Divide {p['n']} by {p['d']}. "
            f"{p['d']} fits into {p['n']} exactly {p['q']} times ({p['d']} × {p['q']} = {p['d']*p['q']}). "
            f"The leftover is {p['n']} − {p['d']*p['q']} = {p['r']}. "
            f"So the answer is {p['q']} R {p['r']}.")

def _hint(p):
    return f"Think: what is the biggest multiple of {p['d']} that fits inside {p['n']}? The leftover is the remainder."

def generate(seed: int = 42):
    rng = random.Random(seed)
    questions = []
    q_index = 0
    ranges = {
        "easy":   (10, 99, 2, 9),
        "medium": (100, 999, 10, 99),
        "hard":   (1000, 9999, 10, 99),
    }
    for diff in ("easy", "medium", "hard"):
        stem_list = list(STEMS[diff])
        rng.shuffle(stem_list)
        n_lo, n_hi, d_lo, d_hi = ranges[diff]
        used = []
        attempts = 0
        while len(used) < 6 and attempts < 300:
            attempts += 1
            p = _make_params(rng, n_lo, n_hi, d_lo, d_hi)
            correct_text = _correct_text(p)
            distractors = get_distractors(TOPIC, p, correct_text, RULE_ORDER)
            if len(distractors) < 3:
                continue
            ctx, tmpl = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
            stem_text = tmpl.format(**p)
            correct_pos = get_correct_position(q_index)
            options = build_options(correct_text, distractors, correct_pos)
            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "5.NR.2",
                "difficulty": diff,
                "verifier_type": "division_with_remainder",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": f"divmod_rem({p['n']}, {p['d']})",
                "options": options,
                "correct_index": correct_pos,
                "answer": correct_text,
                "hint": _hint(p),
                "explanation": _explanation(p),
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
            q_index += 1
        questions.extend(used)
    return questions
