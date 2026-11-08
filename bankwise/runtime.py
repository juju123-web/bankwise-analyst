"""Refresh modules left in a running Streamlit process after a source update."""
import importlib
import inspect


def load_agent():
    agent = importlib.import_module('bankwise.agent')
    if 'dataset_notes' not in inspect.signature(agent.OpenAIPlanner).parameters:
        # A rerun can execute the new app.py while Python retains the old class.
        agent = importlib.reload(agent)
    return agent
