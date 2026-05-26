import pytest
from uran.common.band_config import (
    BandConfig,
    BAND_PRESETS,
    get_band_config,
    build_custom_band,
)


class TestBandConfig:
    def test_bandwidth_khz_conversion(self):
        cfg = BandConfig(
            name="test",
            description="test",
            carrier_freq_mhz=2600,
            bandwidth_mhz=100,
        )
        assert cfg.bandwidth_khz == 100000.0

    def test_freq_penalty_same_freq_is_zero(self):
        cfg = BandConfig(
            name="test",
            description="test",
            carrier_freq_mhz=2600,
            bandwidth_mhz=100,
        )
        assert cfg.freq_penalty_db == pytest.approx(0.0, abs=1e-6)

    def test_freq_penalty_higher_freq(self):
        cfg = BandConfig(
            name="test",
            description="test",
            carrier_freq_mhz=4900,
            bandwidth_mhz=100,
        )
        assert cfg.freq_penalty_db > 2.0

    def test_n41_preset(self):
        cfg = BAND_PRESETS["n41_100mhz"]
        assert cfg.name == "n41"
        assert cfg.carrier_freq_mhz == 2600.0
        assert cfg.bandwidth_mhz == 100.0
        assert cfg.bandwidth_khz == 100000.0

    def test_n79_preset(self):
        cfg = BAND_PRESETS["n79_100mhz"]
        assert cfg.name == "n79"
        assert cfg.carrier_freq_mhz == 4900.0
        assert cfg.bandwidth_mhz == 100.0

    def test_n79_penalty_greater_than_n41(self):
        n41 = BAND_PRESETS["n41_100mhz"]
        n79 = BAND_PRESETS["n79_100mhz"]
        assert n79.freq_penalty_db > n41.freq_penalty_db

    def test_sim_default_is_small_bandwidth(self):
        cfg = BAND_PRESETS["sim_default"]
        assert cfg.bandwidth_mhz == 0.5
        assert cfg.bandwidth_khz == 500.0

    def test_get_band_config_valid(self):
        cfg = get_band_config("n41_100mhz")
        assert cfg.name == "n41"

    def test_get_band_config_invalid_falls_back(self):
        cfg = get_band_config("nonexistent")
        assert cfg == BAND_PRESETS["sim_default"]

    def test_build_custom_band(self):
        cfg = build_custom_band(carrier_freq_mhz=3500, bandwidth_mhz=80)
        assert cfg.name == "custom"
        assert cfg.carrier_freq_mhz == 3500
        assert cfg.bandwidth_mhz == 80
        assert cfg.bandwidth_khz == 80000.0

    def test_n41_vs_n79_throughput_ratio(self):
        n41 = BAND_PRESETS["n41_100mhz"]
        n79 = BAND_PRESETS["n79_100mhz"]
        assert n41.bandwidth_khz == n79.bandwidth_khz


from uran.sim.kpi_model import KPIModel


class TestKPIModelWithBandConfig:
    def test_default_no_penalty(self):
        kpi = KPIModel()
        result = kpi.estimate(
            snr_db=10, sinr_db=8,
            modulation="QPSK", coding_rate=0.5,
            pilot_density=0.1, harq_retx=1,
        )
        assert result["throughput_kbps"] > 0

    def test_n41_band_affects_throughput(self):
        n41 = get_band_config("n41_100mhz")
        kpi = KPIModel(band_config=n41)
        result = kpi.estimate(
            snr_db=10, sinr_db=8,
            modulation="QPSK", coding_rate=0.5,
            pilot_density=0.1, harq_retx=1,
        )
        assert result["throughput_kbps"] > 1000

    def test_different_bandwidth_different_throughput(self):
        n41 = get_band_config("n41_100mhz")
        sim = get_band_config("sim_default")
        kpi_n41 = KPIModel(band_config=n41)
        kpi_sim = KPIModel(band_config=sim)
        args = dict(snr_db=10, sinr_db=8, modulation="QPSK",
                    coding_rate=0.5, pilot_density=0.1, harq_retx=1)
        result_n41 = kpi_n41.estimate(**args)
        result_sim = kpi_sim.estimate(**args)
        ratio = result_n41["throughput_kbps"] / result_sim["throughput_kbps"]
        expected_ratio = 100000 / 500
        assert ratio == pytest.approx(expected_ratio, rel=0.01)

    def test_n79_penalty_increases_bler(self):
        n41 = get_band_config("n41_100mhz")
        n79 = get_band_config("n79_100mhz")
        kpi_n41 = KPIModel(band_config=n41)
        kpi_n79 = KPIModel(band_config=n79)
        args = dict(snr_db=5, sinr_db=3, modulation="BPSK",
                    coding_rate=0.33, pilot_density=0.2, harq_retx=2)
        result_n41 = kpi_n41.estimate(**args)
        result_n79 = kpi_n79.estimate(**args)
        assert result_n79["bler"] >= result_n41["bler"]
