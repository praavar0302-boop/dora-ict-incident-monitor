"""Single-incident screening, EU 2024/1772 Arts 6,8,9; not a compliance decision."""
from datetime import timedelta
from decimal import Decimal
import math
import pandas as pd

BOOL_FIELDS = {
    'critical_function': 'ICT supporting a critical or important function affected (Art. 6(a))',
    'regulated_service': 'Authorised, registered or supervised financial service affected (Art. 6(b))',
    'malicious_access': 'Successful, malicious AND unauthorised system access (Art. 6(c))',
    'access_may_cause_loss': 'That access may result in data losses (Art. 9(5)(b))',
    'relevant_clients': 'Relevant clients or financial counterparts affected (Arts 1(3), 9(1)(f))',
    'media': 'Incident reflected in media (Art. 2(a))',
    'complaints': 'Repetitive complaints from different clients/counterparts on client-facing services or critical relationships (Art. 2(b))',
    'regulatory_failure': 'Unable or likely unable to meet regulatory requirements (Art. 2(c))',
    'material_client_loss': 'Likely loss of clients/counterparts materially affecting business (Art. 2(d))',
    'data_adverse': 'Data availability/authenticity/integrity/confidentiality impact adversely affects business objectives or regulatory obligations (Art. 9(5)(a))',
}
NUM_FIELDS = {
    'clients': 'Affected clients', 'total_clients': 'All clients using affected service',
    'counterparts': 'Affected financial counterparts', 'total_counterparts': 'All financial counterparts related to affected service',
    'transactions': 'Affected transaction count', 'daily_transactions': 'Daily average transaction count for affected service',
    'transaction_value': 'Affected transaction value (EUR)', 'daily_value': 'Daily average transaction value for affected service (EUR)',
    'duration_hours': 'Incident duration (hours; Art. 3)',
    'downtime_minutes': 'Downtime of ICT supporting critical/important functions (minutes)',
    'member_states': 'Number of EU Member States impacted (Art. 4)',
    'economic_loss': 'Incurred or likely total costs/losses (EUR; Art. 7, before recoveries)',
}
COUNT_FIELDS = {'clients','total_clients','counterparts','total_counterparts','transactions','member_states'}

def tri_or(*values):
    return True if True in values else (None if None in values else False)

def tri_and(*values):
    return False if False in values else (None if None in values else True)

def gt(value, threshold):
    return None if value is None else Decimal(str(value)) > Decimal(str(threshold))

def ratio(affected, total, threshold):
    if affected is None or total is None or total == 0:
        return None
    return Decimal(str(affected)) > Decimal(str(total)) * Decimal(str(threshold))

def assess(values):
    v = {k: values.get(k) for k in list(BOOL_FIELDS) + list(NUM_FIELDS)}
    for k in BOOL_FIELDS:
        if v[k] is not None and type(v[k]) is not bool:
            raise ValueError(f'{k}: use True, False or None')
    for k in NUM_FIELDS:
        if v[k] is not None:
            if isinstance(v[k], bool) or not isinstance(v[k], (float,int)) or not math.isfinite(v[k]) or v[k] < 0:
                raise ValueError(f'{k}: expected a finite non-negative number or unknown')
            if k in COUNT_FIELDS and v[k] != int(v[k]):
                raise ValueError(f'{k}: expected a whole number')
    if v['member_states'] is not None and v['member_states'] > 27:
        raise ValueError('member_states cannot exceed 27')
    for a,b in [('clients','total_clients'),('counterparts','total_counterparts')]:
        if v[a] is not None and v[b] is not None and v[a] > v[b]:
            raise ValueError(f'{a} cannot exceed {b}')
    gate = tri_or(v['critical_function'],v['regulated_service'],v['malicious_access'])
    # Art. 9(5)(b) expressly excludes access covered by Art. 9(5)(a).
    access_b = tri_and(v['malicious_access'],v['access_may_cause_loss'],
                       None if v['data_adverse'] is None else not v['data_adverse'])
    criteria = {
        'Clients, counterparts and transactions — Art. 9(1)': tri_or(
            gt(v['clients'],100000),ratio(v['clients'],v['total_clients'],.1),
            ratio(v['counterparts'],v['total_counterparts'],.3),
            ratio(v['transactions'],v['daily_transactions'],.1),
            ratio(v['transaction_value'],v['daily_value'],.1),v['relevant_clients']),
        'Reputation — Art. 9(2)': tri_or(v['media'],v['complaints'],v['regulatory_failure'],v['material_client_loss']),
        'Duration / downtime — Art. 9(3)': tri_or(gt(v['duration_hours'],24),tri_and(v['critical_function'],gt(v['downtime_minutes'],120))),
        'Geographical spread — Art. 9(4)': None if v['member_states'] is None else v['member_states'] >= 2,
        'Data losses — Art. 9(5)(a)': v['data_adverse'],
        'Economic impact — Art. 9(6)': gt(v['economic_loss'],100000),
    }
    met = sum(x is True for x in criteria.values())
    unknown = sum(x is None for x in criteria.values())
    two = True if met >= 2 else (None if met + unknown >= 2 else False)
    major = tri_and(gate,tri_or(access_b,two))
    return {'status': 'Major indicated' if major is True else ('Needs review' if major is None else 'Single-incident major criteria not met'),
            'major':major,'criticality_gate':gate,'access_9_5_b':access_b,'criteria':criteria,
            'met_count':met,'unknown_count':unknown}

def deadlines(awareness=None, classification=None, initial=None, intermediate=None):
    """Unadjusted Art. 5 deadlines, UTC; no holiday/entity extension assumed."""
    parsed = {}
    for name,value in [('awareness',awareness),('classification',classification),('initial',initial),('intermediate',intermediate)]:
        if value is None or value == '':
            parsed[name] = None
            continue
        t = pd.Timestamp(value)
        if t.tzinfo is None:
            raise ValueError(f'{name}: timezone offset required')
        parsed[name] = t.tz_convert('UTC')
    a,c,i,m = [parsed[k] for k in ('awareness','classification','initial','intermediate')]
    for earlier,later,label in [(a,c,'classification before awareness'),(c,i,'initial before classification'),(i,m,'intermediate before initial')]:
        if earlier is not None and later is not None and later < earlier:
            raise ValueError(label)
    due = None
    if a is not None and c is not None:
        due = c + timedelta(hours=4)
        if c <= a + timedelta(hours=24):
            due = min(due,a + timedelta(hours=24))
    return {'initial_due_utc':due,
            'intermediate_due_utc':i + timedelta(hours=72) if i is not None else None,
            'final_due_utc':m + pd.DateOffset(months=1) if m is not None else None}
