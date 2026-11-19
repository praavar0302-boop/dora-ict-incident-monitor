import io
import pandas as pd
import pytest
from operations import filter_incidents,incident_directory,export_csv,SORT_COLUMNS
from prepare_data import boolean_series
from pathlib import Path

@pytest.fixture
def data():
    d=pd.read_csv(Path(__file__).resolve().parents[1]/'data/incidents.csv',low_memory=False)
    d['made_sla']=boolean_series(d.made_sla)
    d['opened_at']=pd.to_datetime(d.opened_at)
    return d

def test_metrics_baseline(data):
    assert data.resolution_duration_hours.isna().sum()==1556
    assert data.resolution_duration_hours.median()==22.1
    assert data.made_sla.sum()==15803
    assert data.made_sla.eq(False).sum()==9115
    assert data.made_sla.mean()==pytest.approx(15803/24918)

def test_literal_search_and_combined_filters(data):
    match=filter_incidents(data,search=' inc0000045 ')
    assert match.number.tolist()==['INC0000045']
    assert filter_incidents(data,search='.*').empty
    result=filter_incidents(data,['Closed'],['2 - High'],'False Only')
    assert len(result)==406
    assert result.priority.eq('2 - High').all() and result.made_sla.eq(False).all()

@pytest.mark.parametrize('label',SORT_COLUMNS)
def test_sorted_export_all_matching_records(data,label):
    directory=incident_directory(filter_incidents(data,priorities=['4 - Low']),label,False)
    assert len(directory)==774
    assert directory[SORT_COLUMNS[label]].dropna().is_monotonic_increasing
    exported=pd.read_csv(io.BytesIO(export_csv(directory)))
    assert exported.number.tolist()==directory.number.tolist()
    assert len(exported)==774

def test_empty_export_has_headers(data):
    directory=incident_directory(filter_incidents(data,search='does-not-exist'))
    assert pd.read_csv(io.BytesIO(export_csv(directory))).empty

def test_unknown_sla_not_false(data):
    data=data.head(3).copy();data['made_sla']=pd.Series([True,False,pd.NA],dtype='boolean')
    assert len(filter_incidents(data,sla='Unknown'))==1
    assert len(filter_incidents(data,sla='False Only'))==1
