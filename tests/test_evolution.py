import pytest
import tempfile
from pathlib import Path
from uran.evolution.experience import Experience
from uran.evolution.data_lake import DataLake
from uran.evolution.strategy_memory import StrategyMemory
from uran.evolution.optimizer import HeuristicOptimizer
from uran.evolution.evolution_loop import EvolutionLoop
from uran.ai.intent_schema import IntentSpec
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


class TestExperience:
    def test_experience_creation(self):
        exp = Experience(
            exp_id="exp_001",
            timestamp="2026-01-01T00:00:00",
            intent={"scenario_type": "urban", "target_bler": 0.05},
            environment={"avg_snr_db": 10.0},
            plan={"modulation": "QPSK"},
            twin_score=85.0,
            runtime_kpis={"avg_bler": 0.03, "avg_throughput_kbps": 600},
            success=True,
        )
        assert exp.exp_id == "exp_001"
        assert exp.success is True
        assert exp.twin_score == 85.0


class TestDataLake:
    def test_append_and_load(self):
        tmp_path = Path(tempfile.gettempdir()) / "test_evolution_experience_log.jsonl"
        dl = DataLake(path=str(tmp_path))
        exp = Experience(
            exp_id="exp_test",
            timestamp="2026-01-01",
            intent={"scenario_type": "urban", "target_bler": 0.05},
            environment={"avg_snr_db": 10.0},
            plan={"modulation": "QPSK"},
            twin_score=80.0,
            runtime_kpis={"avg_bler": 0.04, "avg_throughput_kbps": 500},
            success=True,
        )
        dl.append(exp)
        all_data = dl.load_all()
        assert len(all_data) >= 1
        assert any(e.get("exp_id") == "exp_test" for e in all_data)

    def test_query_by_scenario(self):
        tmp_path = Path(tempfile.gettempdir()) / "test_evolution_scenario_log.jsonl"
        dl = DataLake(path=str(tmp_path))
        for scenario in ["urban", "high_speed", "urban"]:
            exp = Experience(
                exp_id=f"exp_{scenario}",
                timestamp="2026-01-01",
                intent={"scenario_type": scenario},
                environment={"avg_snr_db": 10.0},
                plan={"modulation": "QPSK"},
                twin_score=75.0,
                runtime_kpis={"avg_bler": 0.05, "avg_throughput_kbps": 400},
                success=True,
            )
            dl.append(exp)
        urban = dl.query_by_scenario("urban")
        assert len(urban) >= 2


class TestStrategyMemory:
    def test_update_and_get_best(self):
        memory = StrategyMemory(top_k=2)
        memory.update({
            "intent": {"scenario_type": "urban"},
            "plan": {"modulation": "QPSK"},
            "twin_score": 90.0,
            "success": True,
            "runtime_kpis": {"avg_bler": 0.01, "avg_throughput_kbps": 800, "avg_latency_ms": 10},
        })
        memory.update({
            "intent": {"scenario_type": "urban"},
            "plan": {"modulation": "16QAM"},
            "twin_score": 70.0,
            "success": True,
            "runtime_kpis": {"avg_bler": 0.1, "avg_throughput_kbps": 400, "avg_latency_ms": 30},
        })
        best = memory.get_best("urban")
        assert len(best) <= 2
        assert best[0]["plan"]["modulation"] == "QPSK"

    def test_empty_scenario_returns_empty(self):
        memory = StrategyMemory()
        assert memory.get_best("nonexistent") == []


class TestHeuristicOptimizer:
    def test_high_bler_triggers_reliability_recommendation(self):
        optimizer = HeuristicOptimizer()
        intent = make_intent(target_bler=0.01, min_throughput_kbps=100, max_latency_ms=200)
        plan = None
        kpis = {"avg_bler": 0.5, "avg_throughput_kbps": 100, "avg_latency_ms": 50}
        rec = optimizer.recommend(intent, plan, kpis)
        assert "increase_reliability" in rec["changes"]

    def test_low_throughput_triggers_throughput_recommendation(self):
        optimizer = HeuristicOptimizer()
        intent = make_intent(target_bler=0.1, min_throughput_kbps=500, max_latency_ms=200)
        plan = None
        kpis = {"avg_bler": 0.001, "avg_throughput_kbps": 50, "avg_latency_ms": 50}
        rec = optimizer.recommend(intent, plan, kpis)
        assert "increase_throughput" in rec["changes"]

    def test_high_latency_triggers_latency_recommendation(self):
        optimizer = HeuristicOptimizer()
        intent = make_intent(target_bler=0.1, min_throughput_kbps=100, max_latency_ms=10)
        plan = None
        kpis = {"avg_bler": 0.01, "avg_throughput_kbps": 500, "avg_latency_ms": 200}
        rec = optimizer.recommend(intent, plan, kpis)
        assert "reduce_latency" in rec["changes"]

    def test_all_good_triggers_fine_tuning(self):
        optimizer = HeuristicOptimizer()
        intent = make_intent(target_bler=0.1, min_throughput_kbps=100, max_latency_ms=200)
        plan = None
        kpis = {"avg_bler": 0.01, "avg_throughput_kbps": 600, "avg_latency_ms": 10}
        rec = optimizer.recommend(intent, plan, kpis)
        assert "fine_tuning" in rec["changes"]


class TestEvolutionLoop:
    def test_run_once_returns_valid_result(self):
        loop = EvolutionLoop(seed=42)
        result = loop.run_once("在SNR=10dB的城区场景下要求BLER<5%，干扰")
        assert "intent" in result
        assert "selected_plan" in result
        assert "runtime_summary" in result
        assert "recommendation" in result

    def test_run_once_produces_twin_report(self):
        loop = EvolutionLoop(seed=42)
        result = loop.run_once("在高铁场景下需要高可靠性，弱覆盖")
        assert result["best_twin_report"].final_score >= 0

    def test_run_iterations(self):
        loop = EvolutionLoop(seed=42)
        results = loop.run_iterations("在SNR=10dB的城区场景下要求BLER<5%，高清视频", n=2)
        assert len(results) == 2
        for r in results:
            assert "iteration" in r
            assert "runtime_summary" in r