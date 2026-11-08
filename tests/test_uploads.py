import pytest
from bankwise.uploads import create_dataset, read_csv
from bankwise.sql import execute, schema, QueryError
from bankwise.agent import analyze, OpenAIPlanner, CUSTOM_RULES


def test_custom_schema_and_aggregation():
    data = create_dataset('账户编号;交易金额;渠道\n001;120.5;柜台\n002;;手机\n003;20;柜台'.encode())
    try:
        assert [x['name'] for x in schema(data['db'])] == ['账户编号', '交易金额', '渠道']
        assert execute('SELECT "账户编号" FROM bank_contacts ORDER BY "账户编号"', data['db'])['rows'][0] == ['001']
        assert execute('SELECT SUM("交易金额"), COUNT("交易金额") FROM bank_contacts', data['db'])['rows'] == [[140.5, 2]]
        with pytest.raises(QueryError):
            execute('DELETE FROM bank_contacts', data['db'])
        result = analyze('总额', planner=lambda *a: {'status': 'query', 'sql': 'SELECT SUM("交易金额") AS amount FROM bank_contacts'}, db=data['db'], custom=True)
        assert result['status'] == 'ok'
        assert 'duration' not in str(result['warnings'])
        assert analyze('演示', db=data['db'], custom=True)['status'] == 'clarify'
    finally:
        data['owner'].cleanup()


def test_sessions_do_not_share_data():
    first, second = create_dataset(b'amount\n1'), create_dataset(b'amount\n9')
    try:
        assert execute('SELECT amount FROM bank_contacts', first['db'])['rows'] == [[1]]
        assert execute('SELECT amount FROM bank_contacts', second['db'])['rows'] == [[9]]
    finally:
        first['owner'].cleanup()
        second['owner'].cleanup()


@pytest.mark.parametrize('payload', [b'', b'a,a\n1,2', b'A,a\n1,2', b'a,b\n1', b'a,b\n', b'\xff\xff'])
def test_invalid_upload(payload):
    with pytest.raises(ValueError):
        read_csv(payload)


def test_quoted_identifier_and_text():
    data = create_dataset(b'"a""b",status\n2,unknown\n3,NA')
    try:
        assert execute('SELECT SUM("a""b") FROM bank_contacts', data['db'])['rows'] == [[5]]
        assert execute('SELECT status FROM bank_contacts', data['db'])['rows'] == [['unknown'], ['NA']]
    finally:
        data['owner'].cleanup()


def test_paste_ui_and_dataset_switch():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)
    app.radio(key='dataset_source').set_value('自定义银行数据 / Custom').run()
    app.radio[1].set_value('粘贴 CSV / Paste').run()
    app.text_area(key='pasted_csv').set_value('账户编号,余额\n001,12\n002,25').run()
    assert not app.exception
    assert app.metric[0].value == '2'
    app.text_area(key='sql_input').set_value('SELECT SUM("余额") FROM bank_contacts').run()
    next(b for b in app.button if b.label == '执行 SQL').click().run()
    assert app.session_state['sql_result']['rows'] == [[37]]
    app.text_area(key='pasted_csv').set_value('账户编号,余额\n003,100').run()
    assert not app.exception
    assert app.metric[0].value == '1'
    assert 'sql_result' not in app.session_state
    app.radio(key='dataset_source').set_value('UCI 银行营销演示 / Demo').run()
    assert not app.exception
    assert app.metric[0].value == '41,188'


def test_custom_planner_receives_notes_without_uci_assumptions():
    from types import SimpleNamespace
    import json
    captured = {}
    def respond(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(usage=None, output_text='{"status":"clarify","explanation":"请明确金额单位"}')
    planner = OpenAIPlanner.__new__(OpenAIPlanner)
    planner.model, planner.language, planner.dataset_notes = 'test', 'zh', '每行一笔交易；amount 单位为元。'
    planner.client = SimpleNamespace(responses=SimpleNamespace(create=respond))
    planner.usage = []
    assert planner('总额', [{'name': 'amount', 'type': 'REAL'}])['status'] == 'clarify'
    assert json.loads(captured['input'])['dataset_notes'] == planner.dataset_notes
    assert 'No customer ID, revenue' not in captured['instructions']
    assert 'Use only the supplied schema' in captured['instructions']
    assert captured['store'] is False
