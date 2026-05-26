from pydantic import BaseModel


class LinkAdaptationDecision(BaseModel):
    mcs: int
    modulation: str
    coding: str
    coding_rate: float
    pilot_density: float
    harq_retx: int
    tx_power_dbm: float
    reason: str
    event_level: str = "info"


class LinkAdaptationController:
    def __init__(self, target_bler: float = 0.1):
        self.target_bler = target_bler

    def decide(
        self,
        snr_db: float,
        sinr_db: float | None = None,
        previous_bler: float | None = None,
    ) -> LinkAdaptationDecision:
        quality_db = sinr_db if sinr_db is not None else snr_db

        bler_penalty = 0.0
        if previous_bler is not None and previous_bler > self.target_bler:
            bler_penalty = 2.0

        effective_quality = quality_db - bler_penalty

        if effective_quality >= 16.0:
            return LinkAdaptationDecision(
                mcs=8,
                modulation="64QAM",
                coding="ldpc_mock_3_4",
                coding_rate=0.75,
                pilot_density=0.0625,
                harq_retx=0,
                tx_power_dbm=14.0,
                reason="High channel quality: select high-throughput 64QAM/LDPC mode",
                event_level="success",
            )

        if effective_quality >= 10.0:
            return LinkAdaptationDecision(
                mcs=6,
                modulation="16QAM",
                coding="ldpc_mock_2_3",
                coding_rate=0.66,
                pilot_density=0.125,
                harq_retx=1,
                tx_power_dbm=16.0,
                reason="Good channel quality: select balanced 16QAM/LDPC mode",
                event_level="info",
            )

        if effective_quality >= 4.0:
            return LinkAdaptationDecision(
                mcs=3,
                modulation="QPSK",
                coding="convolutional_1_2",
                coding_rate=0.5,
                pilot_density=0.125,
                harq_retx=2,
                tx_power_dbm=18.0,
                reason="Medium channel quality: lower MCS to maintain reliability",
                event_level="warning",
            )

        return LinkAdaptationDecision(
            mcs=1,
            modulation="BPSK",
            coding="repetition_3",
            coding_rate=0.33,
            pilot_density=0.25,
            harq_retx=4,
            tx_power_dbm=20.0,
            reason="Low channel quality: switch to robust safe communication mode",
            event_level="critical",
        )


def modulation_order(modulation: str) -> int:
    mapping = {
        "BPSK": 1,
        "QPSK": 2,
        "16QAM": 4,
        "QAM16": 4,
        "64QAM": 6,
        "QAM64": 6,
        "QAM256": 8,
    }
    return mapping.get(modulation, 2)


def required_snr_for_modulation(modulation: str) -> float:
    mapping = {
        "BPSK": -2.0,
        "QPSK": 2.0,
        "16QAM": 8.0,
        "QAM16": 8.0,
        "64QAM": 14.0,
        "QAM64": 14.0,
        "QAM256": 20.0,
    }
    return mapping.get(modulation, 2.0)