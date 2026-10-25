"""Shared seedgen utilities."""
import sys, os, random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fractions import Fraction
from math import lcm
from typing import Optional, Dict, List

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

# Balanced correct-position sequence: 18 positions
# 5 zeros, 4 ones, 5 twos, 4 threes -> max count is 5/18 = 27.8% (well <= 35%)
BASE_BALANCED_POSITIONS = [0, 1, 2, 3, 1, 0, 3, 2, 2, 3, 0, 1, 3, 0, 1, 2, 0, 2]

def get_topic_positions(topic_id: str, seed: int = 42) -> Dict[str, List[int]]:
    """Offset by hash of topic_id and shuffle within each difficulty bucket.
    Guarantees every position is <= 35% (max 27.8%) and different question letters across topics.
    """
    offset = sum(ord(c) * (k + 1) for k, c in enumerate(topic_id)) % len(BASE_BALANCED_POSITIONS)
    shifted = BASE_BALANCED_POSITIONS[offset:] + BASE_BALANCED_POSITIONS[:offset]

    easy_pool = shifted[0:6]
    med_pool = shifted[6:12]
    hard_pool = shifted[12:18]

    rng = random.Random(seed + offset * 37)
    rng.shuffle(easy_pool)
    rng.shuffle(med_pool)
    rng.shuffle(hard_pool)

    return {
        "easy": easy_pool,
        "medium": med_pool,
        "hard": hard_pool,
    }

def build_options(correct_text: str, distractors: list, correct_pos: int):
    """Insert correct answer at correct_pos among the first 4 slots.
    Stores id, text, and misconception_id (null for correct answer).
    Duplicate legacy 'misconception' field is dropped.
    """
    ids = ["A", "B", "C", "D"]
    opts = []
    dist_iter = iter(distractors[:3])
    for i in range(4):
        if i == correct_pos:
            opts.append({"id": ids[i], "text": correct_text, "misconception_id": None})
        else:
            d = next(dist_iter, None)
            if d is None:
                break
            opts.append({"id": ids[i], "text": d["text"], "misconception_id": d["rule_id"]})
    return opts

def get_distractors(topic_id: str, params: dict, correct_text: str, rule_order: list):
    """Return up to 3 valid distractor dicts using rule_order preference."""
    from api._lib.misconceptions import RULES, apply_rule, load_registry
    from api._lib.verifier import normalize_option
    registry = load_registry()
    seen_texts = {correct_text}
    norm_c, _ = normalize_option(correct_text)
    seen_norms = {norm_c}
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
        if text is None:
            continue
        norm_t, _ = normalize_option(text)
        if text in seen_texts or norm_t in seen_norms or rule_id in used_rules:
            continue
        seen_texts.add(text)
        seen_norms.add(norm_t)
        used_rules.add(rule_id)
        entry = registry.get(rule_id, {})
        result.append({"rule_id": rule_id, "text": text, "kid_label": entry.get("kid_label", "")})
        if len(result) == 3:
            break
    return result
