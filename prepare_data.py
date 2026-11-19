"""Deterministic event-to-incident preparation; no regulatory metrics inferred."""
from pathlib import Path
import argparse
import hashlib
import json
import pandas as pd

TIME_COLS = ['opened_at','sys_updated_at','resolved_at','closed_at']
REQUIRED = ['number','incident_state','sys_mod_count','made_sla','active','priority','impact','urgency','reassignment_count'] + TIME_COLS

def boolean_series(s):
    return s.astype('string').str.strip().str.lower().map({'true':True,'false':False}).astype('boolean')

def prepare(raw):
    missing = sorted(set(REQUIRED)-set(raw.columns))
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    p = raw.copy().replace(r'^\s*(?:\?|)\s*$',pd.NA,regex=True)
    if p['number'].isna().any():
        raise ValueError('Missing incident identifier')
    p['number'] = p['number'].astype('string').str.strip()
    p['_source_row'] = range(len(p))
    audit = {'event_rows':len(raw),'source_columns':len(raw.columns),'exact_duplicate_rows':int(raw.duplicated().sum()),
             'missing_by_column':{k:int(v) for k,v in p[raw.columns].isna().sum().items()},'invalid_datetimes':{}}
    for col in TIME_COLS:
        original = p[col]
        p[col] = pd.to_datetime(original,format='%d/%m/%Y %H:%M',errors='coerce')
        audit['invalid_datetimes'][col] = int((original.notna() & p[col].isna()).sum())
    for col in ['sys_mod_count','reassignment_count']:
        p[col] = pd.to_numeric(p[col],errors='coerce')
    if p['sys_mod_count'].isna().any() or (p.sys_mod_count < 0).any() or (p.sys_mod_count % 1 != 0).any():
        raise ValueError('Missing/invalid revision count: cannot reliably select latest snapshot')
    for col in ['made_sla','active']:
        p[col] = boolean_series(p[col])
    # ServiceNow sys_mod_count orders revisions; clock timestamps can be out of order.
    # Preserve a whole snapshot (not groupby.last(), which splices non-null values).
    ordered = p.sort_values(['number','sys_mod_count','sys_updated_at','_source_row'],na_position='first',kind='stable')
    out = ordered.drop_duplicates('number',keep='last').copy()
    out['snapshot_tie'] = out['number'].isin(p.loc[p.duplicated(['number','sys_mod_count','sys_updated_at'],keep=False),'number'])
    out['event_count'] = out['number'].map(p.groupby('number').size())
    duration = (out.resolved_at-out.opened_at).dt.total_seconds()/3600
    out['duration_invalid'] = duration.lt(0)
    out['resolution_duration_hours'] = duration.where(duration.ge(0) & out.incident_state.isin(['Resolved','Closed']))
    audit.update(incident_rows=len(out),unknown_sla=int(out.made_sla.isna().sum()),
                 negative_durations=int(out.duration_invalid.sum()),missing_resolution_duration=int(out.resolution_duration_hours.isna().sum()),
                 incidents_with_snapshot_ties=int(out.snapshot_tie.sum()),
                 latest_states={str(k):int(v) for k,v in out.incident_state.value_counts(dropna=False).items()},
                 mean_resolution_hours=float(out.resolution_duration_hours.mean()) if out.resolution_duration_hours.notna().any() else None,
                 median_resolution_hours=float(out.resolution_duration_hours.median()) if out.resolution_duration_hours.notna().any() else None)
    return out.drop(columns='_source_row').reset_index(drop=True),audit

def build(path,output_dir):
    path=Path(path); dest=Path(output_dir);dest.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(path,low_memory=False,keep_default_na=False)
    out,audit=prepare(raw)
    audit['raw_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    out.to_csv(dest/'incidents.csv',index=False)
    (dest/'data_quality.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))
    return out,audit

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('source');a.add_argument('--output-dir',default='data')
    args=a.parse_args();build(args.source,args.output_dir)
