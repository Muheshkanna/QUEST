"""Generator for g6-percents."""
import random
from . import get_topic_positions, build_options, get_distractors, fmt_num

TOPIC = "g6-percents"

STEMS = {
    "easy": [
        ("food",   "A restaurant bill is ${n}. You leave a {p}% tip. How much is the tip?"),
        ("sports", "A team won {p}% of their {n} games this season. How many games did they win?"),
        ("school", "There are {n} students in school. {p}% brought their own lunch. How many students brought lunch?"),
        ("games",  "A player earns {n} coins. Spending {p}% on upgrades, how many coins are spent?"),
        ("nature", "A forest has {n} trees. {p}% are oak trees. How many oak trees are there?"),
    ],
    "medium": [
        ("food",   "A bag of trail mix has {n} grams. {p}% of it is nuts. How many grams of nuts are there?"),
        ("sports", "An athlete runs {n} metres in a race. {p}% of the route is uphill. How many metres are uphill?"),
        ("school", "A school raised ${n} for charity. {p}% goes to the food bank. How much money goes to the food bank?"),
        ("games",  "A dungeon has {n} rooms. {p}% have treasure. How many rooms have treasure?"),
        ("nature", "A lake has {n} species of fish. {p}% are endangered. How many species are endangered?"),
    ],
    "hard": [
        ("food",   "A market has {n} oranges. {p}% of them are sold in the morning. How many oranges were sold?"),
        ("sports", "A basketball team scored {n} points in a match. {p}% came from three-pointers. How many points was that?"),
        ("school", "A test has {n} questions. A student got {p}% correct. How many questions did they answer correctly?"),
        ("games",  "A castle has {n} guards. During a patrol, {p}% are stationed at the gate. How many guards are at the gate?"),
        ("nature", "A wildlife park has {n} birds. {p}% migrate south for the winter. How many birds migrate south?"),
    ],
}

ALL_RULES = [
    "found_one_percent_only",
    "divided_instead_of_multiplying",
    "multiplied_by_percent_number",
    "moved_decimal_wrong_way",
    "found_the_leftover_amount",
]

def _params(rng, diff):
    if diff == "easy":
        percents = [10, 20, 25, 50]
        ns = [40, 60, 80, 100, 120]
    elif diff == "medium":
        percents = [15, 20, 30, 40]
        ns = [60, 80, 120, 150, 200]
    else:
        percents = [15, 25, 35, 40, 45]
        ns = [80, 100, 120, 200, 240]
    for _ in range(100):
        p = rng.choice(percents)
        n = rng.choice(ns)
        correct = (p / 100) * n
        # keep whole number answers for clarity and ensure n/p != correct for divided_instead_of_multiplying
        if correct == int(correct) and abs(n / p - correct) > 1e-6:
            return {"p": p, "n": n}
    return {"p": 15, "n": 60}

def _explanation(p_val, n, correct):
    dec = p_val / 100
    return (f"{p_val}% means {p_val} parts out of 100, which is {dec}. "
            f"Multiply: {dec} × {n} = {correct}.")

def _hint(diff):
    if diff == "easy":
        return "Percent means parts per 100. Write it as a decimal first, then multiply."
    elif diff == "medium":
        return "How can you change a percent into a decimal or fraction before multiplying by the total?"
    else:
        return "Convert the percent to a decimal by dividing by 100, then find that share of the total."

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
            pv, n = p["p"], p["n"]
            correct_val = (pv / 100) * n
            correct_text = fmt_num(correct_val)

            offset = global_q_idx % len(ALL_RULES)
            rule_order = ALL_RULES[offset:] + ALL_RULES[:offset]

            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            ctx, tmpl = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
            stem_text = tmpl.format(p=pv, n=n)
            correct_pos = pos_map[diff][len(used)]
            options = build_options(correct_text, distractors, correct_pos)

            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "6.NR.4.6",
                "difficulty": diff,
                "verifier_type": "percent_calculation",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": f"{pv}% of {n}",
                "options": options,
                "correct_index": correct_pos,
                "answer": correct_text,
                "hint": _hint(diff),
                "explanation": _explanation(pv, n, correct_text),
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
            global_q_idx += 1
        questions.extend(used)
    return questions
