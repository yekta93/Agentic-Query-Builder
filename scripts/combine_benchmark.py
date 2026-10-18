#!/usr/bin/env python3
"""Rebuild Dataset_slaql_v1.tsv/csv from questions/ and queries/ (001-104)."""
from __future__ import annotations

import csv
from pathlib import Path

BENCH = Path(__file__).resolve().parents[1] / "data" / "benchmark"
QDIR = BENCH / "questions"
RDIR = BENCH / "queries"


def main() -> None:
    # Prefer zero-padded names (001.txt); ignore legacy unpadded (1.txt)
    files = sorted(
        p for p in QDIR.glob("*.txt") if len(p.stem) == 3 and p.stem.isdigit()
    )
    if not files:
        raise SystemExit(f"No zero-padded questions under {QDIR} (expected 001.txt ...)")

    rows = []
    for qp in files:
        stem = qp.stem  # e.g. 001
        rp = RDIR / f"{stem}.txt"
        if not rp.exists():
            print(f"WARNING: missing query for {stem}")
            continue
        rows.append({
            "suffix": stem,
            "question_en": qp.read_text(encoding="utf-8").strip(),
            "query_slaql": rp.read_text(encoding="utf-8").strip(),
        })

    print(f"Loaded {len(rows)} pairs (001-style)")

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
