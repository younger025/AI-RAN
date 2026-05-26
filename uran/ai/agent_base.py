from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AgentBase(ABC):
    def __init__(self, name: str):
        self.name = name
        self._trace: List[Dict[str, str]] = []

    def log(self, message: str):
        self._trace.append({
            "agent": self.name,
            "message": message,
        })

    def get_trace(self) -> List[Dict[str, str]]:
        return list(self._trace)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        pass