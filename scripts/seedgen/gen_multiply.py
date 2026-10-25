"""Generator for g5-multiply.
Params: a, b two-digit; neither ends in 0; b >= 12.
easy = 2-digit x 1-digit-tens with small digits
medium = typical 2-digit x 2-digit
hard = 2-digit x 2-digit with larger digits in rich story problems
"""
import random
from . import get_topic_positions, build_options, get_distractors, fmt_num

TOPIC = "g5-multiply"

STEMS = {
    "easy": [
        ("food",   "A bakery packs {b} boxes of muffins. Each box contains {a} muffins. How many muffins are there in total?"),
        ("sports", "A youth league has {b} teams. Each team has {a} players. How many players are in the league?"),
        ("school", "A teacher orders {b} packs of colored pencils. Each pack contains {a} pencils. How many pencils were ordered?"),
        ("games",  "A player completes {b} quests. Each quest awards {a} gold coins. How much gold was earned in total?"),
        ("nature", "A garden has {b} flower beds. Each bed contains {a} tulips. How many tulips are there in total?"),
    ],
    "medium": [
        ("food",   "A restaurant uses {b} sacks of potatoes each month. Each sack weighs {a} pounds. How many pounds are used in total?"),
        ("sports", "A city fun run has {b} running clubs participating. Each club has {a} runners. How many runners are participating?"),
        ("school", "A school library receives {b} crates of reading books. Each crate holds {a} books. How many books were received?"),
        ("games",  "An armorer crafts {b} complete suits of plate mail. Each suit requires {a} metal plates. How many plates are needed?"),
        ("nature", "An apple orchard has {b} rows of fruit trees. Each row has {a} trees. How many fruit trees are in the orchard?"),
    ],
    "hard": [
        ("food",   "A regional food bank distributed {b} shipping pallets of canned goods. Each pallet carried {a} cans. How many cans were distributed in total?"),
        ("sports", "An international track meet booked {b} accommodation suites. Each suite housed {a} athletes. How many athletes were housed in total?"),
        ("school", "A county school district purchased {b} mobile learning carts. Each cart holds {a} student tablets. How many tablets were purchased in total?"),
        ("games",  "A fortress wall is constructed in {b} defensive tiers. Each tier requires {a} heavy granite stones. How many stones are needed to finish the wall?"),
        ("nature", "A conservation group planted {b} designated zones of forest. Each zone received {a} oak saplings. How many saplings were planted in total?"),
    ],
}

ALL_RULES = [
    "forgot_the_placeholder_zero",
    "multiplied_only_the_ones_digit",
    "skipped_the_cross_products",
    "added_instead_of_multiplying",
    "put_the_zero_on_the_wrong_row",
]

def _params(rng, diff):
    for _ in range(300):
        if diff == "easy":
            a = rng.randint(12, 34)
            b = rng.randint(12, 19)
        elif diff == "medium":
            a = rng.randint(23, 68)
            b = rng.randint(14, 49)
        else:
            a = rng.randint(45, 98)
            b = rng.randint(24, 89)

        # Neither ends in 0; b >= 12
        if a % 10 == 0 or b % 10 == 0 or b < 12:
            continue
        p = {"a": a, "b": b}
        correct = a * b
        r1 = a * (b % 10) + a * (b // 10)
        r2 = a * (b % 10)
        r3 = (10 * (a // 10)) * (10 * (b // 10)) + (a % 10) * (b % 10)
        r4 = a + b
        r5 = a * (b % 10) * 10 + a * (b // 10)
        # require distinct distractors
        if len({correct, r1, r2, r3, r4, r5}) == 6:
            return p
    return {"a": 23, "b": 14}

def _explanation(p, correct):
    a, b = p["a"], p["b"]
    ones = b % 10
    tens = b // 10
    prod1 = a * ones
    prod2 = a * tens * 10
    return (f"Multiply {a} by the ones digit {ones}: {a} × {ones} = {prod1}. "
            f"Multiply {a} by the tens digit {tens} (which is {tens * 10}): {a} × {tens * 10} = {prod2}. "
            f"Add the two partial products together: {prod1} + {prod2} = {correct}.")

def _hint(diff):
    if diff == "easy":
        return "Multiply by the ones digit first, then multiply by the tens digit with a placeholder zero."
    elif diff == "medium":
        return "Remember to include the placeholder zero on the second row before multiplying by the tens digit."
    else:
        return "Calculate both partial products carefully, aligning by place value before adding."

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
            a, b = p["a"], p["b"]
            correct = a * b
            correct_text = fmt_num(correct)

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
                "standard": "5.NR.2",
                "difficulty": diff,
                "verifier_type": "integer_arithmetic",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": f"{a} * {b}",
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
