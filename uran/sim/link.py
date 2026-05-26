from pydantic import BaseModel


class CommLink(BaseModel):
    link_id: str
    source_node_id: str
    target_node_id: str

    active: bool = True

    distance_m: float = 0.0
    path_loss_db: float = 0.0

    snr_db: float = 10.0
    sinr_db: float = 10.0
    interference_dbm: float = -100.0

    current_mcs: int = 0
    current_modulation: str = "QPSK"
    current_coding: str = "ConvCodeRate13"
    current_coding_rate: float = 0.33
    current_pilot_density: float = 0.25
    current_harq_retx: int = 2
    current_tx_power_dbm: float = 20.0

    established: bool = False

    def mark_established(self) -> None:
        self.established = True

    def update_adaptation_state(
        self,
        mcs: int,
        modulation: str,
        coding: str,
        coding_rate: float,
        pilot_density: float,
        harq_retx: int,
        tx_power_dbm: float,
    ) -> None:
        self.current_mcs = mcs
        self.current_modulation = modulation
        self.current_coding = coding
        self.current_coding_rate = coding_rate
        self.current_pilot_density = pilot_density
        self.current_harq_retx = harq_retx
        self.current_tx_power_dbm = tx_power_dbm