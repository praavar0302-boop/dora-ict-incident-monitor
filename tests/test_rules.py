import json
from pathlib import Path
import pytest
from rules import assess,deadlines,BOOL_FIELDS,NUM_FIELDS

def base(**updates):
    v={k:False for k in BOOL_FIELDS};v.update({k:0 for k in NUM_FIELDS})
    v.update(total_clients=1000000,total_counterparts=100,daily_transactions=100000,daily_value=1000000,critical_function=True)
    v.update(updates);return v

@pytest.mark.parametrize('field,edge,above',[
 ('clients',100000,100001),('economic_loss',100000,100000.01),
 ('duration_hours',24,24.01),('downtime_minutes',120,120.01),
 ('counterparts',30,31),('transactions',10000,10001),('transaction_value',100000,100000.01),
 ('member_states',1,2)])
def test_thresholds(field,edge,above):
    # Add reputation as exactly one independent category.
    assert assess(base(media=True,**{field:edge}))['major'] is False
    assert assess(base(media=True,**{field:above}))['major'] is True

def test_client_relative_boundary():
    assert assess(base(total_clients=100,clients=10,media=True))['major'] is False
    assert assess(base(total_clients=100,clients=11,media=True))['major'] is True

def test_categories_are_not_subthreshold_counts():
    r=assess(base(clients=100001,transactions=20000,counterparts=40))
    assert r['met_count']==1 and r['major'] is False
    r=assess(base(duration_hours=25,downtime_minutes=121))
    assert r['met_count']==1 and r['major'] is False

def test_gate_and_access():
    assert assess(base(critical_function=False,media=True,economic_loss=200000))['major'] is False
    assert assess(base(critical_function=False,regulated_service=True,media=True,economic_loss=200000))['major'] is True
    assert assess(base(critical_function=False,malicious_access=True,access_may_cause_loss=True))['major'] is True
    # Adverse data effect falls under 9(5)(a), so no special (b) shortcut.
    assert assess(base(malicious_access=True,access_may_cause_loss=True,data_adverse=True))['major'] is False
    assert assess(base(malicious_access=True,access_may_cause_loss=True,data_adverse=True,media=True))['major'] is True
    assert assess(base(malicious_access=True,access_may_cause_loss=False))['major'] is False

def test_critical_downtime_requirement():
    r=assess(base(critical_function=False,regulated_service=True,downtime_minutes=121,media=True))
    assert r['major'] is False

def test_unknowns_and_zero_denominators():
    assert assess({})['major'] is None
    assert assess(base(media=True,clients=None))['major'] is None
    assert assess(base(media=True,total_clients=0))['major'] is None
    assert assess(base(media=True,total_clients=None,economic_loss=100001))['major'] is True
    assert assess(base(critical_function=False,regulated_service=False,malicious_access=False,clients=None))['major'] is False

@pytest.mark.parametrize('field,value',[('clients',-1),('economic_loss',float('nan')),('economic_loss',float('inf')),('member_states',28),('member_states',1.5),('critical_function','No'),('clients',True)])
def test_invalid(field,value):
    with pytest.raises(ValueError):assess(base(**{field:value}))

def test_inconsistent_denominator():
    with pytest.raises(ValueError):assess(base(clients=101,total_clients=100))

def test_five_scenarios():
    data=json.loads((Path(__file__).resolve().parents[1]/'data/dora_scenarios.json').read_text())
    assert [assess(s)['status'] for s in data]==['Major indicated','Needs review','Major indicated','Needs review','Major indicated']

def test_reporting_clocks():
    a='2026-11-19T00:00:00Z'
    assert deadlines(a,'2026-11-19T01:00:00Z')['initial_due_utc'].isoformat()=='2026-11-19T05:00:00+00:00'
    assert deadlines(a,'2026-11-19T23:00:00Z')['initial_due_utc'].isoformat()=='2026-11-20T00:00:00+00:00'
    assert deadlines(a,'2026-11-20T00:00:00Z')['initial_due_utc'].isoformat()=='2026-11-20T00:00:00+00:00'
    assert deadlines(a,'2026-11-20T00:00:01Z')['initial_due_utc'].isoformat()=='2026-11-20T04:00:01+00:00'
    r=deadlines(a,'2026-11-19T01:00:00Z','2026-11-19T02:00:00Z','2026-11-22T02:00:00Z')
    assert r['intermediate_due_utc'].isoformat()=='2026-11-22T02:00:00+00:00'
    assert r['final_due_utc'].isoformat()=='2026-12-22T02:00:00+00:00'

def test_month_end_and_timezone():
    assert deadlines(intermediate='2028-01-31T12:00:00+01:00')['final_due_utc'].isoformat()=='2028-02-29T11:00:00+00:00'
    assert deadlines(intermediate='2027-01-31T12:00:00Z')['final_due_utc'].day==28
    assert deadlines()['initial_due_utc'] is None
    with pytest.raises(ValueError):deadlines(awareness='2026-11-19T00:00:00')
    with pytest.raises(ValueError):deadlines('2026-11-19T12:00:00Z','2026-11-19T11:00:00Z')
