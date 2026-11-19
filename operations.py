"""Shared dashboard filtering, directory ordering and export."""
SORT_COLUMNS = {'Incident ID':'number','Opened at':'opened_at','Resolution duration':'resolution_duration_hours','Priority':'priority','Reassignments':'reassignment_count'}
DIRECTORY_COLUMNS = ['number','opened_at','incident_state','priority','impact','urgency','reassignment_count','made_sla','resolution_duration_hours']

def filter_incidents(data, states=(), priorities=(), sla='All', search=''):
    result=data.copy()
    if states:
        result=result[result.incident_state.isin(states)]
    if priorities:
        result=result[result.priority.isin(priorities)]
    if sla=='True Only':
        result=result[result.made_sla.eq(True)]
    elif sla=='False Only':
        result=result[result.made_sla.eq(False)]
    elif sla=='Unknown':
        result=result[result.made_sla.isna()]
    if search.strip():
        result=result[result.number.astype('string').str.contains(search.strip(),case=False,regex=False,na=False)]
    return result

def incident_directory(data,sort_label='Opened at',descending=True):
    return data.sort_values([SORT_COLUMNS[sort_label]] + ([] if SORT_COLUMNS[sort_label]=='number' else ['number']),ascending=[not descending] + ([] if SORT_COLUMNS[sort_label]=='number' else [True]),na_position='last',kind='stable')[DIRECTORY_COLUMNS].reset_index(drop=True)

def export_csv(data):
    return data.to_csv(index=False).encode('utf-8')
