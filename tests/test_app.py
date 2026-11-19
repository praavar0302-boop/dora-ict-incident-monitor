from pathlib import Path
from streamlit.testing.v1 import AppTest
APP=Path(__file__).resolve().parents[1]/'app.py'

def find(elements,label):
    return next(e for e in elements if e.label==label)

def test_default_and_all_scenarios():
    at=AppTest.from_file(str(APP)).run(timeout=60)
    assert not at.exception
    assert at.metric[0].value=='24,918'
    scenario=find(at.selectbox,'Load a simulated ICT scenario')
    for name in scenario.options[1:]:
        find(at.selectbox,'Load a simulated ICT scenario').select(name).run(timeout=30)
        assert not at.exception
    find(at.selectbox,'Load a simulated ICT scenario').select('Core Retail Payment System Outage').run(timeout=30)
    assert at.error[0].value=='Major indicated'
    find(at.selectbox,'Load a simulated ICT scenario').select('Customer Facing Authentication Service Outage').run(timeout=30)
    assert any(w.value=='Needs review' for w in at.warning)

def test_empty_filter_and_sla():
    at=AppTest.from_file(str(APP)).run(timeout=60)
    find(at.selectbox,'SLA Made Status').select('False Only').run(timeout=30)
    assert not at.exception and at.metric[3].value=='0.0%'
    # Pick a priority then an SLA combination with no results if any available.
    import pandas as pd
    from prepare_data import boolean_series
    d=pd.read_csv(APP.parent/'data/incidents.csv',low_memory=False);d.made_sla=boolean_series(d.made_sla)
    for p in d.priority.unique():
        if not ((d.priority==p)&(d.made_sla==False)).any():
            find(at.multiselect,'Incident Priority').set_value([p]).run(timeout=30)
            assert not at.exception and at.metric[0].value=='0' and at.metric[3].value=='N/A'
            break

def test_deadline_inputs():
    at=AppTest.from_file(str(APP)).run(timeout=60)
    at.text_input[0].set_value('2026-11-19T00:00:00Z')
    at.text_input[1].set_value('2026-11-19T01:00:00Z').run(timeout=30)
    assert not at.exception
    assert any('2026-11-19T05:00:00+00:00' in x.value for x in at.markdown)
    at.text_input[1].set_value('invalid').run(timeout=30)
    assert not at.exception and any('Invalid timestamp' in e.value for e in at.error)

def test_empty_dataset_filter_path(tmp_path):
    import shutil
    import pandas as pd
    for f in ['app.py','rules.py','prepare_data.py']:
        shutil.copy(APP.parent/f,tmp_path/f)
    shutil.copytree(APP.parent/'data',tmp_path/'data')
    data=pd.read_csv(tmp_path/'data/incidents.csv',low_memory=False).head(2).copy()
    data['incident_state']=['Closed','Resolved'];data['made_sla']=[True,False]
    data.to_csv(tmp_path/'data/incidents.csv',index=False)
    at=AppTest.from_file(str(tmp_path/'app.py')).run(timeout=60)
    find(at.multiselect,'Latest Incident State').set_value(['Closed'])
    find(at.selectbox,'SLA Made Status').select('False Only').run(timeout=30)
    assert not at.exception and at.metric[0].value=='0'
    assert at.metric[2].value=='N/A' and at.metric[3].value=='N/A'
    assert any('No incidents match' in x.value for x in at.info)

def test_scenario_reset_and_invalid_input():
    from rules import NUM_FIELDS
    at=AppTest.from_file(str(APP)).run(timeout=60)
    find(at.selectbox,'Load a simulated ICT scenario').select('Core Retail Payment System Outage').run(timeout=30)
    assert find(at.number_input,NUM_FIELDS['member_states']).value==3
    find(at.selectbox,'Load a simulated ICT scenario').select('Customer Facing Authentication Service Outage').run(timeout=30)
    assert find(at.number_input,NUM_FIELDS['member_states']).value==1
    find(at.number_input,NUM_FIELDS['member_states']).set_value(28).run(timeout=30)
    assert not at.exception and any('Invalid screening input' in x.value for x in at.error)
