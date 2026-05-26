from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RuntimeState:
    runtime_id: str
    active_plan_id: Optional[str] = None
    active_modules: List[str] = field(default_factory=list)
    status: str = "INIT"
    step_count: int = 0
    last_kpi: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    fallback_reason: Optional[str] = None