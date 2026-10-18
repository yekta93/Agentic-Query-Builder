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
- Configurable pipeline stages (easy ablation studies)

This project was designed as a real-world solution for converting security-analyst questions into structured SIEM log analysis queries.

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

## Demo Mode (no API key required)

The repository ships with a fully functional **offline demo mode**:

- If `OPENROUTER_API_KEY` is **not** set, the Generate node automatically returns the curated reference query for that example.
- Judge falls back to a strong heuristic scorer.
- Reflect uses a deterministic feedback message.
- Execute always returns a realistic mocked result.

This lets you run the complete graph, inspect intermediate state, and generate output files without any external API.

```bash
# Works out of the box (no .env needed)
python main.py --suffix 1
python main.py --suffix all
```

When you later add a real key, the same commands switch to live LLM generation automatically.

---

## SIEM Log Analytics Query Language (SLAQL)

SLAQL is a pipeline-oriented domain-specific language for security log analysis.

### Core Fields

| Field         | Type     | Description                          |
|---------------|----------|--------------------------------------|
| `timestamp`   | datetime | Event occurrence time                |
| `source_ip`   | string   | Source IP address                    |
| `dest_ip`     | string   | Destination IP address               |
| `dest_port`   | int      | Destination port                     |
| `user`        | string   | Username                             |
| `event_type`  | string   | `login`, `malware`, `firewall`, `dns`, … |
| `severity`   | string   | `low` / `medium` / `high` / `critical` |
| `action`      | string   | `allowed` / `blocked` / `quarantined` |
| `hostname`    | string   | Host name                            |
| `process`     | string   | Process name                         |
| `bytes_in`    | int      | Inbound bytes                        |
| `bytes_out`   | int      | Outbound bytes                       |
| `rule_name`   | string   | Security rule name                   |
| `country`     | string   | Source country                       |
| `query`       | string   | DNS query / request content          |

### Example Queries

```text
from last 24h
| where event_type == "login" and severity == "high"
| stats count() by user, source_ip
| sort count desc
```

```text
from last 1h
| where action == "blocked" and country != "IR"
| timeseries count() by event_type
```

```text
from 2024-06-01 to 2024-06-02
| where process like "*powershell*" and severity in ("high", "critical")
| fields timestamp, user, hostname, process, rule_name
```

---

## Sample Run Output

```bash
$ python main.py --suffix 1
```

```json
{
  "suffix": 1,
  "question": "Show me all high severity login events from the last 24 hours grouped by user and source IP",
  "pql_query": "from last 24h\n| where event_type == \"login\" and severity == \"high\"\n| stats count() by user, source_ip\n| sort count desc",
  "has_error": false,
  "error": null,
  "retry_count": 0,
  "syntax_check_result": {
    "valid": true,
    "message": "OK"
  },
  "evaluation_result": {
    "score": 0.95,
    "valid_syntax": true,
    "comments": "Syntactically valid; High overlap with reference (92%)"
  },
  "execution_result": {
    "status": "success",
    "rows_returned": 17,
    "execution_time_ms": 142,
    "sample_rows": [
      {"user": "alice", "source_ip": "10.0.1.15", "count": 7},
      {"user": "bob", "source_ip": "192.168.3.22", "count": 5}
    ],
    "note": "Mocked execution result for demonstration purposes."
  }
}
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yekta93/Agentic-Query-Builder.git
cd Agentic-Query-Builder

# Using uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### 2. (Optional) Configure Environment for live LLM

```bash
cp .env.example .env
# Edit .env and set your OPENROUTER_API_KEY
```

### 3. Run

```bash
# Single example (works offline)
python main.py --suffix 1

# Full demo set (10 examples)
python main.py --suffix all

# Specific configuration candidate
python main.py --candidate-index 0 --suffix 1

# Run every candidate defined in config.yaml
python main.py --all --suffix 1
```

---

## Configuration

Pipeline behavior is controlled via `config.yaml`. You can define multiple **candidates** (different combinations of model + enabled stages) and compare them easily.

```yaml
candidates:
  - model: "google/gemma-2-27b-it"
    prompt_config: ["few-shots"]
    syntax_checker: true
    reflect: true
    translate: false

  - model: "google/gemma-2-27b-it"
    prompt_config: []
    syntax_checker: true
    reflect: true
    translate: false

  - model: "google/gemma-2-27b-it"
    prompt_config: []
    syntax_checker: false
    reflect: false
    translate: false
```

---

## Project Structure

```text
├── main.py                  # CLI entry point
├── config.yaml              # Pipeline & model configuration
├── src/
│   ├── graph.py             # LangGraph workflow definition
│   ├── state.py             # Shared state schema
│   ├── config_loader.py     # Config management
│   └── query_builder/       # Individual agents
├── utils/                   # Helpers, LLM clients, schemas
├── data/demo/               # 10 synthetic clean examples
│   ├── questions/
│   ├── queries/
│   └── details/
├── artifacts/               # SLAQL syntax & field references
└── tests/
```

---

## Key Features for Portfolio

- **LangGraph multi-agent orchestration** with conditional edges and retry loops
- Configurable agent pipeline (ablation-friendly)
- Few-shot prompting with leave-one-out support
- Self-reflection that feeds guidance back into generation
- LLM-as-Judge + robust heuristic fallback
- Fully synthetic demo data (no sensitive information)
- Works offline out of the box for demos and CI

---

## License

MIT

---

## Author

**Yekta Nasiri**  
AI Engineer | LLMs, NLP & Agentic Systems
