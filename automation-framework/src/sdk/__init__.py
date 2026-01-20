"""
Python SDK for Automation Framework
"""
from .client import AutomationClient
from .task_api import TaskAPI
from .session_api import SessionAPI
from .history_api import HistoryAPI
from .config_api import ConfigAPI

__all__ = [
    "AutomationClient",
    "TaskAPI",
    "SessionAPI",
    "HistoryAPI",
    "ConfigAPI"
]

__version__ = "0.1.0"
