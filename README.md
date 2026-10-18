# Agentic Query Builder

**An agentic multi-agent system that converts natural language questions into structured SIEM Log Analytics queries using LangGraph.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

Agentic Query Builder is a production-oriented multi-agent pipeline that translates natural language questions into precise **SIEM Log Analytics Query Language (SLAQL)** queries.

It demonstrates modern LLM orchestration patterns:

- **Multi-agent workflow** orchestrated with LangGraph
- **Few-shot learning** with curated examples
- **Syntax validation** loop
- **Self-reflection** + retry for query improvement
- **LLM-as-Judge** evaluation (with strong heuristic fallback)
- **Langfuse tracing** for every graph node (optional)
- Configurable pipeline stages (easy ablation studies)
- **104-example SLAQL benchmark** + model/config evaluation study

---

## Architecture

![LangGraph Architecture](https://raw.githubusercontent.com/yekta93/Generate-Query-Language/main/src/graph.png)

*LangGraph multi-agent pipeline: Generate → Syntax Check → Reflect (retry loop) → Judge → Execute*

### Pipeline Stages

| Stage            | Description                                      | Configurable |
|------------------|--------------------------------------------------|--------------|
| **Translate**    | Optional translation of the input question       | Yes          |
| **Generate**     | LLM generates SLAQL query using few-shot examples| Always on    |
| **Syntax Check** | Validates generated query against SLAQL rules    | Yes          |
| **Reflect**      | Analyzes errors and feeds guidance back to Generate | Yes       |
| **Judge**        | Final quality evaluation (LLM-as-judge or heuristic) | Always on |
| **Execute**      | Runs the query (mocked in public demo)           | Always on    |

---

## Evaluation Results

We evaluated **multiple open models** across **pipeline ablations** (Base, FewShot, Reflect, SyntaxCheck, Translate, and combinations) on a **104-query SLAQL benchmark**.

Reference baseline: **GPT-4.1-mini ≈ 60.3% accuracy**.

### Highlights

| Model | Strong configuration | Accuracy (approx.) |
|-------|----------------------|--------------------|
| qwen3-30b-a3b-instruct-2507 | Refl+Trans+FewShot | **~80%** |
| llama-4-maverick | SyntaxCheck+Trans+FewShot | **~70%** |
| gemma-4-31b-it | Base / SyntaxCheck+Refl | **~60%** (matches baseline) |
| gemma-4-26b-a4b-it | Trans+FewShot | **~53%** |

![Accuracy by model](docs/figures/accuracy_by_model.jpg)

![Cost by model](docs/figures/cost_by_model.jpg)

**Takeaways:** reflection + few-shot can push mid-size models above a strong closed baseline; full multi-agent loops trade higher cost for better accuracy on hard items.

Full write-up: **[docs/evaluation.md](docs/evaluation.md)**  
Benchmark data: **[data/benchmark/](data/benchmark/)** (104 NL → SLAQL pairs)

---

## Demo Mode (no API key required)

The repository ships with a fully functional **offline demo mode**:

- If `OPENROUTER_API_KEY` is **not** set, the Generate node automatically returns the curated reference query for that example.
- Judge falls back to a strong heuristic scorer.
- Reflect uses a deterministic feedback message.
- Execute always returns a realistic mocked result.

```bash
python main.py --suffix 1
python main.py --suffix all
```

---

## Observability (Langfuse)

Every LangGraph node can be traced with [Langfuse](https://langfuse.com).

```bash
pip install langfuse   # or: pip install -e ".[observability]"
```

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

Each `(candidate, suffix)` becomes one **session** in Langfuse with spans for generate / syntax_check / reflect / judge / execute.

---

## SIEM Log Analytics Query Language (SLAQL)

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | datetime | Event time |
| `source_ip` / `dest_ip` | string | IPs |
| `dest_port` | int | Destination port |
| `user` | string | Username |
| `event_type` | string | login, malware, firewall, dns, … |
| `severity` | string | low / medium / high / critical |
| `action` | string | allowed / blocked / quarantined |
| `hostname` / `process` | string | Host / process |
| `bytes_in` / `bytes_out` | int | Traffic volume |
| `rule_name` | string | Security rule |
| `country` | string | Source country |
| `query` | string | DNS / request content |

### Example

```text
from last 24h
| where event_type == "login" and severity == "high"
| stats count() by user, source_ip
| sort count desc
```

---

## Quick Start

```bash
git clone https://github.com/yekta93/Agentic-Query-Builder.git
cd Agentic-Query-Builder
pip install -e .
cp .env.example .env   # optional API keys

python main.py --suffix 1
python main.py --suffix all --candidate-index 0
```

---

## Configuration

Pipeline ablations are defined in `config.yaml` as **candidates** (model + enabled stages) for fair comparison.

---

## Project Structure

```text
├── main.py
├── config.yaml
├── src/                    # LangGraph + agents
├── utils/                  # LLM client, Langfuse, helpers
├── data/
│   ├── demo/               # 10 quick demo examples
│   ├── benchmark/          # 104-example SLAQL evaluation set
│   ├── output/             # run artifacts
│   └── execute_result/
├── docs/
│   ├── evaluation.md       # full evaluation write-up
│   └── figures/            # accuracy & cost charts
└── artifacts/              # SLAQL syntax & field guides
```

---

## Key Features for Portfolio

- LangGraph multi-agent orchestration with reflection loops
- Configurable ablations (few-shot, syntax check, reflect, translate)
- 104-query SLAQL benchmark adapted for public release
- Model × configuration accuracy and cost study
- Langfuse observability
- Offline demo mode (no API key required)

---

## Author

**Yekta Nasiri**  
AI Engineer | LLMs, NLP & Agentic Systems
