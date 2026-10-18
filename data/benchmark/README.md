# SLAQL Benchmark Dataset

**104** natural-language → SLAQL pairs for evaluating query generation.

## Layout

```text
data/benchmark/
├── questions/          # 1.txt … 104.txt  (English questions)
├── queries/            # 1.txt … 104.txt  (reference SLAQL)
├── Dataset_slaql_v1.tsv
├── Dataset_slaql_v1.csv
└── README.md
```

Rebuild the table files after any edit:

```bash
python scripts/combine_benchmark.py
```

## Counts

| Asset | Count |
|-------|------|
| Question files | **104** |
| Query files | **104** |

## Source

Adapted from a curated 104-query SOC analyst set and rewritten into public **SLAQL** syntax (`artifacts/slaql_syntax.md`).

Evaluation study (model × configuration accuracy/cost): see `docs/evaluation.md`.
