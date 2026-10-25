"""Generator for g6-percents."""
import random
from . import get_correct_position, build_options, get_distractors, fmt_num

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
        ("food",   "A store has {n} apples. {p}% are bruised and removed. How many apples are NOT bruised?"),
        ("sports", "A team scores {n} points total. {p}% come from three-pointers. How many points come from three-pointers?"),
        ("school", "A test has {n} questions. A student got {p}% correct. How many questions did they get right?"),
        ("games",  "A village has {n} villagers. During a storm, {p}% took shelter indoors. How many took shelter?"),
        ("nature", "A reef has {n} coral formations. Scientists say {p}% are healthy. How many are healthy?"),
    ],
}

RULE_ORDER = ["multiplied_by_percent_number","moved_decimal_wrong_way","found_the_leftover_amount","divided_instead_of_multiplying","found_one_percent_only"]

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
        if correct == int(correct):  # keep whole-number answers for clarity
            return {"p": p, "n": n}
    return {"p": 15, "n": 60}

def _explanation(p_val, n, correct):
    return (f"{p_val}% means {p_val} per 100, so convert to a decimal: {p_val} ÷ 100 = {p_val/100}. "
            f"Multiply: {p_val/100} × {n} = {correct}.")

def _hint(p_val, n):
    return f"Convert the percent to a decimal by dividing by 100 first, then multiply."

def generate(seed: int = 42):
    rng = random.Random(seed)
    questions = []
    q_index = 0
    for diff in ("easy", "medium", "hard"):
        stem_list = list(STEMS[diff])
        rng.shuffle(stem_list)
        used = []
        attempts = 0
        while len(used) < 6 and attempts < 200:
            attempts += 1
            p = _params(rng, diff)
            pv, n = p["p"], p["n"]
            correct_val = (pv / 100) * n
            correct_text = fmt_num(correct_val)
            distractors = get_distractors(TOPIC, p, correct_text, RULE_ORDER)
            if len(distractors) < 3:
                continue
            ctx, tmpl = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
            stem_text = tmpl.format(p=pv, n=n)
            correct_pos = get_correct_position(q_index)
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
                "hint": _hint(pv, n),
                "explanation": _explanation(pv, n, correct_text),
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
            q_index += 1
        questions.extend(used)
    return questions
