# Cityflo Ops MCP Server (`cityflo-ops`)

Lightweight, zero-dependency Python Model Context Protocol (MCP) server over `stdio` for auditing GPS trip exports, enforcing operational directives (Directive `a` PII/complaint redaction and Directive `b` REC-114 timetable reconciliation), and computing outlier-resistant route lateness verdicts.

## How to Run

### 1. As an MCP Server (stdio JSON-RPC 2.0)
Add to `.agents/mcp_config.json` or `~/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "cityflo-ops": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```

### 2. Standalone CLI Verification
```bash
python server.py --cli
```

## Exposed MCP Tools
- `audit_data_quality`: Scans `trips.csv` and `schedule_v2.csv` for corrupt timestamps (`08:60`), negative runtime bounces (`-5.0m`), timezone offset errors (`+00:00` on `T1-02864`), and REC-114 discrepancies.
- `rank_routes`: Ranks all 40 routes with configurable `rec114_mode` (`none`, `effective_date`, `effective_date_literal`, `all_week`), `sort_by` (`trimmed_mean_10`, `mean`, `median`, `p80`, `median_of_daily_means`), `exclude_dates` (e.g. `["2026-08-05"]`), `late_threshold_min`, and `min_bad_days`.
- `inspect_route`: Deep-dives into a specific route ID (`R-14`, `R-35`, `R-33`, `R-26`, `R-37`, `R-31`, `R-27`, `R-12`, `R-23`) with daily breakdown, peak/off-peak split, worst trip IDs, and financial cost sizing.
- `get_ops_incidents`: Parses `ops_log.txt` with strict Directive (a) redaction of phone numbers and verbatim complaint strings, exposing only `ticket_id` and `category`.
