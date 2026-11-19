# DORA-Informed ICT Incident Monitor

**Live app:** https://dora-ict-incident-monitor.streamlit.app/

Public deployment verified on 19 November 2026 in Chrome Incognito without authentication. All three tabs loaded; the five fictional scenarios returned the expected results (SCN-01/03/05: Major indicated; SCN-02/04: Needs review). The operational dashboard showed 24,918 incidents, 178.2-hour mean resolution and 63.4% SLA-met rate, matching the prepared data. The public data-quality audit showed the expected source SHA-256 and 1,556 missing resolution durations. No application exception or visible credentials/private incident information was observed during these checks. This was a functional and visible-exposure check, not a penetration test or legal-compliance assessment.

Cloud runtime: Python 3.12.16, Streamlit 1.50.0. The hosting platform automatically replaced PyArrow 26.0.1 with 24.0.0 during provisioning. No application-code changes were needed for deployment.

Educational portfolio MVP with three tabs: historical operations dashboard, single-incident screening and reference guide. **Not a claim or certification of DORA compliance.** No authority submissions, live monitoring, saved case management or scheduled alerts.

## Run

Use Python 3.12. From the repository root:

```sh
pip install -r requirements.txt
streamlit run app.py
```

The prepared dataset is included. No Google Drive, Colab, external API keys or secrets are required at runtime.

## Classification

Rules are in `rules.py`, separated from the existing Streamlit dashboard so they can be tested. Delegated Regulation (EU) 2024/1772, Article 8(1), requires the Article 6 criticality gate **and** either Article 9(5)(b), or at least two other Article 9 materiality categories. Criticality is a gate, not one of the two categories.

| Category | Implemented threshold |
|---|---|
| Clients / counterparts / transactions, Art. 9(1) | Any: affected clients >10% of service clients or >100,000; counterparts >30%; transaction count or value >10% of daily average for affected service; relevant clients/counterparts affected. All count as one category. |
| Reputation, Art. 9(2) | Any of the four Article 2 conditions. |
| Duration / downtime, Art. 9(3) | Incident >24h, or downtime >2h for ICT supporting critical/important functions. One category. |
| Geography, Art. 9(4) | Impact in at least two EU Member States, assessed under Article 4. |
| Data, Art. 9(5)(a) | Adverse business/regulatory effect of availability, authenticity, integrity or confidentiality loss. |
| Economic, Art. 9(6) | Costs/losses exceeded or likely to exceed EUR 100,000, under Article 7 before recoveries. |

Article 9(5)(b) special path requires successful, malicious AND unauthorised system access, not covered by (a), that may cause data losses. A suspicion alone does not meet it. The gate can be met through ICT supporting critical/important functions, a regulated financial service, or successful malicious unauthorised access (Article 6(a)-(c)).

Unknowns are not filled with zeros or False. The result is `Needs review` where missing evidence could change the conclusion. Zero denominator produces an unknown ratio, not division by zero. Invalid, negative, non-finite or inconsistent inputs are rejected. Counts and EU Member State counts are validated.

## Reporting clocks

Delegated Regulation (EU) 2025/301, Article 5:

- Initial notification as early as possible, within four hours of major classification, normally no later than 24 hours from awareness. Later classification after those 24 hours permits four hours from later classification.
- Intermediate within 72 hours of actual initial submission. Updates without undue delay and when regular activities recover.
- Final within one calendar month of actual latest intermediate submission, not 30 days from incident detection.
- Notify the competent authority by the applicable deadline, with reasons, if reporting on time is impossible.

The helper calculates unadjusted UTC deadlines with explicit timezone offsets and validates chronology. It does **not** apply Article 5(4)-(6) weekend/bank-holiday extensions or entity/authority exceptions. Calendar months are calculated in UTC; confirm national/local time conventions and DST treatment for operational use. Missing clock origins leave the corresponding deadline unknown.

## Data preparation and provenance

Dataset: Amaral, C., Fantinato, M., & Peres, S. (2018), *Incident management process enriched event log*. UCI Machine Learning Repository. https://doi.org/10.24432/C57S4H. License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This project adapts the public data through cleaning and incident-level snapshot selection. The data came from an IT company, not a financial institution or the user's organisation.

The source file SHA-256 was read in the live Colab runtime and independently matched to UCI: `fd184bbfd62329cfe093e99da2ea7071905f2ead91900b448eb2635870821bef`.

`prepare_data.py` normalises `?`, blanks and nulls; parses source dates with explicit day-first format; sorts numeric revision counts, then update time and stable original row order; selects a whole latest snapshot; and flags ties. It preserves unknown fields instead of splicing older non-null values into a new snapshot. Missing identifiers or revision order are rejected. Resolution duration is calculated only for resolved/closed records with valid non-negative opened-to-resolved intervals. It is **not** DORA incident duration or downtime. SLA rate excludes unknown outcomes and shows its denominator/unknown count. Empty filters show N/A.

```sh
python prepare_data.py /path/to/incident_event_log.csv --output-dir data
pip install -r requirements-dev.txt
python -m pytest -q
```

The public event data has 141,712 records / 36 columns and 24,918 incident IDs. The generated incident data has one row per ID. All latest records in this historical sample are Closed; that is not a claim about live operations. There are 1,556 missing usable resolution durations. Detailed values are in `data/data_quality.json`.

The original five fictional scenarios are retained. JSON supplies the screening fields; the original CSV is kept for reference. Additional unprovided facts remain unknown. The original critical-service flag is explicitly interpreted as ICT supporting a critical/important function for these fictional examples. Global impact does not establish an EU Member State count. SCN-01/03/05 indicate major; SCN-02/04 require review with the available facts.

## Scope limits

- Recurring-incident aggregation (Art. 8(2)) is **manual**: at least twice in six months, same apparent root cause and collectively major criteria, assessed monthly, subject to microenterprise/Art. 16(1) exclusions. A negative individual result does not clear recurrence.
- Financial entity applicability, evidential judgements, reference-period estimates, regulatory scope and competent authority are user responsibilities.
- Dataset contains no substantiated regulatory client denominators, downtime, criticality, malicious-access assessments or reporting timestamps. Historical tickets are not automatically classified.
- No regulatory forms, submission, significant-cyber-threat classifier, persistence, access control, production incident handling or notification service.
- User inputs are not explicitly persisted by this code. A public Community Cloud app is intended for fictional examples; no confidentiality assessment of the hosting platform was performed.

## Deploy to Streamlit Community Cloud

1. Put these files at the repository root with the `data/` folder intact.
2. At https://share.streamlit.io choose Create app, select the GitHub repository and `main` branch, entry point `app.py`.
3. Set Python **3.12** in Advanced settings. No secrets are needed.
4. Deploy; verify dashboard rendering, a major scenario, a needs-review scenario, an empty filter and the reporting helper.

## Official references

- [Regulation (EU) 2022/2554](https://eur-lex.europa.eu/eli/reg/2022/2554/oj/eng), Arts. 17–20.
- [Delegated Regulation (EU) 2024/1772](https://eur-lex.europa.eu/eli/reg_del/2024/1772/oj/eng), Arts. 1–9.
- [Delegated Regulation (EU) 2025/301](https://eur-lex.europa.eu/eli/reg_del/2025/301/oj/eng), Art. 5.
- [Implementing Regulation (EU) 2025/302](https://eur-lex.europa.eu/eli/reg_impl/2025/302/oj/eng), official forms/procedures, outside MVP implementation.
