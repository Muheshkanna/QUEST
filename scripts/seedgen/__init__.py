"""Shared seedgen utilities."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fractions import Fraction
from math import lcm
from typing import Optional

def fmt_frac(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"

def fmt_num(v) -> str:
    if isinstance(v, float):
        if v == int(v):
            return str(int(v))
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return s
    return str(int(v)) if float(v) == int(float(v)) else str(v)

# Balanced correct-position sequence: 18 positions cycling through [0,1,2,3]
# so each position appears 4 or 5 times; no position > 35%
BALANCED_POSITIONS = [0, 1, 2, 3, 1, 0, 3, 2, 2, 3, 0, 1, 3, 0, 1, 2, 0, 2]

def get_correct_position(q_index: int) -> int:
    return BALANCED_POSITIONS[q_index % len(BALANCED_POSITIONS)]

def build_options(correct_text: str, distractors: list, correct_pos: int):
    """Insert correct answer at correct_pos among the first 4 slots."""
    ids = ["A", "B", "C", "D"]
    opts = []
    dist_iter = iter(distractors[:3])
    for i in range(4):
        if i == correct_pos:
            opts.append({"id": ids[i], "text": correct_text, "misconception": None, "misconception_id": None})
        else:
            d = next(dist_iter, None)
            if d is None:
                break
            opts.append({"id": ids[i], "text": d["text"], "misconception": d["rule_id"], "misconception_id": d["rule_id"]})
    return opts

def get_distractors(topic_id: str, params: dict, correct_text: str, rule_order: list):
    """Return up to 3 valid distractor dicts using rule_order preference."""
    from api._lib.misconceptions import RULES, apply_rule, load_registry
    registry = load_registry()
    seen_texts = {correct_text}
    result = []
    used_rules = set()
    for rule_id in rule_order:
        if rule_id not in RULES:
            continue
        fn, applies_fn, topics = RULES[rule_id]
        if topic_id not in topics:
            continue
        if not applies_fn(params):
            continue
        text = apply_rule(rule_id, params)
        if text is None or text in seen_texts or rule_id in used_rules:
            continue
        seen_texts.add(text)
        used_rules.add(rule_id)
        entry = registry.get(rule_id, {})
        result.append({"rule_id": rule_id, "text": text, "kid_label": entry.get("kid_label","")})
        if len(result) == 3:
            break
    return result
