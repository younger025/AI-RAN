from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class PlanSpec:
    plan_id: str
    intent_id: str
    name: str
    description: str

    modulation: str
    coding_scheme: str
    coding_rate: float
    mcs: int

    harq_enabled: bool
    harq_max_retx: int

    pilot_density: str
    tx_power_dbm: float

    scheduler: str
    power_control: str

    expected_bler: Optional[float] = None
    expected_throughput_kbps: Optional[float] = None
    expected_latency_ms: Optional[float] = None
    expected_spectral_efficiency: Optional[float] = None

    risk_level: str = "unknown"
    generated_by: str = "rule_based_agents"
    metadata: Dict[str, Any] = field(default_factory=dict)