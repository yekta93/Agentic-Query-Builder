#!/usr/bin/env python3
"""Combine data/benchmark/parts/*.json into full dataset files."""
from __future__ import annotations

import csv
import json
from pathlib import Path

BENCH = Path(__file__).resolve().parents[1] / "data" / "benchmark"
PARTS = BENCH / "parts"


def main() -> None:
    files = sorted(PARTS.glob("part_*.json"))
    if not files:
        raise SystemExit(f"No part_*.json under {PARTS}")

    rows: list[dict] = []
    for f in files:
        rows.extend(json.loads(f.read_text(encoding="utf-8")))
    rows.sort(key=lambda r: int(r["suffix"]))
    print(f"Loaded {len(rows)} rows from {len(files)} parts")

    full_path = BENCH / "Dataset_slaql_v1_full.json"
    full_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {full_path}")

    tsv_path = BENCH / "Dataset_slaql_v1.tsv"
    lines = ["suffix\tquestion_en\tquery_slaql"]
    for r in rows:
        q = r["query_slaql"].replace("\n| ", " | ").replace("\n", " ").replace("\t", " ")
        en = r["question_en"].replace("\t", " ").replace("\n", " ")
        lines.append(f"{r['suffix']}\t{en}\t{q}")
    tsv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {tsv_path}")

    csv_path = BENCH / "Dataset_slaql_v1.csv"
    fields = ["suffix", "question_en", "question_fa", "query_slaql", "query_pql_original"]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
