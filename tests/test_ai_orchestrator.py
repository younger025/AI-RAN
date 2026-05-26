import pytest
from uran.ai.intent_schema import IntentSpec, EnvironmentSpec
from uran.ai.plan_schema import PlanSpec
from uran.ai.orchestrator import AIOrchestrator
from uran.common.ids import new_id


def make_intent(**overrides):
    defaults = {
        "intent_id": new_id("intent_test"),
        "raw_text": "test intent",
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


class TestIntentSchema:
    def test_intent_spec_custom(self):
        intent = make_intent(
            target_bler=0.01,
            min_throughput_kbps=1000,
            max_latency_ms=10,
            scenario_type="urban",
        )
        assert intent.target_bler == 0.01
        assert intent.scenario_type == "urban"


class TestEnvironmentProfile:
    def test_custom(self):
        env = make_env(
            avg_snr_db=15.0,
            mobility_level="high",
        )
        assert env.avg_snr_db == 15.0
        assert env.mobility_level == "high"


class TestPlanSpec:
    def test_plan_creation(self):
        plan = make_plan(
            modulation="QPSK",
            coding_rate=2 / 3,
            harq_enabled=True,
            harq_max_retx=2,
        )
        assert plan.modulation == "QPSK"
        assert plan.coding_rate == pytest.approx(2 / 3)
        assert plan.harq_enabled is True


class TestAIOrchestrator:
    def test_generate_plan_basic(self):
        orchestrator = AIOrchestrator(seed=42)
        raw_intent = "在 SNR=10dB 的城区场景下，要求 BLER<5%，吞吐量>500kbps"
        result = orchestrator.generate_plan(raw_intent)
        assert "intent" in result
        assert "environment" in result
        assert "candidate_plans" in result
        assert "trace" in result
        assert len(result["candidate_plans"]) >= 1

    def test_generate_plan_with_environment(self):
        orchestrator = AIOrchestrator(seed=42)
        raw_intent = "在高铁场景下需要高可靠性通信，BLER<1%"
        env = make_env(avg_snr_db=5.0, mobility_level="high")
        result = orchestrator.generate_plan(raw_intent, environment=env)
        assert result["environment"].avg_snr_db == 5.0

    def test_multiple_plans_generated(self):
        orchestrator = AIOrchestrator(seed=42)
        result = orchestrator.generate_plan("在干扰场景下需要鲁棒通信")
        assert len(result["candidate_plans"]) >= 2

    def test_trace_contains_all_agents(self):
        orchestrator = AIOrchestrator(seed=42)
        result = orchestrator.generate_plan("全面测试意图")
        agent_names = [step["agent"] for step in result["trace"]]
        assert "IntentAgent" in agent_names
        assert "EnvironmentAgent" in agent_names
        assert "ModuleSelectionAgent" in agent_names
        assert "ParameterGenAgent" in agent_names

    def test_high_reliability_intent_yields_robust_plan(self):
        orchestrator = AIOrchestrator(seed=42)
        result = orchestrator.generate_plan("BLER必须小于0.1%，绝对可靠，弱覆盖")
        plan = result["candidate_plans"][0]
        assert plan.harq_enabled is True
        assert plan.harq_max_retx >= 2
        assert plan.pilot_density in ("medium", "high")

    def test_high_throughput_intent_yields_efficient_plan(self):
        orchestrator = AIOrchestrator(seed=42)
        result = orchestrator.generate_plan("需要最大化吞吐量，高清视频，高速下载")
        plan = result["candidate_plans"][0]
        assert plan.modulation in ("16QAM", "64QAM") or plan.coding_rate >= 0.5