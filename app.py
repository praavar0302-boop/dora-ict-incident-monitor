import streamlit as st
import pandas as pd
import json
from pathlib import Path
from prepare_data import boolean_series
from operations import filter_incidents, incident_directory, export_csv, SORT_COLUMNS
from rules import assess, deadlines, BOOL_FIELDS, NUM_FIELDS, COUNT_FIELDS
BASE = Path(__file__).resolve().parent
import plotly.express as px

st.set_page_config(
    page_title="DORA ICT Incident Triage & Monitor",
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
    st.error(f"Error loading processed datasets: {e}. Check the prepared incident data and scenario JSON files.")
    st.stop()

st.title("DORA-Informed ICT Incident Monitor")
st.caption("Historical ICT operations and fictional financial-sector screening. Educational MVP; no official classification or compliance determination.")
tab1, tab2, tab3 = st.tabs(["Incident Operations", "DORA Screening", "Reference Guide"])

with tab1:
    st.header("Incident operations")
    st.caption("Public, anonymised UCI data from an IT company. These historical tickets are separate from the fictional financial-sector scenarios.")
    c1, c2, c3 = st.columns(3)
    with c1:
        state_filter = st.multiselect("Latest Incident State", sorted(df_incidents.incident_state.dropna().unique()))
    with c2:
        priority_filter = st.multiselect("Incident Priority", sorted(df_incidents.priority.dropna().unique()))
    with c3:
        sla_filter = st.selectbox("SLA Made Status", ["All", "True Only", "False Only", "Unknown"])
    search = st.text_input("Search incident ID", placeholder="For example, INC0000045")
    filtered_df = filter_incidents(df_incidents, state_filter, priority_filter, sla_filter, search)
    duration = filtered_df.resolution_duration_hours.dropna()
    sla_known = filtered_df.made_sla.dropna()
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Unique Incidents", f"{len(filtered_df):,}")
    k2.metric("Median resolution time", f"{duration.median():.1f} Hours" if len(duration) else "N/A")
    k3.metric("Resolution data coverage", f"{len(duration)/len(filtered_df)*100:.1f}%" if len(filtered_df) else "N/A")
    k4.metric("SLA Met Rate (known outcomes)", f"{sla_known.mean()*100:.1f}%" if len(sla_known) else "N/A")
    mean = f"{duration.mean():.1f} hours" if len(duration) else "N/A"
    st.caption(f"Mean resolution: {mean} · Valid resolution records: {len(duration):,} · Missing: {filtered_df.resolution_duration_hours.isna().sum():,} · Known SLA outcomes: {len(sla_known):,} · Unknown: {filtered_df.made_sla.isna().sum():,}")
    if filtered_df.empty:
        st.info("No incidents match these filters.")
    else:
        v1,v2 = st.columns(2)
        with v1:
            st.subheader("Incidents by priority")
            counts = filtered_df.priority.value_counts().sort_index().rename_axis('Priority').reset_index(name='Incidents')
            st.plotly_chart(px.bar(counts,x='Priority',y='Incidents',color_discrete_sequence=['#334e68']),use_container_width=True)
        with v2:
            st.subheader("Incidents opened by month")
            trend = filtered_df.dropna(subset=['opened_at']).assign(Month=lambda d:d.opened_at.dt.to_period('M')).groupby('Month').size().reset_index(name='Incidents')
            trend['Month'] = trend.Month.astype(str)
            st.plotly_chart(px.line(trend,x='Month',y='Incidents',markers=True,color_discrete_sequence=['#334e68']),use_container_width=True)
    st.subheader("Incident directory")
    sort_label = st.selectbox("Sort incidents by", list(SORT_COLUMNS))
    descending = st.checkbox("Descending order", value=True)
    directory = incident_directory(filtered_df, sort_label, descending)
    st.caption(f"{len(directory):,} matching records. Sort using the controls below or table headers; the CSV uses the controls' order and includes every matching record.")
    st.dataframe(directory,hide_index=True,width='stretch')
    st.download_button("Download filtered incidents (CSV)",data=export_csv(directory),file_name='filtered_incidents.csv',mime='text/csv')


# TAB 2: DORA Assessment Screening Simulator
with tab2:
    st.header("DORA Major Incident Screening Tool")
    st.caption("Preliminary single-incident screening. Unknown facts remain unknown; the responsible incident/risk team must review the evidence.")
    selected = st.selectbox("Load a simulated ICT scenario", ['Custom input'] + [s['name'] for s in df_scenarios])
    scenario = next((s for s in df_scenarios if s['name'] == selected), {})
    if scenario:
        st.write(scenario['system_affected'])
        st.write(scenario['description'])
        with st.expander('Scenario assumptions'):
            st.caption(scenario['assumptions'])
    assessment = st.container()
    with st.expander('Assessment inputs', expanded=False):
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
    with assessment:
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
    with st.expander('Classification and reporting guidance'):
        st.warning("Recurring incidents are not automatically aggregated. Art. 8(2): assess monthly; at least twice in six months, same apparent root cause, collectively meeting major criteria. Exemptions apply to microenterprises and Art. 16(1) entities. A negative single-incident result does not clear recurring incidents.")
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
    st.subheader("Data quality summary")
    q = json.loads((BASE / 'data/data_quality.json').read_text())
    st.dataframe(pd.DataFrame({"Check":["Source events","Source columns","Unique incidents","Missing resolution durations","Invalid parsed timestamps","Negative resolution durations","Unknown SLA outcomes","Latest snapshot ties"],"Result":[f"{q['event_rows']:,}",str(q['source_columns']),f"{q['incident_rows']:,}",f"{q['missing_resolution_duration']:,}",str(sum(q['invalid_datetimes'].values())),str(q['negative_durations']),str(q['unknown_sla']),str(q['incidents_with_snapshot_ties'])]}),hide_index=True,width='stretch')
    st.caption("Resolution time measures ticket opening to recorded resolution; it is not regulatory incident duration or service downtime. All latest records in this historical sample are Closed.")
