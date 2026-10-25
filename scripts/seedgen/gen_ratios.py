"""Generator for g6-ratios."""
import random
from . import get_topic_positions, build_options, get_distractors, fmt_num

TOPIC = "g6-ratios"

STEMS = {
    "easy": [
        ("food",   "In a recipe, the ratio of cups of flour to cups of sugar is {a} to {b}. An equivalent ratio scaled by {k} is:"),
        ("sports", "A team has {a} defenders for every {b} forwards. With {k} times as many players, the equivalent ratio is:"),
        ("school", "For every {a} fiction books, there are {b} nonfiction books. Using a factor of {k}, the equivalent ratio is:"),
        ("games",  "A bag has {a} red gems for every {b} blue gems. Scaling up by {k}, the equivalent ratio is:"),
        ("nature", "In a garden, the ratio of roses to daisies is {a}:{b}. Multiplied by {k}, the equivalent ratio is:"),
    ],
    "medium": [
        ("food",   "A smoothie uses {a} scoops of protein for every {b} cups of fruit. Scaling by {k}, the equivalent ratio is:"),
        ("sports", "For every {a} laps run, a swimmer rests for {b} minutes. Using a scale factor of {k}, the equivalent ratio is:"),
        ("school", "A class has {a} boys for every {b} girls. With {k} times the students, the equivalent ratio is:"),
        ("games",  "A game spawns {a} monsters for every {b} heroes. Scaled by {k}, the equivalent ratio is:"),
        ("nature", "A birdwatcher spots {a} hawks for every {b} sparrows. Multiplied by {k}, the equivalent ratio is:"),
    ],
    "hard": [
        ("food",   "A baker uses {a} eggs for every {b} cups of milk. Scaling the batch by {k}, the equivalent ratio is:"),
        ("sports", "A coach assigns {a} drills for every {b} minutes of game play. With a factor of {k}, the equivalent ratio is:"),
        ("school", "A library has {a} hardcovers for every {b} paperbacks. Scaled by {k}, the equivalent ratio is:"),
        ("games",  "A dungeon has {a} locked doors for every {b} open doors. Scaling by {k}, the equivalent ratio is:"),
        ("nature", "An aquarium has {a} saltwater tanks for every {b} freshwater tanks. Multiplied by {k}, the equivalent ratio is:"),
    ],
}

ALL_RULES = [
    "additive_ratio_scaling",
    "inverts_ratio_terms_order",
    "multiplied_only_first_term",
    "part_to_part_vs_part_to_whole",
    "squared_terms",
]

def _params(rng, diff):
    if diff == "easy":
        vals = [(2, 3), (3, 4), (2, 5), (3, 5), (1, 4), (1, 3), (4, 5)]
        ks = [2, 3, 4]
    elif diff == "medium":
        vals = [(3, 4), (2, 7), (5, 6), (3, 8), (4, 5), (5, 8), (3, 7)]
        ks = [3, 4, 5]
    else:
        vals = [(5, 7), (3, 11), (4, 9), (7, 8), (6, 11), (5, 9), (7, 10)]
        ks = [4, 5, 6]
    for _ in range(100):
        a, b = rng.choice(vals)
        k = rng.choice(ks)
        if a != b and k != a and k != b:
            return {"a": a, "b": b, "k": k}
    return {"a": 2, "b": 3, "k": 4}

def _explanation(p, correct):
    a, b, k = p["a"], p["b"], p["k"]
    return (f"To find an equivalent ratio, multiply both numbers by the same factor. "
            f"{a} × {k} = {a*k} and {b} × {k} = {b*k}. "
            f"The equivalent ratio is {correct}.")

def _hint(diff):
    if diff == "easy":
        return "Multiply both numbers in the ratio by the same factor."
    elif diff == "medium":
        return "What happens to each number in the ratio when you scale it up?"
    else:
        return "Think about what operation keeps the relationship between two numbers the same."

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
            a, b, k = p["a"], p["b"], p["k"]
            correct_text = f"{k*a}:{k*b}"

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
                "standard": "6.NR.4.1",
                "difficulty": diff,
                "verifier_type": "ratio_comparison",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": f"ratio_scale({a}, {b}, {k})",
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
