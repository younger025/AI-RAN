import pytest
import numpy as np
from uran.sdr.mock_sdr import MockSDRAdapter
from uran.sdr.waveform import generate_iq_symbols, add_awgn
from uran.sdr.spectrum import estimate_psd


class TestWaveform:
    def test_generate_bpsk(self):
        samples = generate_iq_symbols("BPSK", 1024, seed=42)
        assert len(samples) == 1024
        assert np.all(np.abs(samples.real) <= 1.1)
        assert np.all(np.abs(samples.imag) < 1e-9)

    def test_generate_qpsk(self):
        samples = generate_iq_symbols("QPSK", 1024, seed=42)
        assert len(samples) == 1024
        assert np.all(np.abs(samples.real) <= 1.1)
        assert np.all(np.abs(samples.imag) <= 1.1)

    def test_generate_16qam(self):
        samples = generate_iq_symbols("16QAM", 1024, seed=42)
        assert len(samples) == 1024

    def test_generate_64qam(self):
        samples = generate_iq_symbols("64QAM", 1024, seed=42)
        assert len(samples) == 1024

    def test_unsupported_modulation_raises(self):
        with pytest.raises(ValueError):
            generate_iq_symbols("256QAM", 1024)

    def test_add_awgn_reduces_snr(self):
        clean = generate_iq_symbols("QPSK", 4096, seed=42)
        noisy_low = add_awgn(clean, 5.0, seed=42)
        noisy_high = add_awgn(clean, 20.0, seed=42)
        diff_low = np.mean(np.abs(noisy_low - clean) ** 2)
        diff_high = np.mean(np.abs(noisy_high - clean) ** 2)
        assert diff_low > diff_high

    def test_add_awgn_handles_zero_signal(self):
        zeros = np.zeros(1000, dtype=np.complex128)
        result = add_awgn(zeros, 10.0, seed=42)
        assert np.allclose(result, zeros)


class TestSpectrum:
    def test_estimate_psd_shape(self):
        samples = generate_iq_symbols("QPSK", 1024, seed=42)
        freqs, psd = estimate_psd(samples)
        assert len(freqs) == len(samples)
        assert len(psd) == len(samples)
        assert np.isfinite(psd).all()


class TestMockSDR:
    def test_configure_and_measure(self):
        sdr = MockSDRAdapter(seed=42)
        sdr.configure({"modulation": "QPSK", "snr_db": 10.0})
        metrics = sdr.measure_metrics()
        assert "ber" in metrics
        assert "evm_percent" in metrics
        assert "packet_loss" in metrics
        assert "latency_ms" in metrics
        assert metrics["modulation"] == "QPSK"

    def test_ber_decreases_with_snr(self):
        sdr_low = MockSDRAdapter(seed=42)
        sdr_low.configure({"modulation": "QPSK", "snr_db": 0.0})

        sdr_high = MockSDRAdapter(seed=42)
        sdr_high.configure({"modulation": "QPSK", "snr_db": 20.0})

        assert sdr_low.measure_metrics()["ber"] > sdr_high.measure_metrics()["ber"]

    def test_bpsk_more_robust_than_64qam(self):
        sdr_bpsk = MockSDRAdapter(seed=42)
        sdr_bpsk.configure({"modulation": "BPSK", "snr_db": 3.0})

        sdr_64qam = MockSDRAdapter(seed=42)
        sdr_64qam.configure({"modulation": "64QAM", "snr_db": 3.0})

        assert sdr_bpsk.measure_metrics()["ber"] < sdr_64qam.measure_metrics()["ber"]

    def test_transmit_returns_status(self):
        sdr = MockSDRAdapter(seed=42)
        samples = generate_iq_symbols("QPSK", 256)
        result = sdr.transmit(samples)
        assert result["status"] == "TX_OK"
        assert result["tx_samples"] == 256

    def test_receive_returns_correct_shape(self):
        sdr = MockSDRAdapter(seed=42)
        sdr.configure({"modulation": "QPSK", "snr_db": 10.0})
        samples = sdr.receive(duration_ms=10)
        assert len(samples) == 1024
        assert samples.dtype == np.complex128

    def test_measure_spectrum(self):
        sdr = MockSDRAdapter(seed=42)
        sdr.configure({"modulation": "QPSK", "snr_db": 10.0})
        spectrum = sdr.measure_spectrum()
        assert "freqs" in spectrum
        assert "psd" in spectrum
        assert len(spectrum["freqs"]) == len(spectrum["psd"])

    def test_metrics_are_reasonable(self):
        sdr = MockSDRAdapter(seed=42)
        sdr.configure({"modulation": "QPSK", "snr_db": 15.0})
        metrics = sdr.measure_metrics()
        assert 0 <= metrics["ber"] <= 1
        assert 0 <= metrics["packet_loss"] <= 1
        assert metrics["evm_percent"] >= 0
        assert metrics["latency_ms"] >= 0