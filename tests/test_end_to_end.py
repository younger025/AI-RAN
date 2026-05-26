import pytest
from uran.demo.end_to_end import run_end_to_end_demo, DemoReport


class TestEndToEndDemo:
    def test_run_basic_intent(self):
        report = run_end_to_end_demo(
            "在 SNR=10dB 的城区场景下，要求 BLER<5%，吞吐量>500kbps",
            seed=42,
        )
        assert isinstance(report, DemoReport)
        assert report.selected_plan is not None
        assert report.runtime_summary is not None
        assert report.sdr_summary is not None

    def test_run_high_reliability_intent(self):
        report = run_end_to_end_demo(
            "在高铁场景下需要极高可靠性，BLER<0.1%，弱覆盖",
            seed=42,
        )
        assert report.selected_twin_report is not None
        assert len(report.candidate_plans) >= 1

    def test_run_produces_evolution_recommendation(self):
        report = run_end_to_end_demo(
            "在城市宏基站场景下需要高吞吐低时延，高清视频",
            seed=42,
        )
        assert report.evolution_recommendation is not None
        assert "reasons" in report.evolution_recommendation

    def test_run_produces_orchestration_trace(self):
        report = run_end_to_end_demo(
            "室内场景，要求BLER<3%，时延<20ms，机器人",
            seed=42,
        )
        assert len(report.orchestration_trace) > 0
        agent_names = [step["agent"] for step in report.orchestration_trace]
        assert "IntentAgent" in agent_names

    def test_all_demo_report_fields_populated(self):
        report = run_end_to_end_demo(
            "在SNR=8dB的高铁场景下要求BLER<5%吞吐量>500kbps时延<50ms",
            seed=42,
        )
        assert report.raw_intent is not None
        assert report.intent is not None
        assert report.environment is not None
        assert len(report.candidate_plans) >= 1
        assert len(report.twin_reports) >= 1
        assert report.selected_plan is not None
        assert report.selected_twin_report is not None
        assert report.runtime_summary is not None
        assert report.sdr_summary is not None
        assert report.evolution_recommendation is not None
        assert report.orchestration_trace is not None

    def test_runtime_kpis_are_reasonable(self):
        report = run_end_to_end_demo(
            "在SNR=12dB的城区宏基站场景下要求BLER<3%吞吐量>800kbps，热点",
            seed=42,
        )
        summary = report.runtime_summary
        assert 0 <= summary.get("avg_bler", 0) <= 1
        assert summary.get("avg_throughput_kbps", 0) >= 0
        assert summary.get("avg_latency_ms", 0) >= 0

    def test_sdr_metrics_are_reasonable(self):
        report = run_end_to_end_demo(
            "在SNR=15dB的室内场景下要求BLER<1%",
            seed=42,
        )
        sdr = report.sdr_summary
        assert 0 <= sdr.get("ber", 0) <= 1
        assert sdr.get("packet_loss", 0) >= 0
        assert sdr.get("latency_ms", 0) >= 0

    def test_end_to_end_deterministic_with_same_seed(self):
        report_a = run_end_to_end_demo("在SNR=10dB场景下要求BLER<5%，干扰", seed=42)
        report_b = run_end_to_end_demo("在SNR=10dB场景下要求BLER<5%，干扰", seed=42)

        for key in ["modulation", "coding_scheme", "coding_rate", "mcs",
                     "harq_enabled", "harq_max_retx", "pilot_density",
                     "tx_power_dbm", "scheduler", "power_control"]:
            assert report_a.selected_plan.get(key) == report_b.selected_plan.get(key), \
                f"Mismatch on {key}: {report_a.selected_plan.get(key)} != {report_b.selected_plan.get(key)}"

        assert report_a.runtime_summary.get("avg_bler") == pytest.approx(
            report_b.runtime_summary.get("avg_bler"), rel=0.01
        )