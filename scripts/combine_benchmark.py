#!/usr/bin/env python3
"""Rebuild Dataset_slaql_v1.tsv/csv from questions/ and queries/ folders (104 pairs)."""
from __future__ import annotations

import csv
from pathlib import Path

BENCH = Path(__file__).resolve().parents[1] / "data" / "benchmark"
QDIR = BENCH / "questions"
RDIR = BENCH / "queries"


def main() -> None:
    ids = sorted(int(p.stem) for p in QDIR.glob("*.txt"))
    if not ids:
        raise SystemExit(f"No questions under {QDIR}")

    rows = []
    for i in ids:
        q = (QDIR / f"{i}.txt").read_text(encoding="utf-8").strip()
        slaql = (RDIR / f"{i}.txt").read_text(encoding="utf-8").strip()
        rows.append({"suffix": i, "question_en": q, "query_slaql": slaql})

    print(f"Loaded {len(rows)} pairs")

    tsv = BENCH / "Dataset_slaql_v1.tsv"
    lines = ["suffix\tquestion_en\tquery_slaql"]
    for r in rows:
        qline = r["query_slaql"].replace("\n", " | ")
        lines.append(f"{r['suffix']}\t{r['question_en']}\t{qline}")
    tsv.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {tsv}")

    csv_path = BENCH / "Dataset_slaql_v1.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["suffix", "question_en", "query_slaql"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
