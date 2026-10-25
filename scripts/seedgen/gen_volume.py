"""Generator for g5-volume. l*w*h."""
import random
from . import get_correct_position, build_options, get_distractors, fmt_num

TOPIC = "g5-volume"

STEMS = {
    "easy": [
        ("food",   "A lunch box is {l} cm long, {w} cm wide, and {h} cm tall. What is its volume?"),
        ("sports", "A gym locker is {l} ft long, {w} ft wide, and {h} ft tall. What volume does it hold?"),
        ("school", "A pencil case is {l} cm long, {w} cm wide, and {h} cm deep. What is its volume?"),
        ("games",  "A toy chest is {l} cm long, {w} cm wide, and {h} cm high. What volume of toys can it hold?"),
        ("nature", "A fish tank is {l} cm long, {w} cm wide, and {h} cm high. What is its volume?"),
    ],
    "medium": [
        ("food",   "A cake mold is {l} inches long, {w} inches wide, and {h} inches deep. What is the volume of batter it can hold?"),
        ("sports", "A trophy base is {l} cm long, {w} cm wide, and {h} cm tall. Find its volume."),
        ("school", "A storage bin in the classroom is {l} cm long, {w} cm wide, and {h} cm tall. What is its volume?"),
        ("games",  "A game board box is {l} cm by {w} cm by {h} cm. What is the volume of the box?"),
        ("nature", "A flower pot (rectangular) is {l} cm long, {w} cm wide, and {h} cm deep. What volume of soil fits inside?"),
    ],
    "hard": [
        ("food",   "A refrigerator shelf is {l} cm long, {w} cm wide, and {h} cm high. It holds containers of 4 cubic cm each. How many containers fit?"),
        ("sports", "A swimming pool section is {l} m long, {w} m wide, and {h} m deep. A pump fills 6 cubic metres per minute. How many minutes to fill it?"),
        ("school", "A bookshelf cubby is {l} cm long, {w} cm wide, and {h} cm deep. Each book occupies 3 cubic cm. How many books fit?"),
        ("games",  "A dungeon room in a game is {l} units long, {w} units wide, and {h} units tall. What is the total volume?"),
        ("nature", "A rectangular pond is {l} m long, {w} m wide, and {h} m deep. Water evaporates at 2 cubic metres per hour. After 3 hours, how much water remains?"),
    ],
}

RULE_ORDER = ["added_the_sides","found_base_area_only","used_surface_area_formula","multiplied_two_sides_then_added_height","cubed_one_side"]

def _params(rng, diff):
    lo, hi = {"easy":(2,6),"medium":(4,10),"hard":(8,20)}[diff]
    for _ in range(200):
        l = rng.randint(lo, hi)
        w = rng.randint(lo, hi)
        h = rng.randint(lo, hi)
        # ensure not all equal (so cubed_one_side can apply)
        if l == w == h:
            continue
        return {"l": l, "w": w, "h": h}
    return {"l": 6, "w": 6, "h": 4}

def _explanation(p, correct):
    l, w, h = p["l"], p["w"], p["h"]
    base = l * w
    return (f"Volume = length x width x height. "
            f"First multiply length x width: {l} x {w} = {base}. "
            f"Then multiply by height: {base} x {h} = {correct} cubic units.")

def _hint(p):
    return f"Volume needs all three dimensions multiplied together — length, width, and height."

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
            correct = p["l"] * p["w"] * p["h"]
            correct_text = fmt_num(correct)
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
                "hint": _hint(p),
                "explanation": _explanation(p, correct_text),
                "provenance": "verified",
                "model": "template-seed",
                "prompt_version": "seed-v2",
            }
            used.append(q)
            q_index += 1
        questions.extend(used)
    return questions
