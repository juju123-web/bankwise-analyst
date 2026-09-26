from concurrent.futures import ThreadPoolExecutor
import pytest
from bankwise.access import authorize_server_key, reserve_question

@pytest.mark.parametrize('expected,supplied', [('', ''), ('secret', ''), ('secret','wrong')])
def test_deny_missing_or_wrong_code(expected, supplied):
    with pytest.raises(ValueError):
        authorize_server_key(expected, supplied)

def test_correct_code():
    authorize_server_key('test-code', 'test-code')

def test_budget_is_shared_and_atomic(tmp_path):
    path=tmp_path/'usage.db'
    def attempt(_):
        try:
            reserve_question(path,limit=3,day='2026-09-26')
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(max_workers=5) as pool:
        assert sum(pool.map(attempt,range(10)))==3
    assert reserve_question(path,limit=3,day='2026-09-27')==1
