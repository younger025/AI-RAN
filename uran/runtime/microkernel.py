import copy
import numpy as np
from uran.ai.plan_schema import PlanSpec
from uran.modules.registry import build_default_registry
from uran.runtime.events import EventBus
from uran.runtime.monitor import RuntimeMonitor
from uran.runtime.safety_guard import SafetyGuard
from uran.runtime.state_store import RuntimeState
from uran.runtime.module_loader import map_plan_to_module_ids
from uran.common.ids import new_id


class MicrokernelRuntime:
    def __init__(self, registry=None, seed=42):
        self.registry = registry or build_default_registry()
        self.event_bus = EventBus()
        self.monitor = RuntimeMonitor()
        self.safety_guard = SafetyGuard()
        self.state = RuntimeState(runtime_id=new_id("runtime"))
        self.modules = []
        self.rng = np.random.default_rng(seed)

    def load_plan(self, plan: PlanSpec):
        module_ids = map_plan_to_module_ids(plan)
        self.modules = [copy.deepcopy(self.registry.get(mid)) for mid in module_ids]
        for m in self.modules:
            m.recover()
        self.state.active_plan_id = plan.plan_id
        self.state.active_modules = module_ids
        self.state.status = "RUNNING"
        self.event_bus.emit(
            "PLAN_LOADED",
            f"Loaded plan {plan.plan_id}",
            {"modules": module_ids},
        )
        return self.get_state()

    def step(self, input_state=None):
        context = input_state or {}
        context["step"] = self.state.step_count

        for m in self.modules:
            if not m.health_check():
                context["fallback_active"] = True
                self.fallback(f"Module failed before processing: {m.module_id}")
                break
            context = m.process(context)

        kpi = self._estimate_runtime_kpi(context)
        self.monitor.append(kpi)

        self.state.step_count += 1
        self.state.last_kpi = kpi

        should, reason = self.safety_guard.should_fallback(
            self.state, self.modules, self.monitor
        )
        if should and self.state.status != "FALLBACK":
            self.fallback(reason)

        self.state.events = self.event_bus.list_events()
        return {
            "context": context,
            "kpi": kpi,
            "state": self.get_state(),
        }

    def run(self, steps: int = 10):
        outputs = []
        for _ in range(steps):
            outputs.append(self.step())
        return outputs

    def inject_failure(self, module_id: str):
        for m in self.modules:
            if m.module_id == module_id:
                m.inject_failure()
                self.event_bus.emit(
                    "MODULE_FAILURE_INJECTED",
                    f"Manual failure injected into {module_id}",
                    {"module_id": module_id},
                )
                return True

        self.event_bus.emit(
            "MODULE_FAILURE_INJECT_FAILED",
            f"Module {module_id} not found",
            {"module_id": module_id},
        )
        return False

    def fallback(self, reason: str):
        fallback_module = copy.deepcopy(self.registry.get("fallback_safe_bpsk"))
        self.modules = [fallback_module]
        self.state.active_modules = ["fallback_safe_bpsk"]
        self.state.status = "FALLBACK"
        self.state.fallback_reason = reason

        self.event_bus.emit(
            "FALLBACK_ACTIVATED",
            f"Fallback activated: {reason}",
            {"reason": reason},
        )

    def get_state(self) -> RuntimeState:
        self.state.events = self.event_bus.list_events()
        return self.state

    def _estimate_runtime_kpi(self, context):
        mod = context.get("modulation", "QPSK")
        bits = context.get("bits_per_symbol", 2)
        rate = context.get("coding_rate", 0.5)
        gain = context.get("coding_gain_db", 0)
        harq = context.get("harq_max_retx", 0)
        pilot = context.get("pilot_density", "medium")
        fallback = context.get("fallback_active", False)

        base_snr = context.get("snr_db", 8.0)
        effective_snr = base_snr + gain + 0.8 * harq

        mod_penalty = {
            "BPSK": 0, "QPSK": 2, "16QAM": 6, "64QAM": 10,
        }.get(mod, 4)

        x = effective_snr - mod_penalty
        bler = 1.0 / (1.0 + np.exp(x / 2.0))
        bler += self.rng.normal(0, 0.01)
        bler = float(np.clip(bler, 0.001, 0.999))

        pilot_eff = {
            "low": 0.95, "medium": 0.88, "high": 0.78,
        }.get(pilot, 0.88)

        throughput = bits * rate * 1000 * (1 - bler) * pilot_eff

        latency = 10 + harq * 8 + self.rng.normal(0, 1)
        if fallback:
            latency += 5

        return {
            "bler": bler,
            "throughput_kbps": throughput,
            "latency_ms": float(latency),
            "fallback_active": fallback,
        }