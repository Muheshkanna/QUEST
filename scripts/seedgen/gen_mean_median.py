"""Generator for g6-mean-median."""
import random
from . import get_topic_positions, build_options, get_distractors, fmt_num

TOPIC = "g6-mean-median"

STEMS_MEAN = {
    "easy": [
        ("food",   "A chef rates {k} dishes with scores {data_str}. What is the mean score?"),
        ("sports", "A player scored {data_str} points across {k} games. What is the mean?"),
        ("school", "A student got test scores of {data_str}. What is the mean score?"),
    ],
    "medium": [
        ("food",   "Daily sales at a bakery were {data_str} loaves over {k} days. What is the mean?"),
        ("sports", "An athlete ran {data_str} laps across {k} days. Find the mean."),
        ("school", "Quiz scores were {data_str}. Find the mean."),
    ],
    "hard": [
        ("food",   "A cafe served {data_str} customers over {k} days. What is the mean number per day?"),
        ("sports", "Scores across {k} matches were {data_str}. What is the mean?"),
        ("school", "A class's project grades were {data_str}. What is the mean?"),
    ],
}

STEMS_MEDIAN = {
    "easy": [
        ("games",  "The {k} players earned {data_str} coins. What is the median?"),
        ("nature", "Heights of {k} plants are {data_str} cm. What is the median?"),
    ],
    "medium": [
        ("games",  "Daily play times were {data_str} minutes. What is the median?"),
        ("nature", "Temperatures over {k} days were {data_str}°F. Find the median."),
    ],
    "hard": [
        ("games",  "Guild members earned {data_str} experience points. What is the median?"),
        ("nature", "Rainfall across {k} days was {data_str} mm. What is the median?"),
    ],
}

ALL_RULES = [
    "finds_median_without_ordering_data",
    "confuses_mean_with_median",
    "gave_the_total_instead_of_the_mean",
    "finds_range_instead",
    "ignores_middle_average_for_even_count",
]

def _make_data(rng, diff, target):
    """Generate a list of integers where mean != median."""
    if diff == "easy":
        count = 5
        lo, hi = 3, 15
    elif diff == "medium":
        count = 5 if target == "mean" else 6
        lo, hi = 5, 25
    else:
        count = 7 if target == "mean" else 6
        lo, hi = 10, 50
    for _ in range(200):
        data = [rng.randint(lo, hi) for _ in range(count)]
        s = sorted(data)
        n = len(s)
        mean_val = sum(data) / n
        if n % 2 == 1:
            med_val = s[n // 2]
        else:
            med_val = (s[n // 2 - 1] + s[n // 2]) / 2
        # require integer correct answer, mean != median, raw middle != sorted middle
        if target == "mean":
            if mean_val != int(mean_val):
                continue
            correct = int(mean_val)
        else:
            if med_val != int(med_val):
                continue
            correct = int(med_val)
        if mean_val == med_val:
            continue
        raw_middle = data[n // 2]
        sorted_middle = s[n // 2] if n % 2 == 1 else med_val
        if raw_middle == sorted_middle:
            continue
        range_val = max(data) - min(data)
        if range_val == correct:
            continue
        return data, correct
    return [9, 2, 7, 1, 5], 5

def _explanation_mean(data, correct):
    total = sum(data)
    k = len(data)
    return (f"Add all the values together: {' + '.join(str(x) for x in data)} = {total}. "
            f"Then divide by the number of values: {total} ÷ {k} = {correct}.")

def _explanation_median(data, correct):
    s = sorted(data)
    n = len(s)
    ordered = ", ".join(str(x) for x in s)
    if n % 2 == 1:
        return (f"First sort the numbers: {ordered}. "
                f"The middle number is {correct}.")
    else:
        m1, m2 = s[n // 2 - 1], s[n // 2]
        return (f"First sort the numbers: {ordered}. "
                f"The two middle numbers are {m1} and {m2}. "
                f"Find the halfway point: ({m1} + {m2}) ÷ 2 = {correct}.")

def _hint(diff, target):
    if target == "mean":
        if diff == "easy":
            return "Add all the numbers together, then divide by how many numbers there are."
        elif diff == "medium":
            return "The mean is the total shared equally among all values."
        else:
            return "Find the total sum first, then figure out the fair share."
    else:
        if diff == "easy":
            return "Put the numbers in order from smallest to largest, then find the middle."
        elif diff == "medium":
            return "After ordering, how do you find the center when there's an even count?"
        else:
            return "Sort the data, then locate the center position."

def generate(seed: int = 42):
    rng = random.Random(seed)
    pos_map = get_topic_positions(TOPIC, seed)
    questions = []
    global_q_idx = 0

    for diff in ("easy", "medium", "hard"):
        mean_stems = list(STEMS_MEAN[diff])
        med_stems = list(STEMS_MEDIAN[diff])
        rng.shuffle(mean_stems)
        rng.shuffle(med_stems)
        # 3 mean + 3 median per difficulty
        used = []
        attempts = 0
        mean_count = 0
        med_count = 0
        while len(used) < 6 and attempts < 600:
            attempts += 1
            if mean_count < 3:
                target = "mean"
            elif med_count < 3:
                target = "median"
            else:
                break

            data, correct = _make_data(rng, diff, target)
            correct_text = fmt_num(correct)
            k = len(data)
            data_str = ", ".join(str(x) for x in data)

            params = {"data": data, "target": target}

            offset = global_q_idx % len(ALL_RULES)
            rule_order = ALL_RULES[offset:] + ALL_RULES[:offset]

            distractors = get_distractors(TOPIC, params, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            if target == "mean":
                ctx, tmpl = mean_stems[mean_count % len(mean_stems)]
                expl = _explanation_mean(data, correct_text)
                mean_count += 1
            else:
                ctx, tmpl = med_stems[med_count % len(med_stems)]
                expl = _explanation_median(data, correct_text)
                med_count += 1

            template_id = f"{TOPIC}-{diff}-{target}-{ctx}"
            stem_text = tmpl.format(k=k, data_str=data_str)
            correct_pos = pos_map[diff][len(used)]
            options = build_options(correct_text, distractors, correct_pos)

            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "6.NR.2.1",
                "difficulty": diff,
                "verifier_type": "statistical_center",
                "template_id": template_id,
                "params": params,
                "stem": stem_text,
                "expression": f"{target}({data_str})",
                "options": options,
                "correct_index": correct_pos,
                "answer": correct_text,
                "hint": _hint(diff, target),
                "explanation": expl,
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
            global_q_idx += 1
        questions.extend(used)
    return questions
