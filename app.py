import streamlit as st
import pandas as pd
import json
from pathlib import Path
from prepare_data import boolean_series
from rules import assess, deadlines, BOOL_FIELDS, NUM_FIELDS, COUNT_FIELDS
BASE = Path(__file__).resolve().parent
import plotly.express as px

st.set_page_config(
    page_title="DORA ICT Incident Triage & Monitor",
    page_icon="🛡️",
    layout="wide"
)

# Load processed datasets
@st.cache_data
def load_data(base_path=str(BASE)):
    base = Path(base_path)
    incidents = pd.read_csv(base / 'data/incidents.csv',low_memory=False)
    scenarios = json.loads((base / 'data/dora_scenarios.json').read_text())
    for col in ['opened_at','resolved_at']:
        incidents[col] = pd.to_datetime(incidents[col], errors='coerce')
    incidents['made_sla'] = boolean_series(incidents['made_sla'])
    if incidents['number'].isna().any() or incidents['number'].duplicated().any():
        raise ValueError('Incident IDs must be present and unique')
    return incidents, scenarios

try:
    df_incidents, df_scenarios = load_data(str(BASE))
except Exception as e:
    st.error(f"Error loading processed datasets: {e}. Please ensure data/incidents.csv and data/dora_scenarios.csv exist.")
    st.stop()

st.title("🛡️ DORA-Informed ICT Incident Triage & Reporting Monitor")
st.markdown("""
An operational dashboard and educational screening environment mapped to **DORA Regulation (EU) 2022/2554**
and adopted Delegated Regulations **2024/1772** (classification) and **2025/301** (reporting).
Educational portfolio MVP; no claim of DORA compliance. No regulatory submission or persistent incident tracking.
""")

tab1, tab2, tab3 = st.tabs(["📊 Incident Operations Dashboard", "🔍 DORA Assessment Screening", "📘 Reference Guide"])

# TAB 1: Incident Operations Dashboard
with tab1:
    st.header("Incident Operations Overview")
    st.markdown("Historical, anonymised public UCI ServiceNow dataset from an IT company; not a financial institution incident register.")

    # Filtering sidebar options simulated in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        state_filter = st.multiselect("Latest Incident State", options=df_incidents['incident_state'].dropna().unique().tolist(), default=None)
    with col2:
        priority_filter = st.multiselect("Incident Priority", options=df_incidents['priority'].dropna().unique().tolist(), default=None)
    with col3:
        sla_filter = st.selectbox("SLA Made Status", ["All", "True Only", "False Only"])

    # Apply filters
    filtered_df = df_incidents.copy()
    if state_filter:
        filtered_df = filtered_df[filtered_df['incident_state'].isin(state_filter)]
    if priority_filter:
        filtered_df = filtered_df[filtered_df['priority'].isin(priority_filter)]
    if sla_filter == "True Only":
        filtered_df = filtered_df[filtered_df['made_sla'] == True]
    elif sla_filter == "False Only":
        filtered_df = filtered_df[filtered_df['made_sla'] == False]

    # Key Performance Indicators
    kp1, kp2, kp3, kp4 = st.columns(4)
    kp1.metric("Total Unique Incidents", f"{len(filtered_df):,}")

    closed_count = len(filtered_df[filtered_df['incident_state'] == 'Closed'])
    kp2.metric("Closed Incidents", f"{closed_count:,}")

    avg_res_time = filtered_df['resolution_duration_hours'].mean()
    kp3.metric("Avg. Resolution Duration", f"{avg_res_time:.1f} Hours" if not pd.isna(avg_res_time) else "N/A")

    sla_known = filtered_df['made_sla'].dropna()
    sla_met_pct = sla_known.mean() * 100 if len(sla_known) else None
    kp4.metric("SLA Met Rate (known outcomes)", f"{sla_met_pct:.1f}%" if sla_met_pct is not None else "N/A")
    st.caption(f"Resolution mean uses {filtered_df['resolution_duration_hours'].notna().sum():,} valid resolved/closed records. SLA unknown: {filtered_df['made_sla'].isna().sum():,}. Neither metric establishes DORA compliance.")
    if filtered_df.empty:
        st.info("No incidents match these filters.")

    # Visualizations
    v1, v2 = st.columns(2)
    with v1:
        st.subheader("Incidents by Priority State")
        p_counts = filtered_df['priority'].value_counts().rename_axis('priority').reset_index(name='count')
        fig_p = px.bar(p_counts, x='priority', y='count', color='priority', labels={'count': 'Number of Incidents'})
        st.plotly_chart(fig_p, use_container_width=True)

    with v2:
        st.subheader("Incident Volumes Over Time (Opened Month)")
        filtered_df['opened_month'] = filtered_df['opened_at'].dt.to_period('M')
        trend_df = filtered_df.groupby('opened_month').size().reset_index(name='Incident Count')
        trend_df['opened_month'] = trend_df['opened_month'].astype(str)
        fig_t = px.line(trend_df, x='opened_month', y='Incident Count', markers=True)
        st.plotly_chart(fig_t, use_container_width=True)

    # Table view
    st.subheader("Incident Record Directory (First 100 Rows)")
    st.dataframe(filtered_df[['number', 'incident_state', 'active', 'priority', 'impact', 'urgency', 'reassignment_count', 'made_sla', 'resolution_duration_hours']].head(100), width='stretch')

# TAB 2: DORA Assessment Screening Simulator
with tab2:
    st.header("DORA Major Incident Screening Tool")
    st.info("Educational single-incident screening. Unknown facts remain unknown. Review the evidence with the responsible incident/risk team; this app makes no official classification.")
    selected = st.selectbox("Load a simulated ICT scenario", ['Custom input'] + [s['name'] for s in df_scenarios])
    scenario = next((s for s in df_scenarios if s['name'] == selected), {})
    if scenario:
        st.write(scenario['system_affected'])
        st.write(scenario['description'])
        st.caption(scenario['assumptions'])
    st.caption("Choose Unknown for unestablished facts. Zero means a confirmed zero. Percent denominators must refer to the affected service; daily transaction averages follow Art. 1(2).")
    values = {}
    f1, f2 = st.columns(2)
    for index, (key,label) in enumerate(BOOL_FIELDS.items()):
        with [f1,f2][index % 2]:
            initial = scenario.get(key)
            options = ['Unknown','Yes','No']
            chosen = st.selectbox(label,options,index=0 if initial is None else (1 if initial else 2),key=f'{selected}_{key}')
            values[key] = {'Unknown':None,'Yes':True,'No':False}[chosen]
    st.caption("Data impact in Art. 9(5)(a) includes temporary inaccessibility with adverse business/regulatory consequences. Art. 9(5)(b) is access not covered by (a), with possible data loss; a suspected breach alone is insufficient.")
    for index, (key,label) in enumerate(NUM_FIELDS.items()):
        with [f1,f2][index % 2]:
            initial = scenario.get(key)
            count = key in COUNT_FIELDS
            values[key] = st.number_input(label,min_value=0 if count else 0.0,
                value=None if initial is None else (int(initial) if count else float(initial)),
                step=1 if count else 0.01,key=f'{selected}_{key}',placeholder='Unknown')
    st.caption("Geography counts EU Member States impacted, considering Art. 4 significance; worldwide scope alone is insufficient. Economic loss includes Art. 7 direct/indirect incident costs before recoveries, excluding normal operating/improvement costs.")
    try:
        result = assess(values)
    except ValueError as e:
        st.error(f"Invalid screening input: {e}")
    else:
        {'Major indicated':st.error,'Needs review':st.warning,'Single-incident major criteria not met':st.info}[result['status']](result['status'])
        label = lambda v: 'Met' if v is True else ('Unknown' if v is None else 'Not met')
        st.write(f"Criticality gate (Art. 6): {label(result['criticality_gate'])}. Special access trigger (Art. 9(5)(b)): {label(result['access_9_5_b'])}.")
        st.dataframe(pd.DataFrame([{'Criterion':k,'Result':label(v)} for k,v in result['criteria'].items()]),hide_index=True,width='stretch')
        st.caption(f"{result['met_count']} of six ordinary categories met; {result['unknown_count']} unknown. Art. 8 requires the criticality gate plus the special access trigger OR at least two ordinary categories. Multiple client/transaction triggers still count as one category.")
    st.warning("Recurring incidents are not automatically aggregated. Art. 8(2): assess monthly; at least twice in six months, same apparent root cause, collectively meeting major criteria. Exemptions apply to microenterprises and Art. 16(1) entities. A negative single-incident result does not clear recurring incidents.")
    st.subheader("Reporting deadline helper")
    st.markdown("Initial: as early as possible, within **4 hours after major classification**, normally capped at **24 hours after awareness**. If classified after 24 hours, within 4 hours of that later classification. Intermediate: **72 hours after initial submission**; update without undue delay and when regular activities recover. Final: **one calendar month after the latest intermediate submission**.")
    st.caption("Unadjusted deadlines only. Art. 5(4) permits certain weekend/bank-holiday deadlines to move to noon next working day. Initial/intermediate exceptions and competent-authority exclusions apply under Art. 5(5)-(6). No extension is assumed here; verify entity type, local calendar and authority decisions. If unable to report on time, notify the authority by the deadline with reasons.")
    with st.expander("Calculate unadjusted deadlines (explicit timezone required)"):
        times = {}
        for key, text in [('awareness','Awareness'),('classification','Major classification'),('initial','Actual initial submission'),('intermediate','Latest actual intermediate submission')]:
            times[key] = st.text_input(text + ' — ISO 8601 with timezone offset',placeholder='2026-11-19T12:00:00+01:00',key='time_'+key)
        try:
            due = deadlines(**times)
            for name, value in due.items():
                st.write(name.replace('_',' ')+': '+(value.isoformat() if value is not None else 'Awaiting required timestamps'))
        except (ValueError,TypeError) as e:
            st.error(f'Invalid timestamp: {e}')
    st.caption("Keep an internal log and escalate indicated major incidents promptly. Client communications under DORA Art. 19(3) depend on impact on clients' financial interests; notifications are not sent by this app.")

with tab3:
    st.header("Regulatory Reference Framework")
    st.markdown("""
- [DORA — Regulation (EU) 2022/2554, Arts. 17–20](https://eur-lex.europa.eu/eli/reg/2022/2554/oj/eng)
- [Delegated Regulation (EU) 2024/1772, Arts. 1–9](https://eur-lex.europa.eu/eli/reg_del/2024/1772/oj/eng): classification criteria, six materiality categories and criticality gate.
- [Delegated Regulation (EU) 2025/301, Art. 5](https://eur-lex.europa.eu/eli/reg_del/2025/301/oj/eng): reporting clocks, later classification and holiday exceptions.
- [Implementing Regulation (EU) 2025/302](https://eur-lex.europa.eu/eli/reg_impl/2025/302/oj/eng): official reporting forms/procedures; this MVP does not implement or submit them.

**Limitations:** No automated recurring-incident aggregation, authority submission, alert scheduling, persistence, entity-scope determination, or bank-holiday extension calculation. The historical ticket dataset lacks DORA client denominators, downtime, criticality evidence and reporting timestamps; it is used only for operational analysis. Fictional scenarios are kept separate. Inputs are not saved by this app.

**Data attribution:** Amaral, C., Fantinato, M., & Peres, S. (2018), Incident management process enriched event log, UCI Machine Learning Repository, [doi:10.24432/C57S4H](https://doi.org/10.24432/C57S4H), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Anonymised public data from an IT company; not the user's organisation. Preprocessing selects whole latest snapshots by numeric revision count, then update timestamp and original row order; ties are flagged. Unknown outcomes and invalid resolution durations are excluded from the relevant means.
""")
    with st.expander("Dataset quality audit"):
        st.json(json.loads((BASE / 'data/data_quality.json').read_text()))
