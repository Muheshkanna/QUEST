"""Generator for g5-volume. l*w*h."""
import random
from . import get_topic_positions, build_options, get_distractors, fmt_num

TOPIC = "g5-volume"

STEMS = {
    "easy": [
        ("food",   "A lunch box is {l} cm long, {w} cm wide, and {h} cm tall. What is its volume?", "cm"),
        ("sports", "A gym locker is {l} ft long, {w} ft wide, and {h} ft tall. What volume does it hold?", "ft"),
        ("school", "A pencil case is {l} cm long, {w} cm wide, and {h} cm deep. What is its volume?", "cm"),
        ("games",  "A toy chest is {l} in long, {w} in wide, and {h} in high. What volume of toys can it hold?", "in"),
        ("nature", "A fish tank is {l} m long, {w} m wide, and {h} m high. What is its volume?", "m"),
    ],
    "medium": [
        ("food",   "A cake mold is {l} in long, {w} in wide, and {h} in deep. What volume of batter does it hold?", "in"),
        ("sports", "A trophy base is {l} cm long, {w} cm wide, and {h} cm tall. Find its volume.", "cm"),
        ("school", "A classroom storage bin is {l} cm long, {w} cm wide, and {h} cm tall. What is its volume?", "cm"),
        ("games",  "A game board box is {l} cm by {w} cm by {h} cm. What is the volume of the box?", "cm"),
        ("nature", "A rectangular flower planter is {l} ft long, {w} ft wide, and {h} ft deep. What is its volume?", "ft"),
    ],
    "hard": [
        ("food",   "A pantry crate is {l} cm long, {w} cm wide, and {h} cm tall. What is the total volume of the crate?", "cm"),
        ("sports", "A swimming pool section is {l} m long, {w} m wide, and {h} m deep. What is the total volume of water it can hold?", "m"),
        ("school", "A school supply crate is {l} in long, {w} in wide, and {h} in deep. What is its volume?", "in"),
        ("games",  "A game room is {l} ft long, {w} ft wide, and {h} ft high. What is the volume of the room?", "ft"),
        ("nature", "A rectangular pond is {l} m long, {w} m wide, and {h} m deep. What is the volume of the pond?", "m"),
    ],
}

UNIT_POW = {"cm": "cm³", "ft": "ft³", "in": "in³", "m": "m³"}

ALL_RULES = [
    "multiplied_two_sides_then_added_height",
    "cubed_one_side",
    "added_the_sides",
    "found_base_area_only",
    "used_surface_area_formula",
]

def _params(rng, diff):
    lo, hi = {"easy": (2, 6), "medium": (4, 10), "hard": (8, 20)}[diff]
    for _ in range(200):
        l = rng.randint(lo, hi)
        w = rng.randint(lo, hi)
        h = rng.randint(lo, hi)
        # ensure not all equal so cubed_one_side can apply
        if l == w == h:
            continue
        return {"l": l, "w": w, "h": h}
    return {"l": 6, "w": 5, "h": 4}

def _explanation(p, correct, unit):
    l, w, h = p["l"], p["w"], p["h"]
    base = l * w
    u = UNIT_POW.get(unit, f"{unit}³")
    return (f"Multiply the three measurements together: length, width, and height. "
            f"First find the base area: {l} × {w} = {base}. "
            f"Then multiply by height: {base} × {h} = {correct} {u}.")

def _hint(diff):
    if diff == "easy":
        return "Multiply all three measurements together: length, width, and height."
    elif diff == "medium":
        return "Think about how many layers tall this space is, and what size each layer has."
    else:
        return "Find the total space inside by combining all three dimensions."

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
            correct = p["l"] * p["w"] * p["h"]
            correct_text = fmt_num(correct)

            offset = global_q_idx % len(ALL_RULES)
            rule_order = ALL_RULES[offset:] + ALL_RULES[:offset]

            distractors = get_distractors(TOPIC, p, correct_text, rule_order)
            if len(distractors) < 3:
                continue

            ctx, tmpl, unit = stem_list[len(used) % len(stem_list)]
            template_id = f"{TOPIC}-{diff}-{ctx}"
            stem_text = tmpl.format(**p)
            correct_pos = pos_map[diff][len(used)]
            options = build_options(correct_text, distractors, correct_pos)

            q = {
                "id": f"{TOPIC}-{diff}-{len(used)+1}",
                "topic_id": TOPIC,
                "standard": "5.GSR.8.3",
                "difficulty": diff,
                "verifier_type": "volume_geometry",
                "template_id": template_id,
                "params": p,
                "stem": stem_text,
                "expression": f"{p['l']} * {p['w']} * {p['h']}",
                "options": options,
                "correct_index": correct_pos,
                "answer": correct_text,
                "hint": _hint(diff),
                "explanation": _explanation(p, correct_text, unit),
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
            global_q_idx += 1
        questions.extend(used)
    return questions
