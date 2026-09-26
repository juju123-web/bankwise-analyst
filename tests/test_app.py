from pathlib import Path
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

