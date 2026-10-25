"""Main runner: generate all 5 pilot banks and write to data/bank/."""
import sys, os, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.seedgen.gen_fractions_add import generate as gen_fractions
from scripts.seedgen.gen_volume import generate as gen_volume
from scripts.seedgen.gen_percents import generate as gen_percents
from scripts.seedgen.gen_equations import generate as gen_equations
from scripts.seedgen.gen_divide import generate as gen_divide

GENERATORS = {
    "g5-fractions-add": gen_fractions,
    "g5-volume": gen_volume,
    "g6-percents": gen_percents,
    "g6-equations": gen_equations,
    "g5-divide": gen_divide,
}

BANK_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "bank")

def run(seed: int = 42):
    os.makedirs(BANK_DIR, exist_ok=True)
    for topic_id, gen_fn in GENERATORS.items():
        questions = gen_fn(seed=seed)
        counts = {}
        for q in questions:
            d = q["difficulty"]
            counts[d] = counts.get(d, 0) + 1
        bank = {
            "topic_id": topic_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": "template-seed",
            "prompt_version": "seed-v2",
            "counts": counts,
            "questions": questions,
        }
        path = os.path.join(BANK_DIR, f"{topic_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(bank, f, indent=2, ensure_ascii=False)
        total = sum(counts.values())
        print(f"  {topic_id}: {total} questions {counts}")

if __name__ == "__main__":
    print("Generating pilot banks...")
    run()
    print("Done.")
