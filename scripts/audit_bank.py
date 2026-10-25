#!/usr/bin/env python3
"""Audit question banks for provenance and rule compliance.
Reports:
- Per-topic misconception tag usage counts
- Answer position distribution per topic (fail if any > 35%)
- Question count per difficulty level
- Verification & provenance status (fail if not verified)
Exits with non-zero status on any failure.
"""
import json, os, sys
from collections import Counter, defaultdict

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from api._lib.verifier import verify_question

PILOT_TOPICS = [
    "g5-fractions-add",
    "g5-volume",
    "g6-percents",
    "g6-equations",
    "g5-divide",
]

def load_bank(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def audit(topics=None):
    bank_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "bank"))
    if not topics:
        topics = PILOT_TOPICS

    target_files = []
    for t in topics:
        fname = t if t.endswith(".json") else f"{t}.json"
        fpath = os.path.join(bank_dir, fname)
        if os.path.exists(fpath):
            target_files.append((fname, fpath))
        else:
            print(f"Warning: bank file not found: {fpath}")

    failures = []
    tag_usage = defaultdict(Counter)
    answer_positions = defaultdict(Counter)
    level_counts = defaultdict(Counter)
    verified_counts = defaultdict(int)
    total_questions = defaultdict(int)

    for fname, bank_path in target_files:
        bank = load_bank(bank_path)
        topic = bank.get("topic_id", fname.replace(".json", ""))

        for q in bank.get("questions", []):
            total_questions[topic] += 1
            result = verify_question(q)
            if not result.passed:
                failures.append((q.get("id"), result.reasons))
            elif q.get("provenance") != "verified":
                failures.append((q.get("id"), [f"Provenance is '{q.get('provenance')}', expected 'verified'"]))
            else:
                verified_counts[topic] += 1

            for opt in q.get("options", []):
                tag = opt.get("misconception_id") or opt.get("misconception")
                if tag:
                    tag_usage[topic][tag] += 1

            correct_idx = q.get("correct_index")
            if correct_idx is not None:
                answer_positions[topic][correct_idx] += 1

            level = q.get("difficulty")
            if level:
                level_counts[topic][level] += 1

    print("=================================================================")
    print("                 BANK AUDIT REPORT: PILOT TOPICS                ")
    print("=================================================================\n")

    print("--- 1. Per-Level Question Counts ---")
    for topic in sorted(total_questions.keys()):
        counts = level_counts[topic]
        counts_str = ", ".join(f"{lvl}: {counts[lvl]}" for lvl in ["easy", "medium", "hard"] if lvl in counts)
        total = total_questions[topic]
        ver = verified_counts[topic]
        print(f"  {topic}: total={total} ({counts_str}) | verified={ver}/{total}")

    print("\n--- 2. Misconception Tag Usage per Topic ---")
    for topic in sorted(tag_usage.keys()):
        print(f"\n  Topic: {topic}")
        cnts = tag_usage[topic]
        for tag, ct in sorted(cnts.items(), key=lambda x: (-x[1], x[0])):
            print(f"    - {tag}: {ct}")

    print("\n--- 3. Answer Position Distribution per Topic ---")
    pos_failed = False
    for topic in sorted(answer_positions.keys()):
        cnts = answer_positions[topic]
        total = sum(cnts.values())
        print(f"\n  Topic: {topic} (total = {total}):")
        for pos in range(4):
            ct = cnts.get(pos, 0)
            perc = (ct / total * 100) if total else 0
            flag = " [FAIL > 35%]" if perc > 35.0 else " [OK]"
            print(f"    Position {pos} ({['A','B','C','D'][pos]}): {ct:2d} ({perc:5.1f}%){flag}")
            if perc > 35.0:
                failures.append((f"Position {pos} ({perc:.1f}%) exceeds 35% threshold in {topic}", []))
                pos_failed = True

    print("\n=================================================================")
    if failures:
        print(f"AUDIT FAILED with {len(failures)} issue(s):")
        for fid, reasons in failures:
            print(f"  * {fid}:")
            for r in reasons:
                print(f"      - {r}")
        print("=================================================================")
        return 1
    else:
        print("AUDIT PASSED: All 5 pilot topics fully verified with compliant distributions.")
        print("=================================================================")
        return 0

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--all" in sys.argv:
        bank_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "bank"))
        all_topics = [f.replace(".json", "") for f in os.listdir(bank_dir) if f.endswith(".json")]
        sys.exit(audit(all_topics))
    elif args:
        sys.exit(audit(args))
    else:
        sys.exit(audit(PILOT_TOPICS))
