# SLAQL Benchmark Dataset

**104** natural-language → SLAQL pairs for evaluating query generation.

## Layout

```text
data/benchmark/
├── questions/          # 001.txt … 104.txt  (English questions)
├── queries/            # 001.txt … 104.txt  (reference SLAQL)
├── Dataset_slaql_v1.tsv
├── Dataset_slaql_v1.csv
└── README.md
```

File names are **zero-padded** three digits: `001`, `002`, …, `104`.

Rebuild the table files after any edit:

```bash
python scripts/combine_benchmark.py
```

## Counts

| Asset | Count |
|-------|------|
| Question files (`001`–`104`) | **104** |
| Query files (`001`–`104`) | **104** |

## Source

Adapted from a curated 104-query SOC analyst set and rewritten into public **SLAQL** syntax (`artifacts/slaql_syntax.md`).

Evaluation study: `docs/evaluation.md`.

> Note: legacy unpadded files (`1.txt`, `2.txt`, …) may still exist from an earlier commit; only `001.txt`–`104.txt` are canonical.
