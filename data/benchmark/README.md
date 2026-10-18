# SLAQL Benchmark Dataset

**104** natural-language → SLAQL pairs for evaluating query generation.

Rewritten from a curated SOC analyst query set (`Dataset_pql_v4`, 104 hand-written references) into the public **SIEM Log Analytics Query Language (SLAQL)** used in this repository.

## Files to place here

| File | Description |
|------|-------------|
| `Dataset_slaql_v1.tsv` | Compact table: suffix, English question, SLAQL query |
| `Dataset_slaql_v1.csv` | Full CSV (includes Persian question + original query lineage) |
| `Dataset_slaql_v1_full.json` | Full JSON dump |

These files are generated and ready in the project workspace (`artifacts/benchmark/`). Copy them into this folder and push:

```bash
# from repo root — adjust path if needed
cp /path/to/artifacts/benchmark/Dataset_slaql_v1.* data/benchmark/
cp /path/to/artifacts/benchmark/*_by_model.jpg docs/figures/

git add data/benchmark/ docs/figures/
git commit -m "Add full SLAQL benchmark (104) and evaluation charts"
git push
```

## Columns (full JSON / CSV)

| Column | Description |
|--------|-------------|
| `suffix` | Example ID (1–104) |
| `question_en` | English natural-language question |
| `question_fa` | Original Persian question (reference) |
| `query_slaql` | Target SLAQL query |
| `query_pql_original` | Original domain query (lineage only; not used at runtime) |

## Conversion notes

| Legacy concept | SLAQL mapping |
|----------------|---------------|
| `from -1H` / `-1D` | `from last 1h` / `from last 24h` |
| `filter` | `where` |
| `aggregate count(*) as cnt by X` | `stats count() by X` |
| `distinctcount(f)` | `count_distinct(f)` |
| `sourceip`, `destinationip`, `destinationport` | `source_ip`, `dest_ip`, `dest_port` |
| `username`, `processname`, `host` | `user`, `process`, `hostname` |
| `signature` / `tag` | `rule_name` |
| `action=="failure"` | `action == "blocked"` |
| `having cnt > N` after aggregate | `\| where count > N` after `stats` |

## Relation to `data/demo/`

`data/demo/` (10 examples) is a hand-picked subset for quick CLI demos.  
This benchmark (104) is the full evaluation set used in the model × configuration study documented in `docs/evaluation.md`.
