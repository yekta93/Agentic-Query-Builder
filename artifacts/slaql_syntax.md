# SLAQL Syntax Guide

SIEM Log Analytics Query Language (SLAQL) is a pipeline-oriented query language for analyzing security logs.

## Basic Structure

```text
from <time_range>
| where <conditions>
| stats <aggregations> by <fields>
| sort <field> [asc|desc]
| fields <field_list>
| timeseries <aggregation> by <fields>
```

## Time Range

- `from last 1h`
- `from last 24h`
- `from last 7d`
- `from 2024-01-01 to 2024-01-02`
- `from 2024-06-01T00:00:00 to 2024-06-01T23:59:59`

## Filtering (`where`)

Supported operators:

- `==`, `!=`
- `>`, `>=`, `<`, `<=`
- `like` (wildcard with `*`)
- `in (...)`
- `and`, `or`, `not`

Examples:

```text
| where severity == "high"
| where event_type == "login" and action == "blocked"
| where process like "*powershell*"
| where country in ("CN", "RU", "KP")
| where bytes_out > 1000000
```

## Aggregations (`stats`)

```text
| stats count() by user
| stats count(), avg(bytes_out) by source_ip
| stats sum(bytes_in) by hostname
```

## Sorting

```text
| sort count desc
| sort timestamp asc
```

## Field Selection

```text
| fields timestamp, user, source_ip, rule_name
```

## Timeseries

```text
| timeseries count() by event_type
| timeseries avg(bytes_out) by hostname
```

## Full Examples

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
