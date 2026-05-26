from typing import Any, Dict


class CommunicationModule:
    def __init__(self, module_id: str, name: str, module_type: str, version: str = "0.1"):
        self.module_id = module_id
        self.name = name
        self.module_type = module_type
        self.version = version
        self.params: Dict[str, Any] = {}
        self.failed = False

    def configure(self, params: Dict[str, Any]) -> None:
        self.params.update(params or {})

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return context

    def health_check(self) -> bool:
        return not self.failed

    def inject_failure(self):
        self.failed = True

    def recover(self):
        self.failed = False

    def describe(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "module_type": self.module_type,
            "version": self.version,
            "params": self.params,
            "healthy": self.health_check(),
        }