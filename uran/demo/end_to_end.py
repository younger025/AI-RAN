from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uran.ai.orchestrator import AIOrchestrator
from uran.twin.sandbox import DigitalTwinSandbox
from uran.modules.registry import build_default_registry
from uran.runtime.microkernel import MicrokernelRuntime
from uran.sdr.mock_sdr import MockSDRAdapter
from uran.evolution.experience import Experience
from uran.evolution.data_lake import DataLake
from uran.evolution.optimizer import HeuristicOptimizer
from uran.common.ids import new_id
from uran.common.serialization import to_dict
from uran.common.time_utils import now_iso
from uran.common.band_config import BandConfig


@dataclass
class DemoReport:
    raw_intent: str
    intent: Dict[str, Any]
    environment: Dict[str, Any]
    candidate_plans: List[Dict[str, Any]]
    twin_reports: List[Dict[str, Any]]
    selected_plan: Dict[str, Any]
    selected_twin_report: Dict[str, Any]
    runtime_summary: Dict[str, Any]
    sdr_summary: Dict[str, Any]
    evolution_recommendation: Dict[str, Any]
    orchestration_trace: List[Dict[str, str]]


def select_best_plan(plans, reports):
    accepted = [
        (p, r) for p, r in zip(plans, reports)
        if r.decision == "ACCEPT"
    ]
    if accepted:
        return max(accepted, key=lambda x: x[1].final_score)
    return max(zip(plans, reports), key=lambda x: x[1].final_score)


def run_end_to_end_demo(raw_intent: str, seed: int = 42, band_config: Optional[BandConfig] = None) -> DemoReport:
    orchestrator = AIOrchestrator(seed=seed)
    result = orchestrator.generate_plan(raw_intent)

    intent = result["intent"]
    env = result["environment"]
    plans = result["candidate_plans"]
    trace = result["trace"]

    sandbox = DigitalTwinSandbox(band_config=band_config)
    reports = [sandbox.validate(p, intent, env) for p in plans]

    best_plan, best_report = select_best_plan(plans, reports)

    registry = build_default_registry()
    runtime = MicrokernelRuntime(registry=registry, seed=seed)
    runtime.load_plan(best_plan)
    runtime.run(steps=50)
    runtime_summary = runtime.monitor.summary()
    runtime_summary["status"] = runtime.get_state().status
    runtime_summary["active_modules"] = runtime.get_state().active_modules
    runtime_summary["events"] = runtime.get_state().events
    runtime_summary["fallback_triggered"] = runtime.get_state().status == "FALLBACK"

    sdr = MockSDRAdapter(seed=seed)
    sdr.configure({
        "modulation": best_plan.modulation,
        "snr_db": env.avg_snr_db,
    })
    sdr_metrics = sdr.measure_metrics()
    sdr_summary = dict(sdr_metrics)

    optimizer = HeuristicOptimizer()
    recommendation = optimizer.recommend(intent, best_plan, runtime_summary)

    exp = Experience(
        exp_id=new_id("exp"),
        timestamp=now_iso(),
        intent=to_dict(intent),
        environment=to_dict(env),
        plan=to_dict(best_plan),
        twin_score=best_report.final_score,
        runtime_kpis=runtime_summary,
        success=best_report.decision == "ACCEPT",
        failure_reason=None if best_report.decision == "ACCEPT" else f"Twin score: {best_report.final_score:.1f}",
        recommendation=recommendation,
    )
    DataLake().append(exp)

    return DemoReport(
        raw_intent=raw_intent,
        intent=to_dict(intent),
        environment=to_dict(env),
        candidate_plans=[to_dict(p) for p in plans],
        twin_reports=[to_dict(r) for r in reports],
        selected_plan=to_dict(best_plan),
        selected_twin_report=to_dict(best_report),
        runtime_summary=runtime_summary,
        sdr_summary=sdr_summary,
        evolution_recommendation=recommendation,
        orchestration_trace=trace,
    )