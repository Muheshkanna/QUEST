"""Generator for g5-fractions-add.
easy   = same denominator
medium = one denominator a multiple of the other (b != d, d = k*b or b = k*d)
hard   = unlike denominators + two-step word problem
"""
import random
from fractions import Fraction
from math import lcm
from . import get_correct_position, build_options, get_distractors, fmt_frac

TOPIC = "g5-fractions-add"

EASY_STEMS = [
    ("food",   "A baker used {a}/{b} cup of flour for cookies and {c}/{b} cup for a cake. How much flour was used in all?"),
    ("sports", "A runner drank {a}/{b} litre of water before the race and {c}/{b} litre after. How much did they drink total?"),
    ("school", "You coloured {a}/{b} of a page in art class and {c}/{b} more for the border. What fraction of the page is coloured?"),
    ("games",  "In a board game you moved {a}/{b} of the track on your first turn and {c}/{b} on your second. How far did you travel?"),
    ("nature", "A garden path has {a}/{b} metres of gravel on the left side and {c}/{b} metres on the right. What is the total length?"),
]
MEDIUM_STEMS = [
    ("food",   "A smoothie needs {a}/{b} cup of berries and {c}/{d} cup of mango. How much fruit is needed altogether?"),
    ("sports", "A swimmer swam {a}/{b} of a length in training and {c}/{d} of a length for cool-down. What is the total fraction swum?"),
    ("school", "One shelf holds {a}/{b} of a set of books and a second shelf holds {c}/{d} of the same set. What fraction is shelved?"),
    ("games",  "A game map shows treasure at {a}/{b} across the island. A second chest is {c}/{d} further. How far from the start is the second chest?"),
    ("nature", "A plant grew {a}/{b} metre in spring and {c}/{d} metre in summer. How much did it grow altogether?"),
]
HARD_STEMS = [
    ("food",   "A recipe needs {a}/{b} litre of milk for the batter and {c}/{d} litre for the sauce. A chef already has 1/{b} litre. How much MORE milk must they buy to have enough for both?"),
    ("sports", "Two relay runners cover {a}/{b} and {c}/{d} of the total course. What fraction of the total course have they completed together?"),
    ("school", "One project takes {a}/{b} of a week and a second project takes {c}/{d} of a week. How much of the week do both projects take in total?"),
    ("games",  "A wizard has two spell scrolls that restore {a}/{b} and {c}/{d} of a health bar. Together, what fraction of the health bar is restored?"),
    ("nature", "A river flooded {a}/{b} of a valley in January and {c}/{d} more in February. What fraction of the valley flooded over those two months?"),
]

RULE_ORDER_EASY   = ["added_tops_and_bottoms","multiplied_instead_of_adding","subtracted_instead_of_adding","renamed_bottom_kept_tops","added_tops_kept_first_bottom"]
RULE_ORDER_MEDIUM = ["added_tops_and_bottoms","renamed_bottom_kept_tops","subtracted_instead_of_adding","multiplied_instead_of_adding","added_tops_kept_first_bottom"]
RULE_ORDER_HARD   = ["renamed_bottom_kept_tops","added_tops_and_bottoms","added_tops_kept_first_bottom","subtracted_instead_of_adding","multiplied_instead_of_adding"]

def _easy_params(rng):
    """Same denominator."""
    b = rng.choice([4,6,8,10,12])
    max_top = b - 1
    for _ in range(100):
        a = rng.randint(1, max_top - 1)
        c = rng.randint(1, max_top - a)
        if a + c < b:
            return {"a": a, "b": b, "c": c, "d": b}
    return {"a": 1, "b": 4, "c": 1, "d": 4}

def _medium_params(rng):
    """b and d different, one a multiple of the other."""
    bases = [3,4,5,6,8]
    for _ in range(100):
        b = rng.choice(bases)
        k = rng.choice([2,3])
        d = b * k
        a = rng.randint(1, b - 1)
        c = rng.randint(1, d - 1)
        total = Fraction(a, b) + Fraction(c, d)
        if total < 1:
            return {"a": a, "b": b, "c": c, "d": d}
    return {"a": 1, "b": 4, "c": 1, "d": 8}

def _hard_params(rng):
    """Unlike denominators, not multiples."""
    pairs = [(3,4),(3,8),(4,6),(5,6),(3,5),(4,5),(5,8),(6,8)]
    for _ in range(100):
        b, d = rng.choice(pairs)
        a = rng.randint(1, b - 1)
        c = rng.randint(1, d - 1)
        total = Fraction(a, b) + Fraction(c, d)
        if total < 1:
            return {"a": a, "b": b, "c": c, "d": d}
    return {"a": 1, "b": 3, "c": 1, "d": 4}

def _explanation(p, correct_frac):
    a, b, c, d = p["a"], p["b"], p["c"], p["d"]
    L = lcm(b, d)
    na = a * (L // b)
    nc = c * (L // d)
    simplified = fmt_frac(correct_frac)
    if L == b and L == d:
        return (f"Both fractions already share the denominator {b}. "
                f"Add just the tops: {a} + {c} = {a+c}. "
                f"The answer is {a+c}/{b}" + (f" = {simplified}." if Fraction(a+c,b) != correct_frac else "."))
    else:
        return (f"Find the common denominator: lcm({b},{d}) = {L}. "
                f"Convert: {a}/{b} = {na}/{L} and {c}/{d} = {nc}/{L}. "
                f"Now add the tops: {na} + {nc} = {na+nc}, giving {na+nc}/{L}" +
                (f" = {simplified}." if Fraction(na+nc, L) != correct_frac else "."))

def _hint(p):
    b, d = p["b"], p["d"]
    if b == d:
        return f"When the bottom numbers match, you can add just the top numbers and keep the bottom."
    return f"The bottoms are different. Find a number that both {b} and {d} go into evenly before adding."

def generate(seed: int = 42):
    rng = random.Random(seed)
    questions = []
    configs = [("easy", _easy_params, EASY_STEMS, RULE_ORDER_EASY, 6),
               ("medium", _medium_params, MEDIUM_STEMS, RULE_ORDER_MEDIUM, 6),
               ("hard", _hard_params, HARD_STEMS, RULE_ORDER_HARD, 6)]
    q_index = 0
    for diff, param_fn, stems, rule_order, count in configs:
        stem_cycle = list(stems)
        rng.shuffle(stem_cycle)
        used = []
        attempts = 0
        while len(used) < count and attempts < 200:
            attempts += 1
            p = param_fn(rng)
            correct_frac = Fraction(p["a"], p["b"]) + Fraction(p["c"], p["d"])
            correct_text = fmt_frac(correct_frac)
            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue
            stem_entry = stem_cycle[len(used) % len(stem_cycle)]
            context, tmpl = stem_entry
            stem_text = tmpl.format(**p)
            template_id = f"{TOPIC}-{diff}-{context}"
            expr = f"{p['a']}/{p['b']} + {p['c']}/{p['d']}"
            correct_pos = get_correct_position(q_index)
            options = build_options(correct_text, distractors, correct_pos)
            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "5.NR.3.3",
                "difficulty": diff,
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": expr,
                "options": options,
                "correct_index": correct_pos,
                "answer": correct_text,
                "hint": _hint(p),
                "explanation": _explanation(p, correct_frac),
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
            q_index += 1
        questions.extend(used)
    return questions
