#!/usr/bin/env python3
"""Audit inventory for the QUEST project.

This script checks the presence and basic completeness of the key deliverables
required by the 7‑step plan.  It prints a markdown table with one row per
deliverable and a status column: **DONE**, **PARTIAL**, or **MISSING**.

The script is deliberately lightweight – it does not import any project code
so it can be run in a clean environment.
"""
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def exists(path: Path) -> bool:
    return path.exists()

def count_json_files(dir_path: Path) -> int:
    if not dir_path.is_dir():
        return 0
    return sum(1 for p in dir_path.iterdir() if p.suffix == ".json")

def load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Define the inventory items we care about
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

inventory = [
    {
        "name": "scripts/seed_bank.py",
        "path": PROJECT_ROOT / "scripts" / "seed_bank.py",
    },
    {
        "name": "data/bank/<topic_id>.json (20 topics, >=6 questions per difficulty)",
        "path": PROJECT_ROOT / "data" / "bank",
        "check": "bank",
    },
    {
        "name": "data/lessons/<topic_id>.json (20 topics)",
        "path": PROJECT_ROOT / "data" / "lessons",
        "check": "lessons",
    },
    {
        "name": "data/infographics/ and data/explainers/ for g5-fractions-add, g6-ratios, g5-volume",
        "path": PROJECT_ROOT / "data",
        "check": "infographics_explainers",
    },
    {
        "name": "scripts/build_fallback.py",
        "path": PROJECT_ROOT / "scripts" / "build_fallback.py",
    },
    {
        "name": "app/public/fallback/ (populated)",
        "path": PROJECT_ROOT / "app" / "public" / "fallback",
    },
    {
        "name": "prompts/v1 and prompts/v2 (lesson.md, questions.md, infographic.md, explainer.md)",
        "path": PROJECT_ROOT / "prompts",
        "check": "prompts",
    },
    {
        "name": "api/_lib/llm.py (GeminiClient, GroqClient, MockClient)",
        "path": PROJECT_ROOT / "api" / "_lib" / "llm.py",
    },
]

# ---------------------------------------------------------------------------
# Perform checks
# ---------------------------------------------------------------------------
rows = []
for item in inventory:
    name = item["name"]
    path = item["path"]
    status = "MISSING"
    details = ""
    if "check" not in item:
        status = "DONE" if exists(path) else "MISSING"
    else:
        chk = item["check"]
        if chk == "bank":
            if exists(path) and path.is_dir():
                json_files = [p for p in path.iterdir() if p.suffix == ".json"]
                # Expect 20 topics and at least 18 questions per file (6 per difficulty)
                missing = []
                for jf in json_files:
                    try:
                        data = json.load(open(jf, "r", encoding="utf-8"))
                        qcount = len(data.get("questions", []))
                        if qcount < 18:
                            missing.append(f"{jf.name}:{qcount}")
                    except Exception:
                        missing.append(jf.name)
                if len(json_files) >= 20 and not missing:
                    status = "DONE"
                elif json_files:
                    status = "PARTIAL"
                    details = f"{len(json_files)} files, issues: {', '.join(missing[:3])}"
                else:
                    status = "MISSING"
            else:
                status = "MISSING"
        elif chk == "lessons":
            if exists(path) and path.is_dir():
                json_files = [p for p in path.iterdir() if p.suffix == ".json"]
                if len(json_files) >= 20:
                    status = "DONE"
                else:
                    status = "PARTIAL"
                    details = f"{len(json_files)} lesson files"
            else:
                status = "MISSING"
        elif chk == "infographics_explainers":
            required = ["g5-fractions-add", "g6-ratios", "g5-volume"]
            missing = []
            for topic in required:
                inf_path = PROJECT_ROOT / "data" / "infographics" / f"{topic}.json"
                expl_path = PROJECT_ROOT / "data" / "explainers" / f"{topic}.json"
                if not (inf_path.is_file() and expl_path.is_file()):
                    missing.append(topic)
            if not missing:
                status = "DONE"
            else:
                status = "MISSING"
                details = f"missing: {', '.join(missing)}"
        elif chk == "prompts":
            v1 = PROJECT_ROOT / "prompts" / "v1"
            v2 = PROJECT_ROOT / "prompts" / "v2"
            needed = ["lesson.md", "questions.md", "infographic.md", "explainer.md"]
            def has_all(p):
                return all((p / f).is_file() for f in needed)
            if v1.is_dir() and v2.is_dir() and has_all(v1) and has_all(v2):
                status = "DONE"
            else:
                status = "MISSING"
                missing_parts = []
                if not v1.is_dir():
                    missing_parts.append("v1 missing")
                else:
                    missing_parts.append("v1 missing files" if not has_all(v1) else "")
                if not v2.is_dir():
                    missing_parts.append("v2 missing")
                else:
                    missing_parts.append("v2 missing files" if not has_all(v2) else "")
                details = ", ".join([p for p in missing_parts if p])
        else:
            status = "UNKNOWN"
    rows.append((name, status, details))

# ---------------------------------------------------------------------------
# Print markdown table
# ---------------------------------------------------------------------------
print("| Deliverable | Status | Details |")
print("|---|---|---|")
for name, status, details in rows:
    print(f"| {name} | {status} | {details} |")

# Exit with non‑zero code if any MISSING items (useful for CI)
if any(status == "MISSING" for _, status, _ in rows):
    sys.exit(1)
else:
    sys.exit(0)
