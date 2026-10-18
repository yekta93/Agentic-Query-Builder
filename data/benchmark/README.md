# SLAQL Benchmark Dataset

**104** natural-language → SLAQL pairs for evaluating query generation.

Derived from a curated SOC analyst query set and rewritten for the public
**SIEM Log Analytics Query Language (SLAQL)** schema used in this repository.

## Files

| File | Description |
|------|-------------|
| `Dataset_slaql_v1.csv` | Main table (suffix, questions, SLAQL, original PQL reference) |
| `Dataset_slaql_v1.json` | Same data as JSON |

## Columns

| Column | Description |
|--------|-------------|
| `suffix` | Example ID (1–104) |
| `question_en` | English natural-language question |
| `question_fa` | Original Persian question (reference) |
| `query_slaql` | Target SLAQL query |
| `query_pql_original` | Original domain query (for lineage only; not used at runtime) |

## Notes

- Field names and syntax follow `artifacts/fields.md` and `artifacts/slaql_syntax.md`.
- Some legacy concepts (e.g. sensor diversity) are mapped onto SLAQL fields such as `event_type` / `rule_name`.
- The small `data/demo/` set (10 examples) is a hand-picked subset for quick demos; this benchmark is the full evaluation set.
