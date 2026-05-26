from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Experience:
    exp_id: str
    timestamp: str
    intent: Dict[str, Any]
    environment: Dict[str, Any]
    plan: Dict[str, Any]
    twin_score: float
    runtime_kpis: Dict[str, Any]
    success: bool
    failure_reason: Optional[str] = None
    recommendation: Optional[Dict[str, Any]] = None