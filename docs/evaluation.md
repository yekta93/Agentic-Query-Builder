# Evaluation Results

This document summarizes **model × pipeline configuration** experiments run on the SLAQL query-generation benchmark
(`data/benchmark/Dataset_slaql_v1.*`, 104 natural-language → SLAQL pairs adapted from a curated SOC query set).

## Benchmark

| Property | Value |
|----------|--------|
| Size | 104 examples |
| Input | Natural language questions (English + original Persian reference) |
| Target | Hand-written **SLAQL** reference queries |
| Metric | Exact / semantic match accuracy against the reference query |
| Cost | Estimated API cost per configuration ($) |

The public repo includes the full SLAQL benchmark so others can reproduce offline evaluation logic.
Live LLM scores require API keys.

## Pipeline configurations (ablations)

| Code | Stages enabled |
|------|----------------|
| **Base** | Generate only |
| **FewShot** | Generate + few-shot examples |
| **Trans** | Translate + Generate |
| **Trans+FewShot** | Translate + FewShot |
| **SyntaxCheck** | Generate + syntax validation |
| **SyntaxCheck+Refl** | + reflection / retry loop |
| **SyntaxCheck+Refl+FewShot** | + few-shot |
| **SyntaxCheck+Refl+Trans** | + translate |
| **SyntaxCheck+Refl+Trans+FewShot** | full pipeline |
| **SyntaxCheck+Trans+FewShot** | without reflection |
| **Refl+Trans** | Reflect + Translate (no syntax gate) |
| **Refl+Trans+FewShot** | Reflect + Translate + FewShot |

## Accuracy by model (summary)

Reference baseline: **GPT-4.1-mini ≈ 60.3%**.

Notable results from the controlled study:

| Model | Strong configuration | Approx. accuracy | Notes |
|-------|----------------------|------------------|-------|
| **qwen3-30b-a3b-instruct-2507** | Refl+Trans+FewShot | **~80%** | Best single score in the study |
| **llama-4-maverick** | SyntaxCheck+Trans+FewShot | **~70%** | Strong open-model result |
| **gemma-4-31b-it** | Base / SyntaxCheck+Refl / Trans | **~60%** | Matches GPT-4.1-mini baseline |
| **gemma-4-26b-a4b-it** | Trans+FewShot | **~53%** | Benefits from few-shot + translate |
| **qwen3-coder-30b** | FewShot | **~40%** | Weaker on this task |
| **phi-4** | Refl+Trans / +FewShot | **~20–30%** | Underperforms on this benchmark |

![Accuracy by model and configuration](figures/accuracy_by_model.jpg)

*Figure: Accuracy across models and pipeline ablations. Green dashed line = GPT-4.1-mini baseline (60.3%).*

## Cost by model (summary)

Cost scales with the number of LLM calls (reflection retries, translate, judge) and model price.

| Observation | Detail |
|-------------|--------|
| Full pipeline is more expensive | SyntaxCheck+Refl+Trans+FewShot drives higher $ |
| Smaller models stay cheap | Sub-cent per query in most configs |
| Trade-off | qwen3-30b high accuracy config still low absolute $ |

![Cost by model and configuration](figures/cost_by_model.jpg)

*Figure: Estimated cost ($) per configuration and model.*

## Takeaways for the agentic design

1. **Reflection + few-shot** can lift mid-size models above a strong closed-model baseline (see qwen3-30b).
2. **Syntax checking alone** is not enough; combining it with reflection and few-shot is more reliable.
3. **Translate** helps when questions are non-English (original benchmark mixed Persian/English analyst questions).
4. **Cost–quality trade-off** is explicit: full multi-agent loops cost more but can unlock higher accuracy on harder items.

## Reproducing

```bash
# Offline: inspect the benchmark
head -n 5 data/benchmark/Dataset_slaql_v1.csv

# Online (requires API keys): run the agentic pipeline on selected suffixes
python main.py --suffix 1
python main.py --suffix all --candidate-index 0
```

Evaluation scores in the charts were produced with the full experimental harness against the 104-query set;
the public CLI focuses on the demo + benchmark assets for transparency.
