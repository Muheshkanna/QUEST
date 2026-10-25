"""Generator for g5-decimal-ops.
easy = same number of places, no regrouping
medium = different decimal places
hard = regrouping across the decimal point plus word problem context
"""
import random
from . import get_topic_positions, build_options, get_distractors, fmt_num

TOPIC = "g5-decimal-ops"

STEMS = {
    "easy": {
        "+": [
            ("food",   "A baker mixes {a} kg of white sugar and {b} kg of brown sugar. What is the total mass?"),
            ("sports", "A runner ran {a} miles in the morning and {b} miles in the afternoon. What was the total distance?"),
            ("school", "A student has {a} metres of blue yarn and {b} metres of yellow yarn. How many metres of yarn in total?"),
            ("games",  "A player collected {a} grams of gold ore and {b} grams of silver ore. What is the total weight?"),
            ("nature", "A rain gauge recorded {a} cm of rain on Monday and {b} cm on Tuesday. What was the total rainfall?"),
        ],
        "-": [
            ("food",   "A chef had {a} kg of flour and used {b} kg for a bread order. How much flour is left?"),
            ("sports", "A cycling trail is {a} km long and a rider has finished {b} km. How many kilometres remain?"),
            ("school", "A ribbon was {a} metres long before a craft piece of {b} metres was cut off. How long is the ribbon now?"),
            ("games",  "A bag held {a} ounces of magic powder before a potion used {b} ounces. How many ounces remain?"),
            ("nature", "A reservoir level was {a} metres before it dropped by {b} metres. What is the new level?"),
        ],
    },
    "medium": {
        "+": [
            ("food",   "A juice bottle contains {a} litres of apple juice and {b} litres of berry juice. What is the total volume?"),
            ("sports", "A swimmer swam {a} laps in the first set and {b} laps in the second set. What is the total distance?"),
            ("school", "A science experiment combined {a} grams of salt with {b} grams of mineral powder. What is the total mass?"),
            ("games",  "A treasure stash has {a} kg of silver bars and {b} kg of gold coins. What is the combined weight?"),
            ("nature", "A garden path is {a} metres long and an extension adds {b} metres. What is the new total length?"),
        ],
        "-": [
            ("food",   "A bottle held {a} litres of olive oil before a chef poured out {b} litres. How many litres remain?"),
            ("sports", "A running track lap is {a} km and an athlete has run {b} km. How much of the lap remains?"),
            ("school", "A roll of craft paper was {a} metres long before {b} metres was cut for a poster. How much paper is left?"),
            ("games",  "A potion flask contained {a} ounces of elixir before an adventurer drank {b} ounces. How much elixir is left?"),
            ("nature", "A tree seedling was {a} cm tall and pruned by {b} cm. What is its new height?"),
        ],
    },
    "hard": {
        "-": [
            ("food",   "A baker prepared {a} kg of dough, and a morning delivery used {b} kg. How much dough remains for the bakery?"),
            ("sports", "An endurance course is {a} km long. A runner has completed {b} km so far. How many kilometres are left to run?"),
            ("school", "An art canvas was {a} metres long before a border trim of {b} metres was removed. What is the length of the trimmed canvas?"),
            ("games",  "A guild vault stored {a} ounces of crystal essence before a spell consumed {b} ounces. How many ounces remain in the vault?"),
            ("nature", "A garden cistern held {a} kilolitres of rainwater before {b} kilolitres was pumped out. How many kilolitres remain in the cistern?"),
        ],
        "+": [
            ("food",   "A caterer mixed {a} kg of pasta with {b} kg of fresh sauce for an event. What was the total weight of the dish?"),
            ("sports", "A relay team covered {a} km in the road leg and {b} km in the trail leg. What was the total relay distance?"),
            ("school", "A school mural project used {a} litres of blue paint and {b} litres of white paint. How many litres of paint were used?"),
            ("games",  "A mining team hauled {a} tons of copper ore and {b} tons of iron ore. What was the total ore weight?"),
            ("nature", "An environmental study measured {a} mm of rain at the valley station and {b} mm at the ridge station. What was the combined rainfall?"),
        ],
    },
}

ALL_RULES = [
    "ignored_the_decimal_point",
    "subtracted_smaller_digit_from_larger",
    "dropped_the_carry",
    "used_the_wrong_operation",
    "forgot_the_decimal_point",
]

def _params(rng, diff):
    if diff == "easy":
        # different decimal places (1 vs 2 places), no regrouping
        for _ in range(200):
            op = rng.choice(["+", "-"])
            if op == "+":
                a = round(rng.choice([1.4, 2.3, 3.2, 4.1, 2.5]), 1)
                b = round(rng.choice([1.23, 2.14, 1.32, 2.21, 1.15]), 2)
            else:
                a = round(rng.choice([5.76, 6.85, 7.94, 8.67, 6.78]), 2)
                b = round(rng.choice([1.3, 2.4, 3.2, 2.1, 1.5]), 1)
            return {"a": a, "b": b, "op": op}
        return {"a": 3.2, "b": 1.45, "op": "+"}

    elif diff == "medium":
        # different decimal places
        for _ in range(300):
            op = rng.choice(["+", "-"])
            if op == "+":
                a = round(rng.choice([1.5, 2.5, 3.5, 4.5, 2.4, 3.6]), 1)
                b = round(rng.choice([1.25, 2.15, 1.35, 2.45, 1.15]), 2)
            else:
                a = round(rng.choice([5.45, 6.75, 4.85, 7.65, 8.55]), 2)
                b = round(rng.choice([2.3, 1.4, 3.2, 2.1, 1.5]), 1)
            return {"a": a, "b": b, "op": op}
        return {"a": 3.5, "b": 1.25, "op": "+"}

    else:
        # hard: regrouping across the decimal point (especially subtraction like 5.4 - 2.18)
        for _ in range(300):
            op = rng.choice(["-", "+"])
            if op == "-":
                w1 = rng.randint(4, 9)
                w2 = rng.randint(1, 3)
                t1 = rng.randint(1, 5)
                t2 = rng.randint(6, 9)
                # e.g. 5.4 - 2.18
                a = round(w1 + t1 / 10, 1)
                b = round(w2 + rng.randint(1, 3) / 10 + t2 / 100, 2)
            else:
                # addition with carry across decimal point, e.g. 4.85 + 2.7
                a = round(rng.randint(3, 7) + rng.randint(6, 9) / 10 + rng.randint(4, 8) / 100, 2)
                b = round(rng.randint(2, 5) + rng.randint(5, 9) / 10, 1)
            return {"a": a, "b": b, "op": op}
        return {"a": 5.4, "b": 2.18, "op": "-"}

def _explanation(p, correct):
    a, b, op = p["a"], p["b"], p["op"]
    if op == "+":
        return (f"Line up the decimal points first. Add column by column from right to left, "
                f"carrying to the next place value when a column reaches 10 or more. "
                f"{a} + {b} = {correct}.")
    else:
        return (f"Line up the decimal points first, placing placeholder zeros where needed. "
                f"Subtract column by column from right to left, regrouping from the next place value when needed. "
                f"{a} - {b} = {correct}.")

def _hint(diff):
    if diff == "easy":
        return "Line up the decimal points vertically before adding or subtracting each column."
    elif diff == "medium":
        return "Write placeholder zeros so both numbers have the same number of digits after the decimal point."
    else:
        return "Line up the decimals and regroup carefully across the place value columns."

def generate(seed: int = 42):
    rng = random.Random(seed)
    pos_map = get_topic_positions(TOPIC, seed)
    questions = []
    global_q_idx = 0
    for diff in ("easy", "medium", "hard"):
        stems_diff = STEMS[diff]
        used = []
        attempts = 0
        while len(used) < 6 and attempts < 500:
            attempts += 1
            p = _params(rng, diff)
            op = p["op"]
            if op == "+":
                correct_val = round(p["a"] + p["b"], 6)
            else:
                correct_val = round(p["a"] - p["b"], 6)
            correct_text = fmt_num(correct_val)

            offset = global_q_idx % len(ALL_RULES)
            rule_order = ALL_RULES[offset:] + ALL_RULES[:offset]

            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            stem_options = stems_diff[op]
            ctx, tmpl = stem_options[len(used) % len(stem_options)]
            template_id = f"{TOPIC}-{diff}-{op}-{ctx}"
            stem_text = tmpl.format(**p)
            correct_pos = pos_map[diff][len(used)]
            options = build_options(correct_text, distractors, correct_pos)

            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "5.NR.4",
                "difficulty": diff,
                "verifier_type": "decimal_arithmetic",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": f"{p['a']} {op} {p['b']}",
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
