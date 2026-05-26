import math
from typing import Optional
from uran.sim.adaptation import modulation_order, required_snr_for_modulation
from uran.common.band_config import BandConfig, BAND_PRESETS


class KPIModel:
    def __init__(
        self,
        bandwidth_khz: float = 500.0,
        base_latency_ms: float = 10.0,
        band_config: Optional[BandConfig] = None,
    ):
        if band_config is not None:
            self.bandwidth_khz = band_config.bandwidth_khz
            self.freq_penalty_db = band_config.freq_penalty_db
        else:
            self.bandwidth_khz = bandwidth_khz
            self.freq_penalty_db = 0.0
        self.base_latency_ms = base_latency_ms

    def estimate(
        self,
        snr_db: float,
        sinr_db: float,
        modulation: str,
        coding_rate: float,
        pilot_density: float,
        harq_retx: int,
    ) -> dict:
        bits_per_symbol = modulation_order(modulation)
        required_snr = required_snr_for_modulation(modulation)

        effective_sinr = sinr_db - self.freq_penalty_db

        margin = effective_sinr - required_snr

        bler = 1.0 / (1.0 + math.exp(margin))
        bler = max(0.0001, min(0.99, bler))

        spectral_efficiency = bits_per_symbol * coding_rate

        pilot_efficiency = max(0.0, min(1.0, 1.0 - pilot_density))
        harq_efficiency = 1.0 / (1.0 + 0.25 * harq_retx)
        packet_success_rate = 1.0 - bler

        throughput_kbps = (
            self.bandwidth_khz
            * spectral_efficiency
            * pilot_efficiency
            * harq_efficiency
            * packet_success_rate
        )

        latency_ms = (
            self.base_latency_ms
            + 8.0 * harq_retx
            + 8.0 * (1.0 - coding_rate)
            + 20.0 * pilot_density
        )

        reliability = max(0.0, min(1.0, packet_success_rate))

        return {
            "bler": bler,
            "throughput_kbps": throughput_kbps,
            "latency_ms": latency_ms,
            "spectral_efficiency": spectral_efficiency,
            "packet_success_rate": packet_success_rate,
            "reliability": reliability,
        }