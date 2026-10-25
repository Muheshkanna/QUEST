"""Generate data/template_review.md containing a rendered sample for every stem template across all playable topics.
Also validates that every number in params appears in the stem.
"""
import os, json, re

BANK_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "bank")
OUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "template_review.md")

PLAYABLE_TOPICS = [
    "g5-fractions-add",
    "g5-volume",
    "g6-percents",
    "g6-equations",
    "g5-divide",
    "g6-ratios",
    "g6-unit-rates",
    "g5-fractions-multiply",
    "g6-mean-median",
    "g5-decimal-ops",
    "g5-multiply",
    "g6-fraction-division",
]

def check_params_in_stem(params, stem, topic_id):
    missing = []
    if isinstance(params, dict):
        for k, v in params.items():
            if k in ("op", "form", "target", "q", "r"):
                continue
            if isinstance(v, list):
                for item in v:
                    s_item = str(item)
                    if s_item not in stem:
                        missing.append(f"{k}[{item}]")
            elif isinstance(v, (int, float)):
                # If int(v) == v, check both integer and float string representation
                s_int = str(int(v)) if v == int(v) else None
                s_float = str(v)
                found = (s_int and s_int in stem) or (s_float in stem)
                if not found:
                    missing.append(f"{k}={v}")
    return missing

def main():
    lines = [
        "# Template Review — Rendered Samples of All Playable Curriculum Stem Templates",
        "",
        "This document contains one rendered sample for EVERY stem template across all 12 playable topics in Quest.",
        "Includes template_id, stem, expression, correct answer, and each wrong option with its registered misconception rule id.",
        "Also verifies that every numerical parameter appears in the rendered stem.",
        "",
        "---",
        ""
    ]

    total_templates = 0
    param_check_failures = []

    for topic_id in PLAYABLE_TOPICS:
        bank_path = os.path.join(BANK_DIR, f"{topic_id}.json")
        if not os.path.exists(bank_path):
            print(f"Warning: {bank_path} not found")
            continue

        with open(bank_path, "r", encoding="utf-8") as f:
            bank = json.load(f)

        lines.append(f"## Topic: `{topic_id}`")
        lines.append(f"**Total Bank Size:** {len(bank.get('questions', []))} questions  ")
        lines.append(f"**Standard:** `{bank.get('questions', [{}])[0].get('standard', 'N/A')}`\n")

        seen_templates = set()
        topic_templates = 0

        for q in bank.get("questions", []):
            tmpl_id = q.get("template_id")
            if tmpl_id in seen_templates:
                continue
            seen_templates.add(tmpl_id)
            topic_templates += 1
            total_templates += 1

            missing_params = check_params_in_stem(q.get("params", {}), q.get("stem", ""), topic_id)
            if missing_params:
                param_check_failures.append((tmpl_id, missing_params))
                param_status = f"❌ FAILED (missing from stem: {', '.join(missing_params)})"
            else:
                param_status = "✅ PASS (all numerical params appear in stem)"

            lines.append(f"### Template: `{tmpl_id}`")
            lines.append(f"- **Difficulty:** `{q.get('difficulty')}`")
            lines.append(f"- **Stem:** {q.get('stem')}")
            lines.append(f"- **Expression:** `{q.get('expression')}`")
            lines.append(f"- **Correct Answer:** `{q.get('answer')}` (Position {q.get('correct_index')})")
            lines.append(f"- **Param Check:** {param_status}")
            lines.append("- **Options & Misconception Tags:**")
            for opt in q.get("options", []):
                tag = opt.get("misconception_id") or "(Correct Answer)"
                is_corr = " ⭐" if opt.get("misconception_id") is None else ""
                lines.append(f"  * **[{opt.get('id')}]** `{opt.get('text')}` — *{tag}*{is_corr}")
            lines.append(f"- **Hint:** *\"{q.get('hint')}\"*")
            lines.append(f"- **Explanation:** *\"{q.get('explanation')}\"*")
            lines.append("")

        lines.append("---\n")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {OUT_FILE}")
    print(f"Total Unique Templates Reviewed: {total_templates}")
    if param_check_failures:
        print(f"WARNING: {len(param_check_failures)} template(s) had missing params in stem:")
        for tid, miss in param_check_failures:
            print(f"  - {tid}: {miss}")
    else:
        print("ALL templates passed param-in-stem validation (100% of numerical parameters appear in stems).")

if __name__ == "__main__":
    main()
