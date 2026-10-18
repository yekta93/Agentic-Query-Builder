# SLAQL Fields Reference

This document lists the available fields in the SIEM Log Analytics Query Language (SLAQL).

| Field         | Type     | Description                                      |
|---------------|----------|--------------------------------------------------|
| `timestamp`   | datetime | Event occurrence time                            |
| `source_ip`   | string   | Source IP address                                |
| `dest_ip`     | string   | Destination IP address                           |
| `dest_port`   | int      | Destination port number                          |
| `user`        | string   | Username associated with the event               |
| `event_type`  | string   | Event category (login, malware, firewall, dns, ...) |
| `severity`   | string   | Severity level: low, medium, high, critical      |
| `action`      | string   | Action taken: allowed, blocked, quarantined      |
| `hostname`    | string   | Hostname of the affected system                  |
| `process`     | string   | Process name                                     |
| `bytes_in`    | int      | Number of inbound bytes                          |
| `bytes_out`   | int      | Number of outbound bytes                         |
| `rule_name`   | string   | Name of the triggered security rule              |
| `country`     | string   | Country associated with the source IP            |
| `query`       | string   | DNS query string or similar request content      |
