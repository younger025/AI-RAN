import pytest
from uran.modules.base import CommunicationModule
from uran.modules.registry import build_default_registry
from uran.modules.modulation import ModulationModule
from uran.modules.coding import CodingModule
from uran.modules.harq import HARQModule
from uran.modules.pilot import PilotModule
from uran.modules.scheduler import SchedulerModule
from uran.modules.power_control import PowerControlModule
from uran.modules.fallback import FallbackSafeBPSKModule
from uran.runtime.microkernel import MicrokernelRuntime
from uran.runtime.monitor import RuntimeMonitor
from uran.runtime.safety_guard import SafetyGuard
from uran.runtime.module_loader import map_plan_to_module_ids
from uran.ai.plan_schema import PlanSpec
from uran.common.ids import new_id


def make_plan(plan_id="test_plan", **overrides):
    defaults = {
        "plan_id": plan_id,
        "intent_id": new_id("intent_test"),
        "name": "Test Plan",
        "description": "Test plan description",
        "modulation": "QPSK",
        "coding_scheme": "convolutional_1_2",
        "coding_rate": 0.5,
        "mcs": 8,
        "harq_enabled": True,
        "harq_max_retx": 2,
        "pilot_density": "medium",
        "tx_power_dbm": 20.0,
        "scheduler": "balanced",
        "power_control": "snr_based",
    }
    defaults.update(overrides)
    return PlanSpec(**defaults)


class TestCommunicationModule:
    def test_base_module_creation(self):
        module = CommunicationModule("test", "Test Module", "test_type")
        assert module.module_id == "test"
        assert module.health_check() is True

    def test_configure_updates_params(self):
        module = CommunicationModule("test", "Test", "test")
        module.configure({"param1": 42})
        assert module.params["param1"] == 42

    def test_process_returns_context(self):
        module = CommunicationModule("test", "Test", "test")
        result = module.process({"key": "value"})
        assert result == {"key": "value"}

    def test_failure_and_recovery(self):
        module = CommunicationModule("test", "Test", "test")
        assert module.health_check() is True
        module.inject_failure()
        assert module.health_check() is False
        module.recover()
        assert module.health_check() is True

    def test_describe(self):
        module = CommunicationModule("mod_test", "Test Mod", "modulation")
        desc = module.describe()
        assert desc["module_id"] == "mod_test"
        assert desc["module_type"] == "modulation"
        assert desc["healthy"] is True


class TestModulationModule:
    def test_bpsk(self):
        mod = ModulationModule("BPSK", 1, 1.0)
        ctx = mod.process({})
        assert ctx["modulation"] == "BPSK"
        assert ctx["bits_per_symbol"] == 1

    def test_qpsk(self):
        mod = ModulationModule("QPSK", 2, 0.8)
        ctx = mod.process({})
        assert ctx["modulation"] == "QPSK"

    def test_16qam(self):
        mod = ModulationModule("16QAM", 4, 0.5)
        ctx = mod.process({})
        assert ctx["modulation"] == "16QAM"

    def test_64qam(self):
        mod = ModulationModule("64QAM", 6, 0.3)
        ctx = mod.process({})
        assert ctx["modulation"] == "64QAM"


class TestCodingModule:
    def test_repetition_code(self):
        code = CodingModule("code_repetition_3", "Rep 1/3", 1 / 3, 5)
        ctx = code.process({})
        assert ctx["coding_rate"] == pytest.approx(1 / 3)
        assert ctx["coding_gain_db"] == 5


class TestHARQModule:
    def test_no_harq(self):
        harq = HARQModule("harq_none", "No HARQ", 0)
        ctx = harq.process({})
        assert ctx["harq_max_retx"] == 0

    def test_harq_with_retx(self):
        harq = HARQModule("harq_stop_and_wait", "SAW", 2)
        ctx = harq.process({})
        assert ctx["harq_max_retx"] == 2
        assert ctx["harq_gain_db"] > 0


class TestPilotModule:
    def test_low_density(self):
        p = PilotModule("low")
        ctx = p.process({})
        assert ctx["pilot_density"] == "low"


class TestSchedulerModule:
    def test_throughput_first(self):
        s = SchedulerModule("throughput_first")
        ctx = s.process({})
        assert ctx["scheduler"] == "throughput_first"


class TestFallbackModule:
    def test_fallback_context(self):
        fb = FallbackSafeBPSKModule()
        ctx = fb.process({})
        assert ctx["modulation"] == "BPSK"
        assert ctx["fallback_active"] is True
        assert ctx["coding_rate"] == pytest.approx(1 / 3)
        assert ctx["pilot_density"] == "high"


class TestModuleRegistry:
    def test_build_default_registry(self):
        registry = build_default_registry()
        modules = registry.list_modules()
        assert len(modules) > 10

    def test_get_module(self):
        registry = build_default_registry()
        mod = registry.get("mod_qpsk")
        assert mod.module_type == "modulation"

    def test_get_nonexistent_raises(self):
        registry = build_default_registry()
        with pytest.raises(KeyError):
            registry.get("nonexistent_module")

    def test_describe_all(self):
        registry = build_default_registry()
        descriptions = registry.describe_all()
        assert len(descriptions) > 10

    def test_fallback_module_exists(self):
        registry = build_default_registry()
        fb = registry.get("fallback_safe_bpsk")
        assert fb.module_type == "fallback"


class TestMicrokernelRuntime:
    def test_create_runtime(self):
        runtime = MicrokernelRuntime(seed=42)
        assert runtime.state.status == "INIT"
        assert runtime.state.step_count == 0

    def test_load_plan(self):
        runtime = MicrokernelRuntime(seed=42)
        plan = make_plan()
        state = runtime.load_plan(plan)
        assert state.status == "RUNNING"
        assert len(state.active_modules) > 0

    def test_step_produces_kpi(self):
        runtime = MicrokernelRuntime(seed=42)
        runtime.load_plan(make_plan())
        result = runtime.step()
        assert "kpi" in result
        assert "bler" in result["kpi"]
        assert "throughput_kbps" in result["kpi"]
        assert "latency_ms" in result["kpi"]

    def test_run_multiple_steps(self):
        runtime = MicrokernelRuntime(seed=42)
        runtime.load_plan(make_plan())
        outputs = runtime.run(steps=10)
        assert len(outputs) == 10

    def test_inject_failure_triggers_fallback(self):
        runtime = MicrokernelRuntime(seed=42)
        runtime.load_plan(make_plan(coding_scheme="convolutional_1_2"))
        runtime.run(steps=2)
        runtime.inject_failure("code_conv_1_2")
        result = runtime.step()
        state = runtime.get_state()
        assert state.status == "FALLBACK"
        assert result["kpi"]["fallback_active"] is True

    def test_monitor_collects_kpis(self):
        runtime = MicrokernelRuntime(seed=42)
        runtime.load_plan(make_plan())
        runtime.run(steps=5)
        summary = runtime.monitor.summary()
        assert summary["steps"] == 5

    def test_bpsk_plan_is_more_reliable(self):
        runtime_bpsk = MicrokernelRuntime(seed=42)
        runtime_bpsk.load_plan(make_plan(
            modulation="BPSK",
            coding_scheme="repetition_2",
            coding_rate=0.5,
            mcs=2,
            harq_max_retx=4,
            pilot_density="high",
            scheduler="reliability_first",
            power_control="conservative",
        ))
        runtime_bpsk.run(steps=20)

        runtime_qam = MicrokernelRuntime(seed=42)
        runtime_qam.load_plan(make_plan(
            modulation="64QAM",
            coding_scheme="ldpc_mock_3_4",
            coding_rate=0.75,
            mcs=20,
            harq_enabled=False,
            harq_max_retx=0,
            pilot_density="low",
            scheduler="throughput_first",
            power_control="snr_based",
        ))
        runtime_qam.run(steps=20)

        bpsk_bler = runtime_bpsk.monitor.summary()["avg_bler"]
        qam_bler = runtime_qam.monitor.summary()["avg_bler"]
        assert bpsk_bler < qam_bler


class TestSafetyGuard:
    def test_no_fallback_when_healthy(self):
        runtime = MicrokernelRuntime(seed=42)
        runtime.load_plan(make_plan())
        runtime.run(steps=5)
        should, reason = runtime.safety_guard.should_fallback(
            runtime.state, runtime.modules, runtime.monitor
        )
        assert should is False

    def test_fallback_when_high_bler(self):
        monitor = RuntimeMonitor()
        for _ in range(10):
            monitor.append({"bler": 0.9, "throughput_kbps": 10, "latency_ms": 200})
        guard = SafetyGuard(max_bler=0.5, bad_steps=5)
        should, reason = guard.should_fallback(None, [], monitor)
        assert should is True
        assert reason is not None


class TestRuntimeMonitor:
    def test_recent_bad_bler_count(self):
        monitor = RuntimeMonitor()
        for bler in [0.1, 0.3, 0.6, 0.8, 0.9]:
            monitor.append({"bler": bler, "throughput_kbps": 100, "latency_ms": 10})
        assert monitor.recent_bad_bler_count(0.5, 5) >= 3

    def test_summary_empty(self):
        monitor = RuntimeMonitor()
        summary = monitor.summary()
        assert summary["steps"] == 0


class TestModuleLoader:
    def test_map_plan_to_module_ids(self):
        plan = make_plan()
        ids = map_plan_to_module_ids(plan)
        assert "mod_qpsk" in ids
        assert "code_conv_1_2" in ids
        assert "pilot_medium" in ids
        assert "sched_balanced" in ids
        assert "pc_snr_based" in ids

    def test_harq_disabled_no_harq_module(self):
        plan = make_plan(harq_enabled=False, harq_max_retx=0)
        ids = map_plan_to_module_ids(plan)
        assert all("harq_" not in i for i in ids)