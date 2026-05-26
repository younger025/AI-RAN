from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class IntentSpec:
    intent_id: str
    raw_text: str
    scenario_type: str
    priority: str
    min_throughput_kbps: float
    max_latency_ms: float
    target_bler: float
    max_tx_power_dbm: float
    mobility_level: str
    interference_level: str
    snr_hint_db: Optional[float] = None
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentSpec:
    avg_snr_db: float
    avg_sinr_db: float
    doppler_hz: float
    interference_level: str
    channel_type: str
    node_count: int
    mobility_level: str
    spectrum_congestion: str