import pandas as pd
from uran.dashboard.report_exporter import generate_experiment_summary


def test_generate_summary():
    df = pd.DataFrame(
        [
            {
                "bler": 0.01,
                "throughput_kbps": 1000,
                "latency_ms": 10,
                "snr_db": 15,
                "reliability": 0.99,
            },
            {
                "bler": 0.05,
                "throughput_kbps": 800,
                "latency_ms": 12,
                "snr_db": 10,
                "reliability": 0.95,
            },
        ]
    )
    summary = generate_experiment_summary(df, "test")
    assert "Experiment Summary" in summary
    assert "Average BLER" in summary


def test_generate_summary_empty():
    df = pd.DataFrame()
    summary = generate_experiment_summary(df, "empty")
    assert "No data recorded" in summary


def test_generate_summary_has_headers():
    df = pd.DataFrame(
        [
            {
                "bler": 0.02,
                "throughput_kbps": 500,
                "latency_ms": 15,
                "snr_db": 8,
                "reliability": 0.92,
            },
        ]
    )
    summary = generate_experiment_summary(df, "test2")
    assert "KPI Summary" in summary
    assert "Interpretation" in summary