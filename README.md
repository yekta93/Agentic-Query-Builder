# Agentic Query Builder

**An agentic multi-agent system that converts natural language questions into structured SIEM Log Analytics queries using LangGraph.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

Agentic Query Builder is a production-oriented multi-agent pipeline that translates natural language questions (English or Persian) into precise **SIEM Log Analytics Query Language (SLAQL)** queries.

It demonstrates modern LLM orchestration patterns:

- **Multi-agent workflow** orchestrated with LangGraph
- **Few-shot learning** with curated examples
- **Syntax validation** loop
- **Self-reflection** for query improvement
- **Evaluation / judging** stage
- Configurable pipeline stages (enable/disable agents)

This project was designed as a real-world solution for converting analyst questions into structured SIEM log analysis queries.

---

## Architecture

```text
                  ┌─────────────┐
                  │  Translate  │  (optional)
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │   Generate  │  ← Few-shot + Schema
                  └──────┬──────┘
                         │
               ┌─────────▼─────────┐
               │  Syntax Checker   │
               └─────────┬─────────┘
                         │
              ┌──────────▼──────────┐
              │      Reflect        │  (on error, with retry)
              └──────────┬──────────┘
                         │
                  ┌──────▼──────┐
                  │    Judge    │
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │   Execute   │  (mock / demo)
                  └─────────────┘
```

### Pipeline Stages

| Stage            | Description                                      | Configurable |
|------------------|--------------------------------------------------|--------------|
| **Translate**    | Optional translation of the input question       | Yes          |
| **Generate**     | LLM generates SLAQL query using few-shot examples| Always on    |
| **Syntax Check** | Validates generated query against SLAQL rules    | Yes          |
| **Reflect**      | Analyzes errors and improves the query           | Yes          |
| **Judge**        | Final quality evaluation                         | Always on    |
| **Execute**      | Runs the query (mocked in demo mode)             | Always on    |

---

## SIEM Log Analytics Query Language (SLAQL)

SLAQL is a domain-specific language designed for analyzing security logs in a SIEM context.

### Core Fields

| Field         | Type     | Description                          |
|---------------|----------|--------------------------------------|
| `timestamp`   | datetime | Event occurrence time                |
| `source_ip`   | string   | Source IP address                    |
| `dest_ip`     | string   | Destination IP address               |
| `user`        | string   | Username                             |
| `event_type`  | string   | Event category (`login`, `malware`, `firewall`, ...) |
| `severity`   | string   | `low` / `medium` / `high` / `critical` |
| `action`      | string   | `allowed` / `blocked` / `quarantined` |
| `hostname`    | string   | Host name                            |
| `process`     | string   | Process name                         |
| `bytes_in`    | int      | Inbound bytes                        |
| `bytes_out`   | int      | Outbound bytes                       |
| `rule_name`   | string   | Security rule name                   |
| `country`     | string   | Source country                       |

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

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your OPENROUTER_API_KEY
```

### 3. Run Demo

```bash
# Process a single example
python main.py --suffix 1

# Run full demo set
python main.py --suffix all

# Run with a specific configuration candidate
python main.py --candidate-index 0 --suffix 1
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
├── data/demo/               # Synthetic clean examples
├── artifacts/               # SLAQL syntax & field references
└── tests/
```

---

## Key Features for Portfolio

- **LangGraph multi-agent orchestration**
- Configurable agent pipeline (ablation-friendly)
- Few-shot prompting with structured examples
- Self-reflection + retry loop on syntax errors
- Clean separation of concerns
- Ready for evaluation experiments (multiple candidates)
- Fully synthetic demo data (no sensitive information)

---

## License

MIT

---

## Author

**Yekta Nasiri**  
AI Engineer | LLMs, NLP & Agentic Systems
