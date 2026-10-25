#!/usr/bin/env python3
"""Build the static fallback assets for the offline demo.

This script bundles:
- topics.json (with computed `playable` flag and `content_source`)
- misconceptions.json (the misconception registry)
- data/bank (verified question banks)
- data/lessons (lessons)
- data/infographics (flagship infographics)
- data/explainers (flagship explainers)
into ``app/public/fallback/`` so that the web app and offline mode can function.
"""
import json
import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
TARGET_ROOT = PROJECT_ROOT / "app" / "public" / "fallback"


def compute_topic_playability():
    """Load data/topics.json, compute `playable` and `content_source` for each topic."""
    topics_file = DATA_DIR / "topics.json"
    with open(topics_file, "r", encoding="utf-8") as f:
        topics = json.load(f)

    bank_dir = DATA_DIR / "bank"
    bundled_topics = []

    for topic in topics:
        topic_id = topic["id"]
        bank_file = bank_dir / f"{topic_id}.json"

        is_playable = False
        content_source = "coming-soon"

        if bank_file.is_file():
            try:
                with open(bank_file, "r", encoding="utf-8") as bf:
                    bank_data = json.load(bf)
                questions = bank_data.get("questions", [])
                
                # Check: >= 9 verified questions, >= 3 per level, provenance verified
                easy_count = 0
                med_count = 0
                hard_count = 0
                verified_count = 0

                for q in questions:
                    prov = q.get("provenance")
                    diff = q.get("difficulty")
                    if prov == "verified":
                        verified_count += 1
                        if diff == "easy":
                            easy_count += 1
                        elif diff == "medium":
                            med_count += 1
                        elif diff == "hard":
                            hard_count += 1

                if (
                    len(questions) >= 9
                    and verified_count == len(questions)
                    and easy_count >= 3
                    and med_count >= 3
                    and hard_count >= 3
                ):
                    is_playable = True
                    content_source = "verified-bank"
                elif len(questions) > 0:
                    content_source = "partial-bank"
            except Exception as e:
                print(f"Error reading bank for {topic_id}: {e}")

        topic_entry = dict(topic)
        topic_entry["playable"] = is_playable
        topic_entry["content_source"] = content_source
        bundled_topics.append(topic_entry)

    out_topics_file = TARGET_ROOT / "topics.json"
    with open(out_topics_file, "w", encoding="utf-8") as f:
        json.dump(bundled_topics, f, indent=2)
    print(f"Bundled {len(bundled_topics)} topics (playable: {sum(1 for t in bundled_topics if t['playable'])}) -> {out_topics_file}")


def copy_file(src: Path, dest_name: str | None = None):
    dest = TARGET_ROOT / (dest_name or src.name)
    shutil.copy2(src, dest)
    print(f"Copied {src} -> {dest}")


def copy_dir(src: Path):
    dest = TARGET_ROOT / src.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print(f"Copied {src} -> {dest}")


def main():
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    # 1. Compute and bundle topics.json
    compute_topic_playability()

    # 2. Bundle misconceptions registry
    misc_file = DATA_DIR / "misconceptions.json"
    if misc_file.is_file():
        copy_file(misc_file)

    # 3. Bundle bank, lessons, infographics, explainers
    for folder_name in ["bank", "lessons", "infographics", "explainers"]:
        src_folder = DATA_DIR / folder_name
        if src_folder.is_dir():
            copy_dir(src_folder)
        else:
            print(f"Warning: source directory missing: {src_folder}")


if __name__ == "__main__":
    main()

