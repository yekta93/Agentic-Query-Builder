# Sample Outputs

This folder stores pipeline run results.

## Committed demo samples

`demo_candidate_0/` contains **sample outputs** for all 10 demo examples under configuration candidate 0 (full pipeline: few-shots + syntax check + reflect).

Structure (same layout as production runs):

```text
demo_candidate_0/
├── metadata.json
├── syntax_result/result_{id}.json
├── evaluation/evaluation_{id}.json
├── execution_result/execution_result_{id}.json
└── result_{id}.json          # combined snapshot
```

These files were generated in **demo mode** (reference queries + mocked execution) so the repository can showcase the full output shape without a live SIEM or API key.

## Live runs

When you run `python main.py`, new timestamped folders are created:

```text
{YYYY-MM-DD_HH-MM-SS}_candidate_{N}/
```

Those live folders are gitignored; only `demo_candidate_0/` is kept in the repo.

## Dataset-wide execute results

See also `data/execute_result/result00N.json` for mocked execute-node outputs for every demo record.
