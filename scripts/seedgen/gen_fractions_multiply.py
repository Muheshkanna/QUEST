"""Generator for g5-fractions-multiply.
Every stem is a genuine 'part of a part' story problem where the total is a/b * c/d.
Requires a/b != c/d.
"""
import random
from fractions import Fraction
from . import get_topic_positions, build_options, get_distractors, fmt_frac

TOPIC = "g5-fractions-multiply"

STEMS = {
    "easy": [
        ("food",   "A cake recipe uses {a}/{b} of a bag of flour. A baker makes a small batch using {c}/{d} of that amount. What fraction of the bag of flour is used?"),
        ("sports", "A practice track covers {a}/{b} of a sports field. Cones mark off {c}/{d} of that track. What fraction of the sports field is marked by cones?"),
        ("school", "A display board takes up {a}/{b} of a classroom wall. Science posters cover {c}/{d} of that board. What fraction of the wall is covered by science posters?"),
        ("games",  "A game board fills {a}/{b} of a table. A castle map occupies {c}/{d} of that board. What fraction of the table does the castle map occupy?"),
        ("nature", "A garden bed takes up {a}/{b} of a yard. Bean plants cover {c}/{d} of that bed. What fraction of the yard is planted with beans?"),
    ],
    "medium": [
        ("food",   "A fruit bowl is {a}/{b} full of berries. Strawberries make up {c}/{d} of those berries. What fraction of the bowl is strawberries?"),
        ("sports", "A gym locker holds {a}/{b} of the school's sports gear. Basketball gear takes up {c}/{d} of that locker. What fraction of the school's sports gear is basketball gear?"),
        ("school", "A student spends {a}/{b} of a study session on math. Problem sets take up {c}/{d} of that math time. What fraction of the study session is spent on problem sets?"),
        ("games",  "A treasure chest holds {a}/{b} of a dungeon's gold. Gold coins make up {c}/{d} of that loot. What fraction of the dungeon's gold is in coins?"),
        ("nature", "A nature reserve covers {a}/{b} of a county. Oak trees cover {c}/{d} of that reserve. What fraction of the county is covered by oak trees?"),
    ],
    "hard": [
        ("food",   "A farmer's pantry is {a}/{b} stocked with grain. Wheat accounts for {c}/{d} of that grain. What fraction of the pantry is wheat?"),
        ("sports", "A swimming pool fills {a}/{b} of a recreation area. The deep end occupies {c}/{d} of that pool. What fraction of the recreation area is the deep end?"),
        ("school", "An art studio uses {a}/{b} of a school budget. Painting supplies take up {c}/{d} of that art budget. What fraction of the total budget goes to painting supplies?"),
        ("games",  "A guild library stores {a}/{b} of the world's scrolls. Magic spells fill {c}/{d} of those scrolls. What fraction of the world's scrolls are magic spells?"),
        ("nature", "A lake fills {a}/{b} of a valley. A wildlife sanctuary covers {c}/{d} of that lake. What fraction of the valley is the sanctuary?"),
    ],
}

ALL_RULES = [
    "added_fractions_instead",
    "cross_multiplies_instead_of_multiplying_straight",
    "multiplies_tops_adds_bottoms",
    "added_tops_multiplied_bottoms",
]

def _params(rng, diff):
    if diff == "easy":
        fracs = [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (3, 4)]
    elif diff == "medium":
        fracs = [(2, 3), (3, 4), (2, 5), (3, 5), (1, 4), (1, 3), (4, 5)]
    else:
        fracs = [(3, 5), (4, 5), (5, 6), (3, 8), (2, 7), (3, 7), (5, 8)]

    for _ in range(200):
        a, b = rng.choice(fracs)
        c, d = rng.choice(fracs)
        # require a/b != c/d
        if Fraction(a, b) == Fraction(c, d):
            continue
        # Ensure rules produce distinct options
        corr = Fraction(a * c, b * d)
        r_add = Fraction(a, b) + Fraction(c, d)
        r_cross = Fraction(a * d, b * c)
        r_top_mul = Fraction(a * c, b + d)
        r_top_add = Fraction(a + c, b * d)
        if len({corr, r_add, r_cross, r_top_mul, r_top_add}) == 5:
            return {"a": a, "b": b, "c": c, "d": d}
    return {"a": 2, "b": 3, "c": 1, "d": 4}

def _explanation(p, correct):
    a, b, c, d = p["a"], p["b"], p["c"], p["d"]
    return (f"Multiply top × top: {a} × {c} = {a*c}. "
            f"Multiply bottom × bottom: {b} × {d} = {b*d}. "
            f"The answer is {correct}.")

def _hint(diff):
    if diff == "easy":
        return "Find a fraction of a fraction by multiplying the tops together and the bottoms together."
    elif diff == "medium":
        return "Multiply straight across: top times top, bottom times bottom, then simplify."
    else:
        return "Multiply the two fractions straight across to find what portion of the whole is used."

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
            correct = Fraction(a * c, b * d)
            correct_text = fmt_frac(correct)

            offset = global_q_idx % len(ALL_RULES)
            rule_order = ALL_RULES[offset:] + ALL_RULES[:offset]

            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            ctx, tmpl = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
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
