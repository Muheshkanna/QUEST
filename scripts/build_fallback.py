#!/usr/bin/env python3
"""Build the static fallback assets for the offline demo.

This script copies the deterministic JSON bank, lessons, infographics, and
explainers into ``app/public/fallback/`` so that the web app can serve content
without contacting any LLM service.
"""
import shutil
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_DIRS = [
    PROJECT_ROOT / "data" / "bank",
    PROJECT_ROOT / "data" / "lessons",
    PROJECT_ROOT / "data" / "infographics",
    PROJECT_ROOT / "data" / "explainers",
]

TARGET_ROOT = PROJECT_ROOT / "app" / "public" / "fallback"

def ensure_target():
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

def copy_dir(src: Path):
    dest = TARGET_ROOT / src.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print(f"Copied {src} -> {dest}")

def main():
    ensure_target()
    for src in SOURCE_DIRS:
        if src.is_dir():
            copy_dir(src)
        else:
            print(f"Warning: source directory missing: {src}")

if __name__ == "__main__":
    main()
