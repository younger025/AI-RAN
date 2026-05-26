from pathlib import Path
from uran.sim.scenario_loader import load_scenario_config, build_runner_from_config


def test_load_p2p_scenario():
    cfg = load_scenario_config(
        Path("configs/research_scenarios/p2p_link_adaptation.yaml")
    )
    assert cfg["scenario_id"] == "p2p_link_adaptation"
    assert len(cfg["nodes"]) >= 2
    assert len(cfg["links"]) >= 1


def test_runner_generates_records():
    cfg = load_scenario_config(
        Path("configs/research_scenarios/p2p_link_adaptation.yaml")
    )
    runner = build_runner_from_config(cfg)
    records = runner.step()
    assert len(records) >= 1
    record = records[0]
    assert record.snr_db is not None
    assert record.bler >= 0
    assert record.throughput_kbps >= 0
    assert record.mcs >= 0


def test_runner_dataframe_columns():
    cfg = load_scenario_config(
        Path("configs/research_scenarios/p2p_link_adaptation.yaml")
    )
    runner = build_runner_from_config(cfg)
    runner.run_all()
    df = runner.recorder.to_dataframe()
    required_cols = [
        "snr_db",
        "sinr_db",
        "bler",
        "throughput_kbps",
        "latency_ms",
        "mcs",
        "modulation",
        "coding_rate",
        "harq_retx",
    ]
    for col in required_cols:
        assert col in df.columns
    assert len(df) > 0


def test_runner_reset():
    cfg = load_scenario_config(
        Path("configs/research_scenarios/p2p_link_adaptation.yaml")
    )
    runner = build_runner_from_config(cfg)
    runner.step()
    assert runner.current_step == 1
    runner.reset()
    assert runner.current_step == 0


def test_load_all_scenarios():
    scenarios = [
        "p2p_link_adaptation.yaml",
        "multi_node_cell.yaml",
        "jamming_self_evolution.yaml",
        "blockage_recovery.yaml",
    ]
    for scenario in scenarios:
        cfg = load_scenario_config(
            Path("configs/research_scenarios") / scenario
        )
        runner = build_runner_from_config(cfg)
        records = runner.step()
        assert len(records) >= 1