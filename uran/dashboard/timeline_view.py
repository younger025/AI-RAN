def build_event_timeline(df):
    if df is None or df.empty:
        return []

    events = []

    for link_id in df["link_id"].unique():
        sub = df[df["link_id"] == link_id].sort_values("step")

        last_mcs = None
        last_modulation = None
        last_coding_rate = None
        last_harq = None

        for _, row in sub.iterrows():
            time_s = row["time_s"]

            if last_mcs is None:
                events.append(
                    {
                        "time_s": time_s,
                        "link_id": link_id,
                        "event": "Link Established",
                        "detail": f"Initial mode: MCS={row['mcs']}, {row['modulation']}, coding_rate={row['coding_rate']:.2f}",
                        "level": "success",
                    }
                )
            else:
                if row["mcs"] != last_mcs:
                    events.append(
                        {
                            "time_s": time_s,
                            "link_id": link_id,
                            "event": "MCS Changed",
                            "detail": f"MCS {last_mcs} -> {row['mcs']}",
                            "level": "warning",
                        }
                    )

                if row["modulation"] != last_modulation:
                    events.append(
                        {
                            "time_s": time_s,
                            "link_id": link_id,
                            "event": "Modulation Changed",
                            "detail": f"{last_modulation} -> {row['modulation']}",
                            "level": "warning",
                        }
                    )

                if abs(row["coding_rate"] - last_coding_rate) > 1e-6:
                    events.append(
                        {
                            "time_s": time_s,
                            "link_id": link_id,
                            "event": "Coding Rate Changed",
                            "detail": f"{last_coding_rate:.2f} -> {row['coding_rate']:.2f}",
                            "level": "info",
                        }
                    )

                if row["harq_retx"] != last_harq:
                    events.append(
                        {
                            "time_s": time_s,
                            "link_id": link_id,
                            "event": "HARQ Policy Changed",
                            "detail": f"HARQ retx {last_harq} -> {row['harq_retx']}",
                            "level": "info",
                        }
                    )

                if row["sinr_db"] < 4:
                    events.append(
                        {
                            "time_s": time_s,
                            "link_id": link_id,
                            "event": "Robust Mode Activated",
                            "detail": f"SINR={row['sinr_db']:.2f} dB, robust communication mode enabled",
                            "level": "critical",
                        }
                    )

            last_mcs = row["mcs"]
            last_modulation = row["modulation"]
            last_coding_rate = row["coding_rate"]
            last_harq = row["harq_retx"]

    events = sorted(events, key=lambda x: x["time_s"])

    return events


def render_event_timeline(events, max_events: int = 30):
    import streamlit as st
    import pandas as pd

    if not events:
        st.info("No events yet.")
        return

    df = pd.DataFrame(events[-max_events:])

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )