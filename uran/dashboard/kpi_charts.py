import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def _empty_figure(title: str):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=350,
    )
    return fig


def plot_snr_sinr_curve(df):
    if df is None or df.empty:
        return _empty_figure("SNR / SINR over Time")

    fig = go.Figure()

    for link_id in df["link_id"].unique():
        sub = df[df["link_id"] == link_id]

        fig.add_trace(
            go.Scatter(
                x=sub["time_s"],
                y=sub["snr_db"],
                mode="lines",
                name=f"{link_id} SNR",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=sub["time_s"],
                y=sub["sinr_db"],
                mode="lines",
                line=dict(dash="dash"),
                name=f"{link_id} SINR",
            )
        )

    fig.update_layout(
        title="SNR / SINR over Time",
        xaxis_title="Time (s)",
        yaxis_title="dB",
        template="plotly_white",
        height=350,
    )

    return fig


def plot_bler_curve(df, target_bler=0.1):
    if df is None or df.empty:
        return _empty_figure("BLER over Time")

    fig = go.Figure()

    for link_id in df["link_id"].unique():
        sub = df[df["link_id"] == link_id]

        fig.add_trace(
            go.Scatter(
                x=sub["time_s"],
                y=sub["bler"],
                mode="lines",
                name=link_id,
            )
        )

    fig.add_hline(
        y=target_bler,
        line_dash="dash",
        line_color="red",
        annotation_text="Target BLER",
    )

    fig.update_layout(
        title="BLER over Time",
        xaxis_title="Time (s)",
        yaxis_title="BLER",
        template="plotly_white",
        height=350,
    )

    return fig


def plot_throughput_curve(df):
    if df is None or df.empty:
        return _empty_figure("Throughput over Time")

    fig = px.line(
        df,
        x="time_s",
        y="throughput_kbps",
        color="link_id",
        title="Throughput over Time",
        labels={
            "time_s": "Time (s)",
            "throughput_kbps": "Throughput (kbps)",
        },
    )

    fig.update_layout(template="plotly_white", height=350)

    return fig


def plot_latency_curve(df):
    if df is None or df.empty:
        return _empty_figure("Latency over Time")

    fig = px.line(
        df,
        x="time_s",
        y="latency_ms",
        color="link_id",
        title="Latency over Time",
        labels={
            "time_s": "Time (s)",
            "latency_ms": "Latency (ms)",
        },
    )

    fig.update_layout(template="plotly_white", height=350)

    return fig


def plot_adaptation_params(df):
    if df is None or df.empty:
        return _empty_figure("Adaptive Communication Parameters")

    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=[
            "MCS Index",
            "Coding Rate",
            "Pilot Density",
            "TX Power",
            "HARQ Retransmissions",
            "Spectral Efficiency",
        ],
    )

    for link_id in df["link_id"].unique():
        sub = df[df["link_id"] == link_id]

        fig.add_trace(
            go.Scatter(x=sub["time_s"], y=sub["mcs"], mode="lines", name=f"{link_id} MCS"),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(x=sub["time_s"], y=sub["coding_rate"], mode="lines", name=f"{link_id} Coding Rate"),
            row=1,
            col=2,
        )

        fig.add_trace(
            go.Scatter(x=sub["time_s"], y=sub["pilot_density"], mode="lines", name=f"{link_id} Pilot"),
            row=2,
            col=1,
        )

        fig.add_trace(
            go.Scatter(x=sub["time_s"], y=sub["tx_power_dbm"], mode="lines", name=f"{link_id} TX Power"),
            row=2,
            col=2,
        )

        fig.add_trace(
            go.Scatter(x=sub["time_s"], y=sub["harq_retx"], mode="lines", name=f"{link_id} HARQ"),
            row=3,
            col=1,
        )

        fig.add_trace(
            go.Scatter(x=sub["time_s"], y=sub["spectral_efficiency"], mode="lines", name=f"{link_id} SE"),
            row=3,
            col=2,
        )

    fig.update_layout(
        title="Adaptive Communication Parameters over Time",
        template="plotly_white",
        height=760,
    )

    return fig


def plot_reliability_curve(df):
    if df is None or df.empty:
        return _empty_figure("Reliability over Time")

    fig = px.line(
        df,
        x="time_s",
        y="reliability",
        color="link_id",
        title="Reliability over Time",
        labels={
            "time_s": "Time (s)",
            "reliability": "Reliability",
        },
    )

    fig.update_layout(template="plotly_white", height=350)

    return fig