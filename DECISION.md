# Friday Regional Review — Route Lateness Verdicts & Worst-Three Ranking

**From:** Ops Analytics / Priya (Ops Lead, Mumbai North)  
**Subject:** Committed Weekly Route Verdicts, Worst-Three Ranking, and Consequential Rule Defenses  

---

## 1. Executive Verdict & The Committed Worst-Three

A raw weekly mean is unfit for regional review: a single misconfigured UTC clock (`T1-02864` on `R-23` at `-332.0 min`) or a single day of municipal corridor flooding (`R-35` on Wednesday `2026-08-05` at `+51.32 min`) swings the weekly mean and hands depot heads an easy target to discredit the review.

To make Priya's numbers bulletproof, every route is evaluated after deterministic telemetry hygiene using a **Two-Gate Chronic Lateness Rule**:
1. **Severity Gate:** **10% Two-Sided Trimmed Mean Lateness >= +3.50 minutes** (trimming the top 10% and bottom 10% of trips per route to neutralize single-trip outliers).
2. **Persistence Gate:** **At least 3 out of 7 days with a daily mean lateness >= +4.00 minutes** (separating structural schedule/depot failure from a one-day external force-majeure incident).

### The Worst-Three Ranking (Committed Call)

* **Official Worst-Three (Enforcing Signed-Off REC-114 from Effective Date `2026-08-05`):**
  1. **#1 Worst — `R-33` (`LATE - CHRONIC`):** **+5.42 min** trimmed mean (+5.36 min mean, +5.0 min median, +9.0 min P80). Late >= 4.0 min on **7 out of 7 days** (`4.73m, 4.40m, 4.13m, 6.60m, 6.40m, 6.80m, 4.36m`). 47.1% of trips arrived >5 min late.
  2. **#2 Worst — `R-26` (`LATE - CHRONIC`):** **+4.52 min** trimmed mean (+4.51 min mean, +4.0 min median, +8.0 min P80). Late >= 4.0 min on **5 out of 7 days** (`5.43m, 2.73m, 4.60m, 5.73m, 3.07m, 4.00m, 6.21m`). 42.7% of trips arrived >5 min late.
  3. **#3 Worst — `R-37` (`LATE - CHRONIC`):** **+4.27 min** trimmed mean (+4.13 min mean, +4.0 min median, +8.0 min P80). Late >= 4.0 min on **4 out of 7 days** (and 3.73–3.93 min on the other 3 days). 40.0% of trips arrived >5 min late.
* **Shadow #1 (If REC-114 Schedule Padding Is Rejected) — `R-14` (`RECONCILED_BY_REC114`):**
  * Physically, **`R-14` is the #1 latest route in the network** (**+7.90 min** trimmed mean, **+8.07 min** raw mean, **+8.0 min** median, **7/7 days** >6.5 min late, **72.0%** of trips >5 min late). However, per signed-off **REC-114**, `schedule_v2.csv` resets `R-14`'s scheduled runtime to a flat **53 minutes** effective `2026-08-05` (adding ~8 minutes of timetable buffer to match its actual 53.3-minute average runtime), which drops `R-14`'s post-reconciliation lateness to **+2.89 min** trimmed mean (**+2.47 min** mean; `-3.29m` to `+3.82m` from Aug 5–9).
  * **Our stance for Priya:** Present **`R-33`, `R-26`, `R-37`** as the official Worst-Three aligned with the REC-114 sheet in front of the committee, while explicitly tabling **`R-14`** as a **Timetable-Padded Chronic Route** where rider wait times were solved on paper rather than on the road.
* **Borderline #4 (Also Flagged `LATE - CHRONIC`, Cut from Top-3) — `R-31`:** **+3.73 min** trimmed mean (+3.59 min mean, +4.0 min median, 3/7 days >= 4.0 min, 0% of trips >10 min late).
* **Explicit Answer on `R-12` (Priya's Standup Question):** **`R-12` was NOT late this week (`ON_TIME`).** Across 112 clean trips, `R-12` posted a **+1.62 min** trimmed mean (+1.79 min mean, +2.0 min median, P80 +4.0 min, **0/7 days** >= 4.0 min, and only 2 trips all week >10 min late). Clear `R-12` completely.

---

## 2. Five Consequential Calls & Borderline Defenses

### Call 1: Clearing `R-35` from the Worst-Three Despite an +8.05 min Weekly Mean (The "Single Bad Day" Rule)
* **The Rule:** A route is classified as `LATE (CHRONIC)` and eligible for the Worst-Three **only if** it breaches both the Severity Gate (10% trimmed mean >= +3.50 min) **and** the Persistence Gate (daily mean >= +4.00 min on at least **3 out of 7 days**). Any route breaching the mean solely on 1–2 days is classified `INCIDENT_SPIKE_ONLY (CLEAR_DEPOT)`.
* **The Case It Breaks On:** **Route `R-35`** (specifically Wednesday `2026-08-05` trips **`T1-04505` through `T1-04523`**, peaking at **`T1-04521` (+61.0 min late)** and **`T1-04508` / `T1-04516` (+60.0 min late)**). Under our rule, `R-35`'s depot head is **cleared** even though `R-35` has the second-highest raw mean in the network (**+8.05 min**) and generated **21 severe-delay trips (>10 min late)** on Wednesday alone. Furthermore, `ops_log.txt` notes `"Wed 06:40 SV Road waterlogged, western corridor diverted ~35min all AM"` and `"Wed 18:20 crowd surge, festival"`, yet `R-35` also had 5 midday trips (`T1-04507`, `T1-04514`, `T1-04518`, `T1-04520`, `T1-04521` between 12:21 and 14:23) delayed by 48–61 minutes as morning diversions cascaded through vehicle turnarounds. We keep the rule anyway because on the other **6 days of the week (113 trips)**, `R-35` averaged **+0.78 minutes** (`+0.26m, +0.74m, -0.22m, +1.58m, +1.42m, +0.84m`) with a weekly median of **+2.0 minutes**. Punishing a depot head for a 1-day municipal flooding collapse destroys operational trust.
* **The Cost, and Who Pays It:** **Riders and the Customer Refund Queue pay.** Clearing `R-35`'s depot head protects their **Rs 25,000 monthly on-time incentive**, while Cityflo's central ops budget absorbs the **21 severely delayed Wednesday trips** (~525 riders affected; at Rs 150 SLA credit per >10 min trip, **Rs 78,750 in rider refund exposure** plus app-store rating damage from riders stranded on Wednesday).
* **What Would Change My Mind:** Dispatch or GPS breadcrumbs on Wednesday `2026-08-05` showing that sibling western-corridor routes cleared the SV Road diversion by 11:00 AM while `R-35` buses sat idle in the depot or missed midday crew handoffs (`11:20–14:23`), OR `R-35` breaching +4.0 min on at least 2 additional non-weather days.

---

### Call 2: Interpreting REC-114 (`schedule_v2.csv`) on `R-14` and `R-27` (The "Last-Two-Digits & No-Change" Rule)
* **The Rule:** Per `DATA_GUIDE.md`, `vehicle_series` records only the **last two digits** of the 3-digit vehicle class (meaning `414` -> `14` on `R-14` and `427` -> `27` on `R-27`, whereas `vehicle_series == '40'` on `R-40` is simply route 40's suffix, not a `4xx` revision). When applying `schedule_v2.csv`:
  1. Respect the `effective_date` (`2026-08-05` onwards).
  2. Apply `revised_runtime_min` **only where `note` indicates an active reconciliation (`R-14` -> 53 min)**; **do not** overwrite trip-level runtimes with a flat constant when `note == "no change"` (`R-27` -> 45 min).
* **The Case It Breaks On:** **Route `R-14`** (e.g., Sunday trip **`T1-01784`**, where actual runtime was 68 min vs 50 min export schedule = **+18.0 min late**, reduced to +15.0 min under REC-114; and Wednesday `2026-08-05` trips where `R-14`'s daily mean flips from **+8.24 min late** to **-3.29 min "early"** overnight) AND **Route `R-27`** (where overwriting 50- and 55-minute peak trips with a flat `45 min` when `schedule_v2.csv` explicitly states `"no change"` fabricates a **+4.14 min** mean lateness with 21.7% >10m late out of a healthy **+2.60 min** route with 3.5% >10m late).
* **The Cost, and Who Pays It:**
  * On **`R-14`**, **riders pay in hidden wait/travel time** and **the refund queue pays** for the **28 trips** (pre-REC114) / **18 trips** (post-REC114) delayed >10 min (**Rs 67,500–Rs 1,05,000** in rider SLA exposure), while `R-14`'s depot head keeps their **Rs 25,000 incentive** thanks to the 53-minute timetable revision.
  * On **`R-27`**, our rule **saves `R-27`'s depot head from losing Rs 25,000** to a spreadsheet artifact (`"no change"` flat-45 bug) that would have falsely ranked `R-27` #4/#3 worst.
* **What Would Change My Mind:**
  * For **`R-14`**: If regional review confirms REC-114 was a *retroactive* accounting baseline meant to excuse Mon–Tue (`2026-08-03` and `2026-08-04`) as well, `R-14` drops to **+0.32 min** all-week; conversely, if the review rules that passenger-facing app ETAs still showed the 35–55 min export schedule all week, `R-14` immediately takes **Rank #1 Worst (+7.90m trimmed / +8.07m mean)**.
  * For **`R-27`**: Written confirmation from scheduling that Peak `50/55 min` timetables on `R-27` were intentionally abolished on Aug 5 in favor of a hard 45-minute cap.

---

### Call 3: Ranking `R-37` (#3 Worst) Over Borderline `R-31` (#4)
* **The Rule:** Among routes passing both Chronic Lateness gates (10% trimmed mean >= +3.50 min and >= 3 days >= +4.00 min), rank by **10% Trimmed Mean**, breaking ties by **P80 lateness** and **%>10 min severe delay rate**.
* **The Case It Breaks On:** **Route `R-31` on Thursday `2026-08-06` (+4.56 min mean)** and **Saturday `2026-08-08` (+4.50 min mean)** vs **Route `R-37` on Wednesday `2026-08-05` (+3.93 min, median 3.0m)** and **Sunday `2026-08-09` (+3.73 min, median 3.0m)**. Both `R-37` and `R-31` have the exact same weekly median (**+4.0 min**), and `R-31` was worse than `R-37` on Tuesday (`4.06m vs 3.93m`), Thursday (`4.56m vs 4.00m`), and Saturday (`4.50m vs 4.27m`). However, we keep `R-37` at #3 Worst and cut `R-31` at #4 because `R-37` has a higher trimmed mean (**+4.27 min vs +3.73 min**), higher P80 (**+8.0 min vs +7.0 min**), higher >5 min rate (**40.0% vs 33.0%**), and **5 trips >10 min late** (e.g., `T1-04740` and `T1-04804` at **+13.0 min late**), whereas **`R-31` had 0 trips >10 min late all week**.
* **The Cost, and Who Pays It:** **`R-37`'s depot head pays** (loses the **Rs 25,000 on-time incentive** by 0.54 min of trimmed mean), while **`R-31` riders absorb a chronic 3.6–4.0 minute drag** across 37 trips (>5 min late) without triggering either a Top-3 depot escalation or >10 min automated refund vouchers (**Rs 0 refund payout on `R-31`** vs **Rs 18,750 on `R-37`**).
* **What Would Change My Mind:** If the review weights **Peak-Hour Commuter Lateness** only (07:00–10:59 and 17:00–20:59), `R-37`'s peak mean is **+3.63 min** (because its worst delays are off-peak, +4.67 min) — a single peak-hour breakdown on `R-31` (+3.31 min peak) pushing `R-31`'s peak mean above `R-37` would flip #3 and #4.

---

### Call 4: Telemetry Hygiene — Dropping 18 Negative-Runtime Bounces (`-5.0 min`) and 24 Corrupt `08:60` Timestamps
* **The Rule:** Discard any trip record where (a) `actual_arrival` contains an invalid sexagesimal minute (`08:60`, 24 rows) or (b) normalized `actual_runtime_min < 0` (18 rows, all exactly **-5.0 minutes** where `actual_arrival = scheduled_departure - 5 min`). Do **not** impute or winsorize these rows into route averages.
* **The Case It Breaks On:**
  1. **Negative runtime rows (`-5.0 min`):** Specific trips like **`T1-02730` on `R-21`** (`dep: 2026-08-08 06:18, arr: 06:13, sched: 55m` -> raw lateness **-60.0 min**) and **`T1-03377` on `R-26`** (`dep: 11:58, arr: 11:53, sched: 50m`, raw lateness `-55.0m`). Dropping `T1-03377` raises `R-26`'s mean from **+3.94 min to +4.51 min**, cementing `R-26` in the Worst-Three.
  2. **Corrupt `08:60` rows:** Specific trips like **`T1-03641` on `R-28`** (`dep: 2026-08-07 06:29, sched: 35m, arr: 2026-08-07 08:60`) or **`T1-00136` on `R-01`** (`dep: 16:51, arr: 08:60`). Repairing `"08:60"` to `"09:00"` turns `T1-03641` into a fake **+116.0 min delay** and `T1-00136` into a **-471.0 min** error because `"08:60"` is a firmware null-sentinel value, not a 9:00 AM arrival.
* **The Cost, and Who Pays It:** **42 trips (0.79% of the 5,292-row export) go unmeasured.** On **`R-26`**, dropping `T1-03377` removes a fake `-55 min` credit and locks `R-26` into **Rank #2 Worst** (costing `R-26`'s depot head their **Rs 25,000 incentive**). On **`R-27`** and **`R-29`** (3 dropped `08:60` rows each), if any of those 6 unlogged trips were actually >10 min late, ~150 riders lost automated delay verification (~Rs 22,500 in unissued delay credits).
* **What Would Change My Mind:** Raw GPS packet logs showing that `08:60` was a string-formatting bug specifically for arrivals in the `08:59:30–09:00:00` window (which would only validate trips departing around `08:05–08:25`).

---

### Call 5: Timezone Normalization on `T1-02864` (`R-23`) and Retaining Coincident Arrival Timestamps
* **The Rule:** Normalize any `actual_arrival` stamped with `tz_offset != '+05:30'` to IST (`+05:30`) before computing runtime (`+00:00` -> add `+330 minutes`). Retain trips that share an identical `(route, actual_arrival)` timestamp provided their `trip_id` and `scheduled_departure` are distinct and yield physically valid runtimes.
* **The Case It Breaks On:**
  1. **Timezone fix:** Trip **`T1-02864` on `R-23`** (`dep: 2026-08-03 06:14, arr: 2026-08-03 01:32, tz_offset: +00:00, sched: 50m`). Without UTC-to-IST conversion, `T1-02864` computes as **-332.0 min late**, dragging `R-23`'s weekly mean from **+0.11 min** down to **-2.39 min**. Converting `01:32 UTC` to `07:02 IST` yields an actual runtime of `48.0 min` (**-2.0 min lateness**).
  2. **Coincident arrival timestamps (59 pairs):** For example, on **`R-01` (`2026-08-07 19:27`)**, trips **`T1-00095`** (`dep: 18:55, sched: 40m` -> `-8.0m` late) and **`T1-00110`** (`dep: 18:39, sched: 40m` -> `+8.0m` late) both report arrival at `19:27`. We keep both rows because their opposite lateness signs cancel in the mean and our 10% trimmed mean + median are invariant to symmetric tail pairs.
* **The Cost, and Who Pays It:** Zero incentive or refund distortion on `R-23` (which remains `ON_TIME` at +0.11m).
* **What Would Change My Mind:** Vehicle-ID or IMEI-level telemetry showing the same physical bus was assigned to both overlapping `trip_id`s within the same hour, which would trigger deduplication keeping only the trip matching the schedule slot.

---

## 3. Complete 40-Route Weekly Verdict Table (Sorted by Post-REC114 Ranking)

| Rank (Post-REC114) | Route | Verdict | Clean Trips | 10% Trimmed Mean (min) | Mean (min) | Median (min) | P80 (min) | Days >= 4.0m | % Late > 5m | Pre-REC114 Mean (min) |
|---:|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | **R-33** | `LATE (CHRONIC)` | 104 | **+5.42** | +5.36 | +5.0 | +9.0 | 7/7 | 47.1% | +5.36 |
| 2 | **R-26** | `LATE (CHRONIC)` | 103 | **+4.52** | +4.51 | +4.0 | +8.0 | 5/7 | 42.7% | +4.51 |
| 3 | **R-37** | `LATE (CHRONIC)` | 105 | **+4.27** | +4.13 | +4.0 | +8.0 | 4/7 | 40.0% | +4.13 |
| 4 | **R-31** | `LATE (CHRONIC)` | 112 | **+3.73** | +3.59 | +4.0 | +7.0 | 3/7 | 33.0% | +3.59 |
| 5 | **R-35** | `INCIDENT_SPIKE_ONLY (CLEAR_DEPOT)` | 132 | **+3.96** | +8.05 | +2.0 | +7.0 | 1/7 | 24.2% | +8.05 |
| 6 | **R-14** | `RECONCILED_BY_REC114 (CHRONIC_RAW_+8.07m)` | 118 | **+2.89** | +2.47 | +4.0 | +10.0 | 2/7 | 43.2% | +8.07 |
| 7 | **R-17** | `BORDERLINE_WATCH` | 147 | **+2.87** | +2.98 | +3.0 | +7.0 | 1/7 | 27.9% | +2.98 |
| 8 | **R-07** | `ON_TIME` | 147 | **+2.67** | +2.73 | +3.0 | +6.0 | 0/7 | 21.8% | +2.73 |
| 9 | **R-40** | `ON_TIME` | 152 | **+2.65** | +2.61 | +3.0 | +6.0 | 0/7 | 21.7% | +2.61 |
| 10 | **R-15** | `BORDERLINE_WATCH` | 119 | **+2.64** | +2.67 | +3.0 | +6.0 | 2/7 | 21.0% | +2.67 |
| 11 | **R-08** | `ON_TIME` | 126 | **+2.58** | +2.36 | +3.0 | +6.0 | 0/7 | 20.6% | +2.36 |
| 12 | **R-27** | `ON_TIME` | 143 | **+2.56** | +2.60 | +2.0 | +6.0 | 1/7 | 22.4% | +2.60 |
| 13 | **R-34** | `ON_TIME` | 124 | **+2.55** | +2.51 | +3.0 | +6.0 | 1/7 | 22.6% | +2.51 |
| 14 | **R-05** | `ON_TIME` | 105 | **+2.40** | +2.34 | +2.0 | +5.0 | 0/7 | 19.0% | +2.34 |
| 15 | **R-19** | `ON_TIME` | 125 | **+2.38** | +2.33 | +3.0 | +5.0 | 1/7 | 18.4% | +2.33 |
| 16 | **R-09** | `ON_TIME` | 146 | **+2.29** | +2.31 | +2.0 | +6.0 | 0/7 | 22.6% | +2.31 |
| 17 | **R-11** | `ON_TIME` | 137 | **+2.05** | +2.26 | +2.0 | +5.0 | 0/7 | 16.8% | +2.26 |
| 18 | **R-21** | `ON_TIME` | 124 | **+2.04** | +1.82 | +2.0 | +6.0 | 0/7 | 21.0% | +1.82 |
| 19 | **R-18** | `ON_TIME` | 154 | **+2.00** | +2.03 | +2.0 | +6.0 | 0/7 | 20.8% | +2.03 |
| 20 | **R-20** | `ON_TIME` | 145 | **+1.97** | +1.97 | +2.0 | +5.0 | 0/7 | 16.6% | +1.97 |
| 21 | **R-22** | `ON_TIME` | 112 | **+1.92** | +1.82 | +2.0 | +5.0 | 0/7 | 16.1% | +1.82 |
| 22 | **R-39** | `ON_TIME` | 154 | **+1.83** | +1.81 | +2.0 | +5.0 | 0/7 | 16.2% | +1.81 |
| 23 | **R-03** | `ON_TIME` | 103 | **+1.67** | +1.70 | +2.0 | +6.0 | 1/7 | 20.4% | +1.70 |
| 24 | **R-12** | `ON_TIME` | 112 | **+1.62** | +1.79 | +2.0 | +4.0 | 0/7 | 13.4% | +1.79 |
| 25 | **R-38** | `ON_TIME` | 146 | **+1.44** | +1.49 | +1.0 | +5.0 | 0/7 | 16.4% | +1.49 |
| 26 | **R-02** | `ON_TIME` | 105 | **+1.42** | +1.34 | +2.0 | +5.0 | 0/7 | 14.3% | +1.34 |
| 27 | **R-25** | `ON_TIME` | 139 | **+1.38** | +1.45 | +1.0 | +5.0 | 0/7 | 14.4% | +1.45 |
| 28 | **R-32** | `ON_TIME` | 133 | **+1.17** | +1.17 | +1.0 | +5.0 | 0/7 | 15.8% | +1.17 |
| 29 | **R-10** | `ON_TIME` | 126 | **+1.07** | +1.07 | +1.0 | +4.0 | 0/7 | 14.3% | +1.07 |
| 30 | **R-01** | `ON_TIME` | 153 | **+0.76** | +0.82 | +1.0 | +4.0 | 0/7 | 8.5% | +0.82 |
| 31 | **R-24** | `ON_TIME` | 146 | **+0.75** | +0.84 | +1.0 | +4.0 | 0/7 | 11.0% | +0.84 |
| 32 | **R-28** | `ON_TIME` | 151 | **+0.66** | +0.62 | +1.0 | +4.0 | 0/7 | 9.9% | +0.62 |
| 33 | **R-36** | `ON_TIME` | 132 | **+0.39** | +0.22 | +1.0 | +4.0 | 0/7 | 9.8% | +0.22 |
| 34 | **R-23** | `ON_TIME` | 132 | **+0.17** | +0.11 | +0.0 | +4.0 | 0/7 | 6.1% | +0.11 |
| 35 | **R-04** | `ON_TIME` | 144 | **+0.11** | +0.17 | +0.0 | +4.0 | 0/7 | 9.7% | +0.17 |
| 36 | **R-16** | `ON_TIME` | 146 | **-0.14** | -0.19 | +0.0 | +3.0 | 0/7 | 4.8% | -0.19 |
| 37 | **R-30** | `ON_TIME` | 147 | **-0.46** | -0.38 | -1.0 | +3.0 | 0/7 | 7.5% | -0.38 |
| 38 | **R-13** | `ON_TIME` | 133 | **-0.91** | -0.93 | -1.0 | +3.0 | 0/7 | 6.0% | -0.93 |
| 39 | **R-29** | `ON_TIME` | 151 | **-0.94** | -0.93 | -1.0 | +2.0 | 0/7 | 4.0% | -0.93 |
| 40 | **R-06** | `ON_TIME` | 117 | **-1.54** | -1.45 | -2.0 | +2.0 | 0/7 | 5.1% | -1.45 |
