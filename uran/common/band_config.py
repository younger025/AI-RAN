from dataclasses import dataclass, field
import math


@dataclass
class BandConfig:
    name: str
    description: str
    carrier_freq_mhz: float
    bandwidth_mhz: float
    band_range: str = ""

    @property
    def bandwidth_khz(self) -> float:
        return self.bandwidth_mhz * 1000.0

    @property
    def freq_penalty_db(self) -> float:
        ref_freq = 2600.0
        if self.carrier_freq_mhz <= 0:
            return 0.0
        return 20.0 * math.log10(self.carrier_freq_mhz / ref_freq)


BAND_PRESETS: dict[str, BandConfig] = {
    "n41_100mhz": BandConfig(
        name="n41",
        description="n41 2.6GHz 100MHz — 中国移动主力频段",
        carrier_freq_mhz=2600.0,
        bandwidth_mhz=100.0,
        band_range="2575–2675 MHz",
    ),
    "n79_100mhz": BandConfig(
        name="n79",
        description="n79 4.9GHz 100MHz — 高速热点覆盖",
        carrier_freq_mhz=4900.0,
        bandwidth_mhz=100.0,
        band_range="4800–4900 MHz",
    ),
    "n41_50mhz": BandConfig(
        name="n41",
        description="n41 2.6GHz 50MHz — 中等带宽配置",
        carrier_freq_mhz=2600.0,
        bandwidth_mhz=50.0,
        band_range="2575–2625 MHz",
    ),
    "sim_default": BandConfig(
        name="仿真默认",
        description="仿真默认 500kHz — 小带宽快速仿真",
        carrier_freq_mhz=2600.0,
        bandwidth_mhz=0.5,
        band_range="—",
    ),
}


def get_band_config(key: str) -> BandConfig:
    if key in BAND_PRESETS:
        return BAND_PRESETS[key]
    return BAND_PRESETS["sim_default"]


def build_custom_band(carrier_freq_mhz: float, bandwidth_mhz: float) -> BandConfig:
    return BandConfig(
        name="custom",
        description=f"自定义 {carrier_freq_mhz:.0f}MHz / {bandwidth_mhz:.1f}MHz",
        carrier_freq_mhz=carrier_freq_mhz,
        bandwidth_mhz=bandwidth_mhz,
        band_range=f"{carrier_freq_mhz - bandwidth_mhz / 2:.0f}–{carrier_freq_mhz + bandwidth_mhz / 2:.0f} MHz",
    )
