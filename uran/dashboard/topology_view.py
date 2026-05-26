import plotly.graph_objects as go


def _link_color_by_bler(bler: float | None) -> str:
    if bler is None:
        return "gray"
    if bler < 0.03:
        return "green"
    if bler < 0.1:
        return "orange"
    return "red"


def _node_style(node_type: str) -> tuple[str, str]:
    if node_type == "gNB":
        return "square", "royalblue"
    if node_type == "UE":
        return "circle", "seagreen"
    if node_type == "jammer":
        return "x", "red"
    if node_type == "relay":
        return "diamond", "purple"
    return "circle", "gray"


def draw_topology(topology, latest_records_by_link=None):
    fig = go.Figure()

    latest_records_by_link = latest_records_by_link or {}
    node_map = {node.node_id: node for node in topology.nodes}

    for link in topology.links:
        src = node_map.get(link.source_node_id)
        dst = node_map.get(link.target_node_id)

        if src is None or dst is None:
            continue

        record = latest_records_by_link.get(link.link_id)
        bler = record.bler if record else None
        color = _link_color_by_bler(bler)

        if record:
            hover_text = (
                f"<b>{link.link_id}</b><br>"
                f"SNR: {record.snr_db:.2f} dB<br>"
                f"SINR: {record.sinr_db:.2f} dB<br>"
                f"BLER: {record.bler:.4f}<br>"
                f"MCS: {record.mcs}<br>"
                f"Modulation: {record.modulation}<br>"
                f"Coding: {record.coding}<br>"
                f"Throughput: {record.throughput_kbps:.2f} kbps<br>"
                f"Latency: {record.latency_ms:.2f} ms"
            )
        else:
            hover_text = f"<b>{link.link_id}</b><br>No KPI yet"

        fig.add_trace(
            go.Scatter(
                x=[src.position.x, dst.position.x],
                y=[src.position.y, dst.position.y],
                mode="lines",
                line=dict(width=4, color=color),
                hovertext=hover_text,
                hoverinfo="text",
                showlegend=False,
            )
        )

    for node in topology.nodes:
        symbol, color = _node_style(node.node_type)

        hover_text = (
            f"<b>{node.name}</b><br>"
            f"ID: {node.node_id}<br>"
            f"Type: {node.node_type}<br>"
            f"TX Power: {node.tx_power_dbm:.1f} dBm<br>"
            f"Position: ({node.position.x:.1f}, {node.position.y:.1f})"
        )

        fig.add_trace(
            go.Scatter(
                x=[node.position.x],
                y=[node.position.y],
                mode="markers+text",
                marker=dict(size=18, symbol=symbol, color=color),
                text=[node.name],
                textposition="top center",
                hovertext=hover_text,
                hoverinfo="text",
                name=node.name,
            )
        )

    fig.update_layout(
        title="Network Topology and Link Quality",
        xaxis_title="X Position (m)",
        yaxis_title="Y Position (m)",
        height=460,
        template="plotly_white",
        legend_title="Nodes",
    )

    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig