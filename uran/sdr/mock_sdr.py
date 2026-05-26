import math
import numpy as np
from uran.sdr.adapter_base import SDRAdapterBase
from uran.sdr.waveform import generate_iq_symbols, add_awgn
from uran.sdr.spectrum import estimate_psd


class MockSDRAdapter(SDRAdapterBase):
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.config = {}
        self.rng = np.random.default_rng(seed)

    def configure(self, config):
        self.config.update(config)

    def transmit(self, iq_samples: np.ndarray):
        return {
            "tx_samples": len(iq_samples),
            "status": "TX_OK",
        }

    def receive(self, duration_ms: int = 10) -> np.ndarray:
        modulation = self.config.get("modulation", "QPSK")
        snr_db = self.config.get("snr_db", 10.0)
        samples = generate_iq_symbols(modulation, 1024, self.seed)
        return add_awgn(samples, snr_db, self.seed)

    def measure_spectrum(self):
        samples = self.receive()
        freqs, psd = estimate_psd(samples)
        return {
            "freqs": freqs,
            "psd": psd,
        }

    def measure_metrics(self):
        modulation = self.config.get("modulation", "QPSK")
        snr_db = self.config.get("snr_db", 10.0)
        snr_linear = 10 ** (snr_db / 10)

        if modulation == "BPSK":
            ber = 0.5 * math.exp(-snr_linear)
        elif modulation == "QPSK":
            ber = 0.7 * math.exp(-0.8 * snr_linear)
        elif modulation == "16QAM":
            ber = math.exp(-0.25 * snr_linear)
        elif modulation == "64QAM":
            ber = math.exp(-0.12 * snr_linear)
        else:
            ber = 1.0

        ber = float(np.clip(ber, 1e-8, 0.5))
        evm_percent = float(100 / math.sqrt(max(snr_linear, 1e-9)))
        packet_loss = float(np.clip(1 - (1 - ber) ** 1000, 0, 1))
        latency_ms = float(5 + 50 * packet_loss + self.rng.normal(0, 0.5))

        return {
            "ber": ber,
            "evm_percent": evm_percent,
            "packet_loss": packet_loss,
            "latency_ms": latency_ms,
            "snr_db": snr_db,
            "modulation": modulation,
        }

    def close(self) -> None:
        pass