"""Evaluate the current deterministic language detector and entity extractor on a small gold set.

Run from the repository root with: python scripts/evaluate_bilingual_nlp.py
The dataset is a starter benchmark, not a statistically representative study.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.nlp.entity_extractor import EntityExtractor
from backend.nlp.language_detector import LanguageDetector

DATASET = ROOT / "tests" / "evaluation" / "data" / "bilingual_entity_cases.jsonl"


def safe_equal(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) < 1e-6
    return a == b


def main() -> int:
    cases = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    language_correct = 0
    per_field = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    failures = []

    for case in cases:
        predicted_lang, confidence, mixed = LanguageDetector.detect(case["text"])
        language_correct += predicted_lang == case["language"]
        predicted_raw = EntityExtractor.extract_entities(case["text"])
        predicted = {key: item["value"] for key, item in predicted_raw.items()}
        expected = case["expected"]
        all_fields = set(expected) | set(predicted)
        case_errors = []
        for field in all_fields:
            stats = per_field[field]
            if field in expected and field in predicted and safe_equal(expected[field], predicted[field]):
                stats["tp"] += 1
            else:
                if field in predicted:
                    stats["fp"] += 1
                if field in expected:
                    stats["fn"] += 1
                if field in expected or field in predicted:
                    case_errors.append({"field": field, "expected": expected.get(field), "predicted": predicted.get(field)})
        if case_errors or predicted_lang != case["language"]:
            failures.append({"id": case["id"], "expected_language": case["language"], "predicted_language": predicted_lang, "language_confidence": confidence, "code_mixed": mixed, "entity_errors": case_errors})

    print(f"Cases: {len(cases)}")
    print(f"Language accuracy: {language_correct}/{len(cases)} = {language_correct / max(len(cases), 1):.1%}")
    print("\nEntity extraction by field (micro one-vs-rest over annotated attributes):")
    totals = {"tp": 0, "fp": 0, "fn": 0}
    for field in sorted(per_field):
        s = per_field[field]
        p = s["tp"] / (s["tp"] + s["fp"]) if s["tp"] + s["fp"] else 0.0
        r = s["tp"] / (s["tp"] + s["fn"]) if s["tp"] + s["fn"] else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        print(f"  {field:28s} P={p:.3f} R={r:.3f} F1={f1:.3f} (TP={s['tp']} FP={s['fp']} FN={s['fn']})")
        for key in totals:
            totals[key] += s[key]
    p = totals["tp"] / (totals["tp"] + totals["fp"]) if totals["tp"] + totals["fp"] else 0.0
    r = totals["tp"] / (totals["tp"] + totals["fn"]) if totals["tp"] + totals["fn"] else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    print(f"\nMicro precision={p:.3f} recall={r:.3f} F1={f1:.3f}")
    print(f"Cases with one or more mismatches: {len(failures)}")
    if failures:
        print("\nMismatch details:")
        print(json.dumps(failures, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
