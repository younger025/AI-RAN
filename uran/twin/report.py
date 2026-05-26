from dataclasses import dataclass, field
from typing import List


@dataclass
class TwinValidationReport:
    report_id: str
    plan_id: str
    passed: bool
    decision: str

    interface_check_passed: bool
    constraint_check_passed: bool
    link_sim_passed: bool
    fault_test_passed: bool
    fallback_test_passed: bool

    bler: float
    throughput_kbps: float
    latency_ms: float
    spectral_efficiency: float
    energy_cost: float
    robustness_score: float
    final_score: float

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)