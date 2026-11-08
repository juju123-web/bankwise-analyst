import inspect
from bankwise import agent
from bankwise.runtime import load_agent


def test_refresh_stale_planner_after_deployment(monkeypatch):
    class LegacyPlanner:
        def __init__(self, key=None, model=None, language='zh'):
            pass
    monkeypatch.setattr(agent, 'OpenAIPlanner', LegacyPlanner)
    refreshed = load_agent()
    assert 'dataset_notes' in inspect.signature(refreshed.OpenAIPlanner).parameters
    # Construct a real SDK client with a dummy key; no network request is made.
    planner = refreshed.OpenAIPlanner(key='test-not-a-real-key', model='test', dataset_notes='每行一笔交易')
    assert planner.dataset_notes == '每行一笔交易'
    assert planner.client is not None
    planner.client.close()


def test_current_agent_does_not_reload(monkeypatch):
    import bankwise.runtime as runtime
    def unexpected_reload(module):
        raise AssertionError('Current modules should not reload on every rerun')
    monkeypatch.setattr(runtime.importlib, 'reload', unexpected_reload)
    assert runtime.load_agent() is agent
