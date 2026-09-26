from pathlib import Path
from types import SimpleNamespace
from streamlit.testing.v1 import AppTest
from bankwise.agent import OpenAIPlanner, analyze
from bankwise.i18n import question_text

def test_english_demo_and_refusal():
    result = analyze(question_text('channel', 'en'), demo_id='channel', language='en')
    assert result['status']=='ok'
    assert 'Highest group' in result['summary']
    assert result['table']['rows'][0]==['cellular',26144,3853,14.7376]
    result = analyze(question_text('revenue', 'en'), demo_id='revenue', language='en')
    assert result['status']=='refuse' and 'cannot be calculated' in result['explanation']

def test_english_model_instructions(monkeypatch):
    captured = {}
    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(usage=None, output_text='{"status":"refuse","explanation":"No revenue data."}')
    monkeypatch.setattr('openai.OpenAI', lambda **kwargs: SimpleNamespace(responses=SimpleNamespace(create=create)))
    planner = OpenAIPlanner(key='test-only', model='test-only', language='en')
    assert planner('Revenue?', [])['status']=='refuse'
    assert 'Write every explanation in English.' in captured['instructions']
    assert 'in Chinese' not in captured['instructions']

def test_english_page_and_language_switch():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run()
    app.selectbox(key='language').select('en').run()
    assert not app.exception
    assert app.metric[0].label=='Marketing observations'
    app.button[0].click().run()
    assert app.session_state['analysis']['language']=='en'
    assert 'Overall:' in app.session_state['analysis']['summary']
    assert any('STUDY_GUIDE_EN.md' in x.value for x in app.caption)
    assert [tab.label for tab in app.tabs] == ['Business analysis', 'Data and definitions']
    app.selectbox(key='language').select('zh').run()
    assert not app.exception
    assert app.metric[0].label=='营销观察记录'
