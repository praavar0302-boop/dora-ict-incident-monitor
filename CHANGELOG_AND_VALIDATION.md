# Changes and validation — 19 November 2026

## Changes

- Preserved the operations dashboard, scenario selector, interactive screening and reference tabs.
- Replaced incorrect 50,000-client threshold with >100,000 / >10% alternatives; added counterparts, transaction count/value and relevant-client alternatives, grouped as one category.
- Implemented the Article 6 criticality gate separately; ordinary classification requires two categories. Added reputation, geographic impact in EU Member States, duration and adverse data effects. Implemented the qualified Art. 9(5)(b) access path, excluding cases covered by (a).
- Unknown values remain unknown; added Needs review results, ratio-denominator validation and rejection of invalid numbers. Global geography is no longer silently reset to single-state impact or assumed cross-EU.
- Replaced the incorrect four-hours-from-detection statement; implemented awareness/classification clocks, late classification, 72-hour intermediate and calendar-month final deadline origins. Documented holiday/entity/authority exceptions; no extension is assumed.
- Kept the five fictional scenarios with explicit interpretations and missing facts; did not manufacture client/transaction denominators or EU geography.
- Normalised ?, blanks and nulls; numeric revision sorting and stable whole-row snapshot selection; ties flagged, missing identifiers/revisions rejected. Replaced exploratory groupby.last() snapshot splicing.
- Kept 24,918 incidents. On this source the revised snapshot ordering selects the same final revision as the previous timestamp-first ordering (zero differences).
- Restricted resolution averages to valid resolved/closed observations. Missing durations remain missing; not inferred from closure time. SLA rates use known boolean outcomes; empty subsets show N/A. No regulatory metrics are inferred from ticket resolution or SLA.
- Corrected dataset attribution: public anonymised UCI IT-company data, not the user's organisation or a bank. Added CC BY 4.0 attribution.
- Pinned runtime dependencies, made paths independent of working directory, made cache keys include dataset directory, and regenerated app/data/notebook packaging. Bundle generation fails if required files are absent.
- Removed references to adopted delegated regulations as Joint Draft RTS. Added official sources and explicit MVP limitations.

## Executed validation

Python 3.12.13, Streamlit 1.50.0, pandas 2.3.3, Plotly 7.1.0, pytest 8.4.2. Command: `python -m pytest -q`. **37 tests passed**, no pytest warnings (see `test_results.xml`).

Coverage includes each material threshold at and above the boundary; grouped category counting; criticality gate alternatives; special access versus adverse-data path; unknowns; zero denominators; negative/NaN/infinite values; inconsistent affected-client counts; all five scenarios; early/late/exact-24h reporting clocks; 72h origin; leap-year/month-end final deadlines; explicit timezone and chronology validation; whole-row selection; numeric 9-to-10 revision ordering with conflicting timestamps; placeholder/blank/boolean handling; missing/invalid/negative resolution times; tied snapshots; latest-ID integrity; Streamlit initial rendering, all scenarios, resets, SLA filters, empty results, invalid screening inputs and reporting-helper interactions.

### Data evidence

The raw CSV hash was read in the existing live Colab runtime and matches the independently downloaded official UCI file: `fd184bbfd62329cfe093e99da2ea7071905f2ead91900b448eb2635870821bef`.

| Check | Result |
|---|---:|
| Source records / columns | 141,712 / 36 |
| Unique incident IDs / generated rows | 24,918 / 24,918 |
| Exact duplicate source rows | 0 |
| Invalid non-missing parsed operational timestamps | 0 |
| Negative resolution durations | 0 |
| Missing usable incident resolution durations | 1,556 |
| Valid resolution observations | 23,362 |
| Latest snapshot ties | 0 |
| Unknown latest SLA outcomes | 0 |
| Latest state Closed | 24,918 |
| Mean / median valid resolution hours | 178.171582 / 22.1 |

Original notebook app.py, scenarios and processed-file existence were inspected in the runtime. Original app.py SHA-256: `de9c4e0a731176bbbe9ade206be34503d777cafe2d8998de8bc13c1091d3115c`. Changes were based on that inspected app and the notebook generator, not a replacement design.

## Unverified / excluded

- No claim of DORA compliance or external legal validation. Entity applicability, factual judgements and competent-authority reporting decisions are not verified.
- No automatic aggregation of recurring incidents or significant-cyber-threat classifier.
- Holiday calendars, entity exceptions, authority overrides and local/DST treatment are not automated; displayed deadlines are unadjusted UTC calculations.
- No forms/submissions under 2025/302, client notification, persistence, real-time feed, scheduler or access-control testing.
- Local AppTest execution is not proof of a public deployment. Cloud build, Linux runtime and anonymous public access must be verified separately after deployment; no public URL is claimed by this report.
- Full exploratory Colab Run all has not been rerun during local validation. The rewritten generator and tests are self-contained for the runtime, but cloud/Colab execution is a separate check.

Official legal sources and implementation scope are linked in README.md and the app's Reference Guide.
