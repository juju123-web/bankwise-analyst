import pytest
from bankwise.insights import wilson, uncertainty

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
