from uran.ai.orchestrator import AIOrchestrator
from uran.ai.intent_schema import IntentSpec
from uran.twin.sandbox import DigitalTwinSandbox
from uran.modules.registry import build_default_registry
from uran.runtime.microkernel import MicrokernelRuntime
from uran.evolution.experience import Experience
from uran.evolution.data_lake import DataLake
from uran.evolution.strategy_memory import StrategyMemory
from uran.evolution.optimizer import HeuristicOptimizer
from uran.common.ids import new_id
from uran.common.serialization import to_dict
from uran.common.time_utils import now_iso
from uran.common.band_config import BandConfig
from typing import Optional


class EvolutionLoop:
    def __init__(self, seed: int = 42, band_config: Optional[BandConfig] = None):
        self.seed = seed
        self.orchestrator = AIOrchestrator(seed=seed)
        self.sandbox = DigitalTwinSandbox(band_config=band_config)
        self.registry = build_default_registry()
        self.optimizer = HeuristicOptimizer()
        self.data_lake = DataLake()
        self.strategy_memory = StrategyMemory()

    def run_once(self, raw_intent: str, environment=None):
        result = self.orchestrator.generate_plan(raw_intent, environment)
        intent = result["intent"]
        env = result["environment"]
        plans = result["candidate_plans"]

        reports = [self.sandbox.validate(p, intent, env) for p in plans]

        accepted = [
            (i, p, r) for i, (p, r) in enumerate(zip(plans, reports))
            if r.decision == "ACCEPT"
        ]
        if accepted:
            best_idx, best_plan, best_report = max(accepted, key=lambda x: x[2].final_score)
        else:
            _, (best_plan, best_report) = max(
                enumerate(zip(plans, reports)),
                key=lambda x: x[1][1].final_score,
            )

        runtime = MicrokernelRuntime(registry=self.registry, seed=self.seed)
        runtime.load_plan(best_plan)
        runtime.run(steps=50)
        summary = runtime.monitor.summary()
        summary["status"] = runtime.get_state().status
        summary["active_modules"] = runtime.get_state().active_modules
        summary["events"] = runtime.get_state().events
        summary["fallback_triggered"] = runtime.get_state().status == "FALLBACK"

        recommendation = self.optimizer.recommend(intent, best_plan, summary)

        exp = Experience(
            exp_id=new_id("exp"),
            timestamp=now_iso(),
            intent=to_dict(intent),
            environment=to_dict(env),
            plan=to_dict(best_plan),
            twin_score=best_report.final_score,
            runtime_kpis=summary,
            success=best_report.decision == "ACCEPT",
            failure_reason=None if best_report.decision == "ACCEPT" else f"Twin score: {best_report.final_score:.1f}",
            recommendation=recommendation,
        )
        self.data_lake.append(exp)
        self.strategy_memory.update(to_dict(exp))

        return {
            "intent": intent,
            "environment": env,
            "candidate_plans": plans,
            "twin_reports": reports,
            "selected_plan": best_plan,
            "best_twin_report": best_report,
            "runtime_summary": summary,
            "recommendation": recommendation,
        }

    def run_iterations(self, raw_intent: str, n: int = 3, environment=None):
        results = []
        current_intent = raw_intent

        for i in range(n):
            result = self.run_once(current_intent, environment=environment)
            result["iteration"] = i + 1
            results.append(result)

            rec = result.get("recommendation", {})
            reasons = " ".join(rec.get("reasons", []))

            if "BLER" in reasons or "bler" in reasons:
                current_intent = raw_intent + "，下一轮请进一步增强可靠性，降低调制阶数，提高冗余。"
            elif "throughput" in reasons or "吞吐" in reasons:
                current_intent = raw_intent + "，下一轮请进一步提高吞吐。"
            elif "latency" in reasons or "时延" in reasons:
                current_intent = raw_intent + "，下一轮请进一步降低时延。"
            else:
                current_intent = raw_intent + "，下一轮请保持策略并优化。"

        return results