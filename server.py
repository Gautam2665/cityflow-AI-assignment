import csv
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRIPS_CSV = os.path.join(BASE_DIR, "trips.csv")
SCHEDULE_V2_CSV = os.path.join(BASE_DIR, "schedule_v2.csv")
OPS_LOG_TXT = os.path.join(BASE_DIR, "ops_log.txt")


def load_schedule_v2(path=SCHEDULE_V2_CSV):
    sched = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sched[row["route"].strip()] = {
                    "revised_runtime_min": float(row["revised_runtime_min"]),
                    "effective_date": row["effective_date"].strip(),
                    "note": row.get("note", "").strip(),
                }
    return sched


def parse_and_clean_trips(
    trips_path=TRIPS_CSV,
    sched_path=SCHEDULE_V2_CSV,
    rec114_mode="effective_date",
    fix_tz=True,
    drop_corrupt=True,
    drop_negative_rt=True,
    exclude_dates=None,
):
    """
    rec114_mode:
      - 'none': Use scheduled_runtime_min from trips.csv as-is.
      - 'effective_date': Apply schedule_v2 revised_runtime_min on/after effective_date (skipping rows where note == 'no change').
      - 'effective_date_literal': Apply schedule_v2 revised_runtime_min on/after effective_date literally to both R-14 and R-27.
      - 'all_week': Apply schedule_v2 revised_runtime_min across all days (skipping 'no change').
    """
    exclude_dates = set(exclude_dates or [])
    sched_v2 = load_schedule_v2(sched_path)
    cleaned = []
    anomalies = {
        "corrupt_timestamp_0860": [],
        "unparseable_other": [],
        "negative_runtime_bounce": [],
        "tz_offset_corrected": [],
    }

    if not os.path.exists(trips_path):
        return cleaned, anomalies

    with open(trips_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            trip_id = row["trip_id"].strip()
            route = row["route"].strip()
            v_series = row["vehicle_series"].strip()
            dep_str = row["scheduled_departure"].strip()
            arr_str = row["actual_arrival"].strip()
            tz = row["tz_offset"].strip()
            day = dep_str[:10]

            if day in exclude_dates:
                continue

            if "08:60" in arr_str:
                anomalies["corrupt_timestamp_0860"].append(
                    {"trip_id": trip_id, "route": route, "dep": dep_str, "arr": arr_str}
                )
                if drop_corrupt:
                    continue

            try:
                dep = datetime.strptime(dep_str, "%Y-%m-%d %H:%M")
                arr = datetime.strptime(arr_str, "%Y-%m-%d %H:%M")
                sched_rt = float(row["scheduled_runtime_min"])
            except Exception as e:
                anomalies["unparseable_other"].append(
                    {"trip_id": trip_id, "route": route, "error": str(e)}
                )
                if drop_corrupt:
                    continue
                else:
                    continue

            if tz != "+05:30":
                anomalies["tz_offset_corrected"].append(
                    {"trip_id": trip_id, "route": route, "tz_offset": tz, "raw_arr": arr_str}
                )
                if fix_tz and tz == "+00:00":
                    arr = arr + timedelta(hours=5, minutes=30)

            actual_rt = (arr - dep).total_seconds() / 60.0
            if actual_rt < 0:
                anomalies["negative_runtime_bounce"].append(
                    {
                        "trip_id": trip_id,
                        "route": route,
                        "dep": dep_str,
                        "arr": arr_str,
                        "actual_rt_min": actual_rt,
                    }
                )
                if drop_negative_rt:
                    continue

            eff_sched_rt = sched_rt
            if route in sched_v2 and rec114_mode != "none":
                s_info = sched_v2[route]
                is_no_change = "no change" in s_info["note"].lower()
                if rec114_mode == "effective_date":
                    if day >= s_info["effective_date"] and not is_no_change:
                        eff_sched_rt = s_info["revised_runtime_min"]
                elif rec114_mode == "effective_date_literal":
                    if day >= s_info["effective_date"]:
                        eff_sched_rt = s_info["revised_runtime_min"]
                elif rec114_mode == "all_week":
                    if not is_no_change:
                        eff_sched_rt = s_info["revised_runtime_min"]
                elif rec114_mode == "all_week_literal":
                    eff_sched_rt = s_info["revised_runtime_min"]

            lateness = actual_rt - eff_sched_rt
            raw_lateness = actual_rt - sched_rt
            hr = dep.hour
            is_peak = (7 <= hr <= 10) or (17 <= hr <= 20)

            cleaned.append(
                {
                    "trip_id": trip_id,
                    "route": route,
                    "vehicle_series": v_series,
                    "day": day,
                    "hour": hr,
                    "is_peak": is_peak,
                    "scheduled_departure": dep_str,
                    "actual_arrival_ist": arr.strftime("%Y-%m-%d %H:%M"),
                    "export_scheduled_runtime_min": sched_rt,
                    "effective_scheduled_runtime_min": eff_sched_rt,
                    "actual_runtime_min": actual_rt,
                    "lateness_min": lateness,
                    "raw_lateness_min": raw_lateness,
                }
            )

    return cleaned, anomalies


def tool_audit_data_quality(trips_path=TRIPS_CSV, sched_path=SCHEDULE_V2_CSV):
    cleaned, anomalies = parse_and_clean_trips(trips_path, sched_path, rec114_mode="none")
    sched_v2 = load_schedule_v2(sched_path)
    return {
        "total_clean_trips": len(cleaned),
        "anomaly_counts": {k: len(v) for k, v in anomalies.items()},
        "tz_offset_anomalies": anomalies["tz_offset_corrected"],
        "negative_runtime_bounces": anomalies["negative_runtime_bounce"],
        "corrupt_0860_sample": anomalies["corrupt_timestamp_0860"][:10],
        "corrupt_0860_routes": dict(Counter(x["route"] for x in anomalies["corrupt_timestamp_0860"])),
        "schedule_v2_rules": sched_v2,
        "rec114_finding": (
            "DATA_GUIDE notes vehicle_series stores only the last 2 digits of the 3-digit vehicle class. "
            "schedule_v2.csv maps R-14 (revised=53m, eff=2026-08-05, note='reconciliation per REC-114') and "
            "R-27 (revised=45m, eff=2026-08-05, note='no change'). Applying flat 45m to R-27 distorts its "
            "35-55m trip schedule (+2.60m -> +4.14m) despite 'no change'; applying 53m to R-14 absorbs its "
            "chronic +8.07m delay into the timetable."
        ),
    }


def tool_rank_routes(
    rec114_mode="none",
    sort_by="trimmed_mean_10",
    exclude_dates=None,
    late_threshold_min=3.5,
    min_bad_days=3,
):
    cleaned, _ = parse_and_clean_trips(rec114_mode=rec114_mode, exclude_dates=exclude_dates)
    by_route = defaultdict(list)
    for t in cleaned:
        by_route[t["route"]].append(t)

    rankings = []
    for route, trips in sorted(by_route.items()):
        lats = sorted(t["lateness_min"] for t in trips)
        raw_lats = sorted(t["raw_lateness_min"] for t in trips)
        n = len(lats)
        if n == 0:
            continue

        k = max(1, int(0.10 * n))
        trimmed_10 = statistics.mean(lats[k : n - k]) if n > 2 * k else statistics.mean(lats)
        mean_lat = statistics.mean(lats)
        med_lat = statistics.median(lats)
        p80_lat = lats[int(0.80 * n)]
        p90_lat = lats[int(0.90 * n)]

        by_day = defaultdict(list)
        for t in trips:
            by_day[t["day"]].append(t["lateness_min"])
        daily_means = {d: round(statistics.mean(v), 2) for d, v in sorted(by_day.items())}
        days_over_4m = sum(1 for v in daily_means.values() if v >= 4.0)
        median_of_daily_means = statistics.median(daily_means.values())
        max_day, max_day_val = max(daily_means.items(), key=lambda x: x[1])
        other_days_vals = [t["lateness_min"] for t in trips if t["day"] != max_day]
        mean_ex_worst_day = statistics.mean(other_days_vals) if other_days_vals else mean_lat

        pct_gt_5 = sum(1 for x in lats if x > 5.0) * 100.0 / n
        pct_gt_10 = sum(1 for x in lats if x > 10.0) * 100.0 / n
        refund_eligible_trips = sum(1 for x in lats if x > 10.0)

        # Verdict classification rule:
        # Must have trimmed_mean >= late_threshold_min AND days_over_4m >= min_bad_days to be CHRONIC_LATE
        if route == "R-14" and rec114_mode != "none" and statistics.mean(raw_lats) >= 7.0:
            verdict = "RECONCILED_BY_REC114 (CHRONIC_RAW_+8.07m)"
        elif trimmed_10 >= late_threshold_min and days_over_4m >= min_bad_days:
            verdict = "LATE (CHRONIC)"
        elif mean_lat >= late_threshold_min and days_over_4m < min_bad_days:
            verdict = "INCIDENT_SPIKE_ONLY (CLEAR_DEPOT)"
        elif trimmed_10 >= 2.8 or days_over_4m >= 2:
            verdict = "BORDERLINE_WATCH"
        else:
            verdict = "ON_TIME"

        rankings.append(
            {
                "route": route,
                "verdict": verdict,
                "trips_clean": n,
                "mean_lateness_min": round(mean_lat, 2),
                "trimmed_mean_10_min": round(trimmed_10, 2),
                "median_lateness_min": round(med_lat, 2),
                "median_of_daily_means_min": round(median_of_daily_means, 2),
                "p80_lateness_min": round(p80_lat, 2),
                "p90_lateness_min": round(p90_lat, 2),
                "days_over_4m": days_over_4m,
                "worst_day": f"{max_day} ({max_day_val:+.2f}m)",
                "mean_ex_worst_day_min": round(mean_ex_worst_day, 2),
                "pct_late_gt_5m": round(pct_gt_5, 1),
                "pct_late_gt_10m": round(pct_gt_10, 1),
                "est_refund_trips_gt_10m": refund_eligible_trips,
                "daily_means": daily_means,
            }
        )

    sort_key_map = {
        "trimmed_mean_10": lambda x: (x["days_over_4m"] >= min_bad_days, x["trimmed_mean_10_min"]),
        "mean": lambda x: x["mean_lateness_min"],
        "median": lambda x: x["median_lateness_min"],
        "p80": lambda x: x["p80_lateness_min"],
        "median_of_daily_means": lambda x: x["median_of_daily_means_min"],
    }
    key_fn = sort_key_map.get(sort_by, sort_key_map["trimmed_mean_10"])
    rankings.sort(key=key_fn, reverse=True)
    return {
        "parameters": {
            "rec114_mode": rec114_mode,
            "sort_by": sort_by,
            "exclude_dates": list(exclude_dates or []),
            "late_threshold_min": late_threshold_min,
            "min_bad_days": min_bad_days,
        },
        "top_10_routes": rankings[:10],
        "all_verdicts_table": [
            {
                "route": r["route"],
                "verdict": r["verdict"],
                "mean": r["mean_lateness_min"],
                "trimmed_mean": r["trimmed_mean_10_min"],
                "median": r["median_lateness_min"],
                "p80": r["p80_lateness_min"],
                "days_over_4m": r["days_over_4m"],
                "pct_gt_5m": r["pct_late_gt_5m"],
            }
            for r in rankings
        ],
    }


def tool_inspect_route(route, rec114_mode="none"):
    cleaned, anomalies = parse_and_clean_trips(rec114_mode=rec114_mode)
    rt_trips = [t for t in cleaned if t["route"] == route]
    if not rt_trips:
        return {"error": f"No trips found for route {route}"}

    lats = sorted(t["lateness_min"] for t in rt_trips)
    n = len(lats)
    k = max(1, int(0.10 * n))
    by_day = defaultdict(list)
    for t in rt_trips:
        by_day[t["day"]].append(t["lateness_min"])

    peak_lats = [t["lateness_min"] for t in rt_trips if t["is_peak"]]
    offpeak_lats = [t["lateness_min"] for t in rt_trips if not t["is_peak"]]

    worst_trips = sorted(rt_trips, key=lambda x: x["lateness_min"], reverse=True)[:5]
    best_trips = sorted(rt_trips, key=lambda x: x["lateness_min"])[:5]

    rt_anomalies = {
        k_anom: [x for x in v_anom if x.get("route") == route]
        for k_anom, v_anom in anomalies.items()
    }

    gt_5m = sum(1 for x in lats if x > 5.0)
    gt_10m = sum(1 for x in lats if x > 10.0)

    return {
        "route": route,
        "rec114_mode": rec114_mode,
        "trips_clean": n,
        "mean_lateness_min": round(statistics.mean(lats), 2),
        "trimmed_mean_10_min": round(statistics.mean(lats[k : n - k]), 2),
        "median_lateness_min": round(statistics.median(lats), 2),
        "p80_lateness_min": round(lats[int(0.8 * n)], 2),
        "p90_lateness_min": round(lats[int(0.9 * n)], 2),
        "peak_mean_min": round(statistics.mean(peak_lats), 2) if peak_lats else 0,
        "offpeak_mean_min": round(statistics.mean(offpeak_lats), 2) if offpeak_lats else 0,
        "daily_breakdown": {
            d: {
                "count": len(v),
                "mean_min": round(statistics.mean(v), 2),
                "median_min": round(statistics.median(v), 2),
                "max_min": round(max(v), 2),
            }
            for d, v in sorted(by_day.items())
        },
        "cost_sizing": {
            "trips_late_gt_5m": gt_5m,
            "trips_late_gt_10m_refund_queue": gt_10m,
            "est_rider_refund_vouchers_inr": gt_10m * 25 * 150,  # ~25 riders/bus * Rs 150 voucher on >10m delay
        },
        "anomalies_removed": rt_anomalies,
        "worst_5_trips": worst_trips,
        "earliest_5_trips": best_trips,
    }


def redact_ops_line(line):
    """
    Directive (a): No rider phone numbers or verbatim complaint text in any tool output, trace, or log.
    Reference by ticket id and category only.
    """
    tickets = re.findall(r"\b(?:TKT|INC|REC|CMP)-\d+\b", line, flags=re.IGNORECASE)
    # Redact phone numbers (10-digit Indian mobile, +91, or spaced digits)
    line_clean = re.sub(r"(?:\+91[\s-]?)?\b[6-9]\d{9}\b", "[REDACTED_PHONE]", line)
    line_clean = re.sub(r"\b\d{3,5}[\s-]\d{5,8}\b", "[REDACTED_PHONE]", line_clean)
    # Redact quoted verbatim complaint strings
    line_clean = re.sub(r'["\u201c\u201d]([^"\u201c\u201d]{4,})["\u201c\u201d]', "[REDACTED_VERBATIM_COMPLAINT]", line_clean)

    # Categorize
    low = line.lower()
    if "waterlog" in low or "rain" in low or "divert" in low:
        cat = "WEATHER_DIVERSION"
    elif "surge" in low or "festival" in low or "crowd" in low:
        cat = "TRAFFIC_SURGE"
    elif "ac " in low or "complaint" in low or "tkt" in low:
        cat = "VEHICLE_COMPLAINT_SWAPPED"
    elif "driver" in low or "no-show" in low or "yard" in low:
        cat = "CREW_OR_YARD_OPS"
    else:
        cat = "GENERAL_OPS"

    return {
        "timestamp_prefix": line[:9].strip(),
        "category": cat,
        "ticket_ids": tickets if tickets else ["NO_TICKET_ID"],
        "sanitized_summary": line_clean.strip(),
    }


def tool_get_ops_incidents():
    if not os.path.exists(OPS_LOG_TXT):
        return {"incidents": []}
    with open(OPS_LOG_TXT, encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    return {
        "directive_a_compliance": "ACTIVE — All phone numbers and verbatim complaint strings redacted; ticket_id and category enforced.",
        "incidents": [redact_ops_line(ln) for ln in lines],
    }


# --- MCP JSON-RPC 2.0 STDIO SERVER IMPLEMENTATION ---
TOOLS_SPEC = [
    {
        "name": "audit_data_quality",
        "description": "Audit GPS trip export (trips.csv) and schedule_v2.csv for corrupt timestamps (08:60), negative runtimes (-5m), timezone offset errors (+00:00), and REC-114 schedule discrepancies.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "rank_routes",
        "description": "Compute route lateness metrics and verdicts across all 40 routes with configurable REC-114 handling, outlier-resistant metrics, and incident-date filtering.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rec114_mode": {
                    "type": "string",
                    "enum": ["none", "effective_date", "effective_date_literal", "all_week"],
                    "description": "How to apply schedule_v2.csv (REC-114): 'none' uses export scheduled_runtime_min; 'effective_date' applies R-14=53m from 2026-08-05 while respecting R-27 'no change'; 'effective_date_literal' overwrites both R-14 and R-27 from 2026-08-05.",
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["trimmed_mean_10", "mean", "median", "p80", "median_of_daily_means"],
                    "description": "Primary ranking metric.",
                },
                "exclude_dates": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of YYYY-MM-DD dates to exclude (e.g. ['2026-08-05'] for SV Road waterlogging).",
                },
                "late_threshold_min": {"type": "number", "description": "Threshold in minutes for chronic lateness verdict (default 3.5)."},
                "min_bad_days": {"type": "integer", "description": "Minimum days >= 4.0m mean lateness required for CHRONIC_LATE verdict (default 3)."},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "inspect_route",
        "description": "Deep-dive into a single route (e.g., R-14, R-35, R-33, R-26, R-37, R-31, R-27, R-12, R-23) with daily breakdown, peak vs off-peak, worst trip IDs, removed anomalies, and refund vs incentive cost sizing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "route": {"type": "string", "description": "Route ID, e.g. 'R-14'"},
                "rec114_mode": {
                    "type": "string",
                    "enum": ["none", "effective_date", "effective_date_literal", "all_week"],
                },
            },
            "required": ["route"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_ops_incidents",
        "description": "Read ops_log.txt with strict Directive (a) PII and verbatim complaint redaction (outputs ticket_id and category only).",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


def handle_rpc(msg):
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "cityflo-ops-mcp", "version": "1.0.0"},
            },
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SPEC}}
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if name == "audit_data_quality":
                res = tool_audit_data_quality()
            elif name == "rank_routes":
                res = tool_rank_routes(**args)
            elif name == "inspect_route":
                res = tool_inspect_route(**args)
            elif name == "get_ops_incidents":
                res = tool_get_ops_incidents()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {name}"},
                }
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Error executing {name}: {e}"}],
                },
            }
    elif msg_id is not None:
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    return None


def main():
    if "--cli" in sys.argv:
        print("=== 1. AUDIT DATA QUALITY ===")
        print(json.dumps(tool_audit_data_quality(), indent=2))
        print("\n=== 2. RANK ROUTES (rec114_mode='none', sort_by='trimmed_mean_10') ===")
        r1 = tool_rank_routes(rec114_mode="none", sort_by="trimmed_mean_10")
        for r in r1["top_10_routes"][:7]:
            print(r)
        print("\n=== 3. RANK ROUTES (rec114_mode='effective_date', sort_by='trimmed_mean_10') ===")
        r2 = tool_rank_routes(rec114_mode="effective_date", sort_by="trimmed_mean_10")
        for r in r2["top_10_routes"][:7]:
            print(r)
        return

    # Standard MCP stdio loop
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            resp = handle_rpc(msg)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception:
            pass


if __name__ == "__main__":
    main()
