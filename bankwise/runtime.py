"""Refresh modules left in a running Streamlit process after a source update."""
import hashlib
import importlib
import inspect
from pathlib import Path


def load_agent():
    agent = importlib.import_module('bankwise.agent')
    digest = hashlib.sha256(Path(agent.__file__).read_bytes()).hexdigest()
    if (getattr(agent, '_loaded_source_digest', None) != digest
            or 'dataset_notes' not in inspect.signature(agent.OpenAIPlanner).parameters):
        # A rerun can execute the new app.py while Python retains the old class.
        agent = importlib.reload(agent)
    agent._loaded_source_digest = digest
    return agent
