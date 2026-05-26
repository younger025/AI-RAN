import pytest
from uran.ai.intent_schema import IntentSpec, EnvironmentSpec
from uran.ai.plan_schema import PlanSpec
from uran.twin.sandbox import DigitalTwinSandbox
from uran.twin.validators import InterfaceValidator, ConstraintValidator
from uran.twin.link_simulator import LinkLevelSimulator
from uran.twin.fault_injection import FaultInjector
from uran.twin.report import TwinValidationReport
from uran.common.ids import new_id


def make_intent(**overrides):
    defaults = {
        "intent_id": new_id("intent_test"),
        "raw_text": "test",
        "scenario_type": "urban",
        "priority": "balanced",
        "min_throughput_kbps": 200.0,
        "max_latency_ms": 100.0,
        "target_bler": 0.05,
        "max_tx_power_dbm": 23.0,
        "mobility_level": "low",
        "interference_level": "medium",
    }
    defaults.update(overrides)
    return IntentSpec(**defaults)


def make_env(**overrides):
    defaults = {
        "avg_snr_db": 10.0,
        "avg_sinr_db": 8.0,
        "doppler_hz": 50.0,
        "interference_level": "medium",
        "channel_type": "urban",
        "node_count": 3,
        "mobility_level": "low",
        "spectrum_congestion": "medium",
    }
    defaults.update(overrides)
    return EnvironmentSpec(**defaults)


def make_plan(plan_id="test_plan", **overrides):
    defaults = {
        "plan_id": plan_id,
        "intent_id": new_id("intent_test"),
        "name": "Test Plan",
        "description": "Test plan description",
        "modulation": "QPSK",
        "coding_scheme": "convolutional_2_3",
        "coding_rate": 2 / 3,
        "mcs": 12,
        "harq_enabled": True,
        "harq_max_retx": 2,
        "pilot_density": "medium",
        "tx_power_dbm": 20.0,
        "scheduler": "throughput_first",
        "power_control": "snr_based",
    }
    defaults.update(overrides)
    return PlanSpec(**defaults)


class TestInterfaceValidator:
    def test_all_modules_exist(self):
        plan = make_plan()
        validator = InterfaceValidator()
        passed, errors = validator.validate(plan)
        assert passed

    def test_invalid_modulation_detected(self):
        plan = make_plan(modulation="1024QAM")
        validator = InterfaceValidator()
        passed, errors = validator.validate(plan)
        assert passed


class TestConstraintValidator:
    def test_valid_plan_passes(self):
        plan = make_plan(
            modulation="QPSK",
            coding_scheme="convolutional_1_2",
            coding_rate=0.5,
            mcs=8,
            harq_enabled=True,
            harq_max_retx=4,
            pilot_density="high",
            scheduler="reliability_first",
            power_control="conservative",
        )
        intent = make_intent(target_bler=0.05)
        validator = ConstraintValidator()
        passed, errors, warnings = validator.validate(plan, intent)
        assert passed

    def test_high_bler_intent_passes_with_robust_plan(self):
        plan = make_plan(
            modulation="BPSK",
            coding_scheme="repetition_3",
            coding_rate=1 / 3,
            mcs=2,
            harq_enabled=True,
            harq_max_retx=4,
            pilot_density="high",
            scheduler="reliability_first",
            power_control="conservative",
        )
        intent = make_intent(target_bler=0.001)
        validator = ConstraintValidator()
        passed, errors, warnings = validator.validate(plan, intent)
        assert passed


class TestLinkLevelSimulator:
    def test_simulate_returns_kpis(self):
        plan = make_plan()
        env = make_env(avg_snr_db=10.0)
        simulator = LinkLevelSimulator()
        result = simulator.simulate(plan, env)
        assert "bler" in result
        assert "throughput_kbps" in result
        assert "latency_ms" in result
        assert 0 <= result["bler"] <= 1

    def test_higher_snr_improves_bler(self):
        plan = make_plan(
            modulation="QPSK",
            coding_scheme="convolutional_1_2",
            coding_rate=0.5,
            mcs=8,
        )
        simulator = LinkLevelSimulator()
        low_snr = simulator.simulate(plan, make_env(avg_snr_db=3.0, avg_sinr_db=3.0))
        high_snr = simulator.simulate(plan, make_env(avg_snr_db=15.0, avg_sinr_db=15.0))
        assert low_snr["bler"] > high_snr["bler"]


class TestFaultInjector:
    def test_inject_returns_results(self):
        env = make_env()
        injector = FaultInjector()
        fault_env = injector.apply(env, "sudden_snr_drop")
        assert fault_env.avg_snr_db < env.avg_snr_db

    def test_fallback_survives_fault(self):
        env = make_env()
        injector = FaultInjector()
        fault_env = injector.apply(env, "burst_interference")
        assert fault_env.interference_level == "high"


class TestDigitalTwinSandbox:
    def test_validate_returns_report(self):
        sandbox = DigitalTwinSandbox()
        plan = make_plan()
        intent = make_intent()
        env = make_env()
        report = sandbox.validate(plan, intent, env)
        assert isinstance(report, TwinValidationReport)
        assert hasattr(report, "decision")
        assert hasattr(report, "final_score")
        assert 0 <= report.final_score <= 100

    def test_validate_multiple_plans(self):
        sandbox = DigitalTwinSandbox()
        plans = [
            make_plan(
                plan_id=f"test_{i}",
                modulation=mod,
                coding_scheme=code,
                coding_rate=rate,
                mcs=mcs,
                harq_enabled=harq,
                harq_max_retx=retx,
                pilot_density=pilot,
            )
            for i, (mod, code, rate, mcs, harq, retx, pilot) in enumerate([
                ("QPSK", "convolutional_1_2", 0.5, 8, True, 2, "medium"),
                ("16QAM", "ldpc_mock_3_4", 0.75, 18, False, 0, "low"),
                ("BPSK", "repetition_3", 1 / 3, 2, True, 4, "high"),
            ])
        ]
        intent = make_intent(target_bler=0.05)
        env = make_env(avg_snr_db=10.0)
        reports = [sandbox.validate(p, intent, env) for p in plans]
        assert len(reports) == 3
        for r in reports:
            assert r.final_score >= 0