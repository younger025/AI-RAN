from pathlib import Path
import datetime


def ensure_output_dirs():
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    Path("outputs/experiment_logs").mkdir(parents=True, exist_ok=True)


def timestamp_str() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def export_kpi_csv(df, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def export_kpi_json(df, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(path, orient="records", indent=2, force_ascii=False)
    return path


def export_plotly_html(fig, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(path))
    return path


def export_plotly_png(fig, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(str(path))
    return path


def generate_experiment_summary(df, scenario_name: str = "Unknown Scenario") -> str:
    if df is None or df.empty:
        return "# Experiment Summary\n\nNo data recorded.\n"

    avg_bler = df["bler"].mean()
    max_bler = df["bler"].max()
    avg_thr = df["throughput_kbps"].mean()
    max_thr = df["throughput_kbps"].max()
    avg_latency = df["latency_ms"].mean()
    min_snr = df["snr_db"].min()
    max_snr = df["snr_db"].max()
    avg_reliability = df["reliability"].mean()

    summary = f"""# Experiment Summary

## Scenario

- Scenario: {scenario_name}

## KPI Summary

- Average BLER: {avg_bler:.4f}
- Maximum BLER: {max_bler:.4f}
- Average Throughput: {avg_thr:.2f} kbps
- Maximum Throughput: {max_thr:.2f} kbps
- Average Latency: {avg_latency:.2f} ms
- Average Reliability: {avg_reliability:.4f}
- SNR Range: {min_snr:.2f} dB ~ {max_snr:.2f} dB

## Interpretation

This experiment demonstrates an AI-native adaptive wireless communication process.
When the channel quality is high, the system selects high-order modulation and high coding rate to improve throughput.
When the channel degrades or interference appears, the system lowers MCS, switches to more robust modulation/coding, increases pilot density, and enables HARQ retransmission.
The result shows a dynamic trade-off between throughput, latency, and reliability.

"""

    return summary


def export_markdown_summary(markdown_text: str, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_text, encoding="utf-8")
    return path