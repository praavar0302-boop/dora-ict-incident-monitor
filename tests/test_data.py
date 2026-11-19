from pathlib import Path
import json
import pandas as pd
import pytest
from prepare_data import prepare,boolean_series
ROOT=Path(__file__).resolve().parents[1]

def row(**updates):
    r=dict(number='INC1',incident_state='Closed',sys_mod_count='1',made_sla='False',active='False',priority='3 - Moderate',impact='2 - Medium',urgency='2 - Medium',reassignment_count='0',opened_at='01/01/2026 00:00',sys_updated_at='02/01/2026 00:00',resolved_at='01/01/2026 02:00',closed_at='02/01/2026 00:00')
    r.update(updates);return r

def test_generated_integrity():
    d=pd.read_csv(ROOT/'data/incidents.csv',low_memory=False)
    q=json.loads((ROOT/'data/data_quality.json').read_text())
    assert len(d)==24918 and d.number.nunique()==len(d) and d.number.notna().all()
    assert q['event_rows']==141712 and q['source_columns']==36
    assert q['raw_sha256']=='fd184bbfd62329cfe093e99da2ea7071905f2ead91900b448eb2635870821bef'
    assert q['exact_duplicate_rows']==0
    assert d.resolution_duration_hours.ge(0).sum()==23362
    assert d.resolution_duration_hours.isna().sum()==1556
    t=(pd.to_datetime(d.resolved_at)-pd.to_datetime(d.opened_at)).dt.total_seconds()/3600
    pd.testing.assert_series_equal(d.resolution_duration_hours,t,check_names=False)
    assert (d.incident_state=='Closed').all()

def test_revision_order_numeric_and_whole_snapshot():
    raw=pd.DataFrame([row(sys_mod_count='9',priority='old',sys_updated_at='03/01/2026 00:00'),row(sys_mod_count='10',priority='?',sys_updated_at='02/01/2026 00:00')])
    d,q=prepare(raw)
    assert d.iloc[0].sys_mod_count==10 and pd.isna(d.iloc[0].priority)
    assert not d.iloc[0].made_sla

def test_missing_invalid_and_negative():
    d,q=prepare(pd.DataFrame([row(resolved_at='?',made_sla='?',priority='   '),row(number='INC2',resolved_at='31/12/2025 23:00'),row(number='INC3',resolved_at='invalid')]))
    assert d.resolution_duration_hours.isna().all()
    assert q['negative_durations']==1 and q['invalid_datetimes']['resolved_at']==1
    assert q['unknown_sla']==1 and pd.isna(d.iloc[0].priority)

def test_unresolved_and_tied_snapshots():
    d,q=prepare(pd.DataFrame([row(incident_state='Active'),row(incident_state='Active',priority='second')]))
    assert pd.isna(d.iloc[0].resolution_duration_hours)
    assert d.iloc[0].priority=='second' and d.iloc[0].snapshot_tie

@pytest.mark.parametrize('change',[{'number':'?'},{'sys_mod_count':'?'},{'sys_mod_count':'oops'}])
def test_reject_invalid_identity_or_order(change):
    with pytest.raises(ValueError):prepare(pd.DataFrame([row(**change)]))

def test_boolean_not_string_truthiness():
    s=boolean_series(pd.Series(['False','True','?',None,'oops']))
    assert s.iloc[0]==False and s.iloc[1]==True and s.isna().sum()==3
