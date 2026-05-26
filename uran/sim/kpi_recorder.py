from pydantic import BaseModel


class LinkKPIRecord(BaseModel):
    step: int
    time_s: float
    link_id: str

    source_node_id: str
    target_node_id: str

    snr_db: float
    sinr_db: float
    bler: float
    throughput_kbps: float
    latency_ms: float

    mcs: int
    modulation: str
    coding: str
    coding_rate: float
    spectral_efficiency: float
    pilot_density: float
    tx_power_dbm: float
    harq_retx: int

    packet_success_rate: float
    reliability: float

    event: str | None = None
    event_level: str = "info"


class KPIRecorder:
    def __init__(self):
        self.records: list[LinkKPIRecord] = []

    def append(self, record: LinkKPIRecord) -> None:
        self.records.append(record)

    def extend(self, records: list[LinkKPIRecord]) -> None:
        self.records.extend(records)

    def clear(self) -> None:
        self.records.clear()

    def latest_records_by_link(self) -> dict[str, LinkKPIRecord]:
        latest = {}
        for record in self.records:
            latest[record.link_id] = record
        return latest

    def to_dataframe(self):
        import pandas as pd

        if not self.records:
            return pd.DataFrame()

        return pd.DataFrame([record.model_dump() for record in self.records])

    def get_previous_bler(self, link_id: str) -> float | None:
        for record in reversed(self.records):
            if record.link_id == link_id:
                return record.bler
        return None