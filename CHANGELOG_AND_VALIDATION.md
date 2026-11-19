# Refinement validation — 19 November 2026

Baseline commit: `5b3d189`; 37 tests passed before edits. After refinement: **47 tests passed** on Python 3.12.13 (`python -m pytest -q`), including all existing regulatory/data tests and additional search, combined-filter, sorting, full CSV round-trip, empty-export and UI checks. `rules.py`, `prepare_data.py`, scenario JSON and deployment incident CSV are unchanged.

The notebook was reduced from 26 cells to 11 cells (five executable cells), then executed sequentially in a fresh Python kernel with the original source supplied through `DORA_SOURCE_CSV`. Newly executed outputs verify 141,712 events / 36 columns → 24,918 unique incidents and an exact dataframe comparison with committed deployment data. Missing resolution durations: 1,556; valid: 23,362; median: 22.1 hours; mean: 178.171582 hours; SLA met: 15,803 / 24,918 (63.4200177%). Automatic first-download code is documented and hash-checked; this execution used the existing verified source, not the download branch.

Changed: analysis notebook, app layout, README, this validation record, development dependencies, ignore rules and UI tests. Added: `operations.py` (shared filtering/export helpers), its tests, and `.streamlit/config.toml` (restrained theme). Removed: unused `data/dora_scenarios.csv` (JSON is authoritative), and transient `test_results.xml` (historical evidence retained below). No app-generation cells or embedded copies of repository Python files remain in the notebook. No production dependency was added.

UI verification before publication: all three tabs render; literal incident-ID search updates KPIs/charts to one record; CSV control clicked; results appear above collapsed assessment inputs; reference data quality is a readable table. Automated CSV tests compare exported bytes with every filtered row and selected ordering. Browser download filesystem contents were not independently inspected. Automated tests cover all five scenario results, input validation, deadline calculations, combined filters and empty states.

Limits retained: educational screening, no official classification, no automatic recurrence aggregation, reporting submissions, persistence, holiday/entity overrides or local-time/DST automation. This work does not constitute a security audit or legal validation. Historical deployment evidence below is dated evidence, not a new claim for changed UI.

---

## Original MVP validation record

### Changes and validation — 19 November 2026

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

Python 3.12.13, Streamlit 1.50.0, pandas 2.3.3, Plotly 7.1.0, pytest 8.4.2. Command: `python -m pytest -q`. **37 tests passed**, no pytest warnings. This is the pre-refinement baseline; the transient XML has been removed in favour of this retained record and reproducible tests.

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

## Refinement deployment check

After publishing refinement commit `4c95adc`, the existing public URL loaded the updated interface without a new deployment: https://dora-ict-incident-monitor.streamlit.app/. All three tabs were opened successfully. The operations view showed 24,918 incidents, median 22.1 hours, coverage 93.8%, mean 178.2 hours and SLA 63.4%; the payment scenario refreshed to Major indicated above the collapsed inputs; Reference Guide showed the readable data-quality summary. No application exception was visible. All five scenarios and reporting clocks passed automated tests; this post-update browser check was a focused smoke test, not a repeat of every automated boundary test.
