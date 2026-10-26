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
TARGET_ROOT_ALT = PROJECT_ROOT / "public" / "fallback"


def compute_topic_playability():
    """Load data/topics.json, compute `playable` and `content_source` for each topic."""
    topics_file = DATA_DIR / "topics.json"
    with open(topics_file, "r", encoding="utf-8") as f:
        topics = json.load(f)

    bank_dir = DATA_DIR / "bank"
    bundled_topics = []

    misc_file = DATA_DIR / "misconceptions.json"
    misc_map = {}
    if misc_file.is_file():
        with open(misc_file, "r", encoding="utf-8") as mf:
            for m in json.load(mf).get("misconceptions", []):
                if m.get("id"):
                    misc_map[m["id"]] = m

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

                easy_count = sum(1 for q in questions if q.get("difficulty") == "easy" and q.get("provenance") == "verified")
                med_count = sum(1 for q in questions if q.get("difficulty") == "medium" and q.get("provenance") == "verified")
                hard_count = sum(1 for q in questions if q.get("difficulty") == "hard" and q.get("provenance") == "verified")
                verified_count = sum(1 for q in questions if q.get("provenance") == "verified")

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

        derived_misc = []
        for mid in topic.get("misconceptions", []):
            if isinstance(mid, dict):
                derived_misc.append({"id": mid.get("id", mid.get("tag", "")), "kid_label": mid.get("kid_label", "")})
            else:
                entry = misc_map.get(mid, {})
                derived_misc.append({"id": mid, "kid_label": entry.get("kid_label", mid)})

        topic_entry = dict(topic)
        topic_entry["misconceptions"] = derived_misc
        topic_entry["playable"] = is_playable
        topic_entry["content_source"] = content_source
        bundled_topics.append(topic_entry)

    # Compute play_order per grade among playable topics
    for g in (5, 6):
        grade_topics = [t for t in bundled_topics if t["grade"] == g]
        grade_topics.sort(key=lambda x: x.get("unlock_order", 0))
        counter = 1
        for gt in grade_topics:
            if gt["playable"]:
                gt["play_order"] = counter
                counter += 1
            else:
                gt["play_order"] = None

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

    # 4. Mirror to public/fallback so Nuxt dev & generate serve it directly
    if TARGET_ROOT.is_dir():
        if TARGET_ROOT_ALT.exists():
            shutil.rmtree(TARGET_ROOT_ALT)
        shutil.copytree(TARGET_ROOT, TARGET_ROOT_ALT)
        print(f"Synced fallback bundle -> {TARGET_ROOT_ALT}")


if __name__ == "__main__":
    main()

