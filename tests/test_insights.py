import pytest
from bankwise.insights import wilson, uncertainty, uncertainty_rows

def test_wilson_known_values():
    lo, hi = wilson(50,100)
    assert lo == pytest.approx(40.383, abs=.01)
    assert hi == pytest.approx(59.617, abs=.01)

def test_wilson_edges():
    assert wilson(0,10)[0]==0
    assert wilson(10,10)[1]==100
    with pytest.raises(ValueError):
        wilson(0,0)

def test_small_sample_and_no_count():
    result = uncertainty({'columns':['observations','subscriptions'], 'rows':[[4,1]]})
    assert result[0]['样本提示']=='小样本，谨慎解读'
    assert uncertainty({'columns':['n'], 'rows':[[3]]})==[]

def test_table_and_chart_share_normalized_intervals():
    table = {'columns':['segment','observations','subscriptions','conversion_pct'],
             'rows':[['A',100,50,50.0]]}
    raw = uncertainty_rows(table)[0]
    shown = uncertainty(table)[0]
    assert raw['ci_low'] == shown['转化率下界 (%)']
    assert raw['ci_high'] == shown['转化率上界 (%)']
    assert raw['observations'] == shown['观察记录数']
