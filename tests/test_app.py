from pathlib import Path
import json
import pytest
from streamlit.testing.v1 import AppTest
from bankwise.data import DB

@pytest.mark.skipif(not DB.exists(), reason='Run python -m bankwise.data for integration tests')
def test_demo_ui():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)
    assert not app.exception
    assert app.metric[0].value == '41,188'
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state['analysis']['status']=='ok'
    app.selectbox[0].select('revenue').run()
    app.button[0].click().run()
    assert app.session_state['analysis']['status']=='refuse'


@pytest.mark.skipif(not DB.exists(), reason='Run python -m bankwise.data for integration tests')
def test_grouped_charts_and_language_switch():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)

    # The default overall-rate question returns one row and must not chart.
    app.button[0].click().run(timeout=20)
    assert len(app.get('vega_lite_chart')) == 0

    # Both acceptance examples render above their result tables.
    for question in ('channel', 'month'):
        app.selectbox[0].select(question).run(timeout=20)
        app.button[0].click().run(timeout=20)
        assert not app.exception
        assert len(app.get('vega_lite_chart')) == 1

    # Re-running in English rebuilds the chart with translated labels.
    app.selectbox(key='language').select('en').run(timeout=20)
    app.selectbox[0].select('month').run(timeout=20)
    app.button[0].click().run(timeout=20)
    spec = json.loads(app.get('vega_lite_chart')[0].proto.spec)
    assert spec['title'] == 'Conversion rate by group with 95% Wilson intervals'
    assert spec['layer'][0]['encoding']['x']['title'] == 'Conversion rate (%)'
