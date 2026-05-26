from uran.ai.agent_base import AgentBase
from uran.ai.intent_schema import EnvironmentSpec, IntentSpec

DEFAULT_ENVIRONMENT = {
    "emergency": EnvironmentSpec(
        avg_snr_db=-3, avg_sinr_db=-5, doppler_hz=20,
        interference_level="medium", channel_type="rayleigh",
        node_count=5, mobility_level="low", spectrum_congestion="low",
    ),
    "high_throughput": EnvironmentSpec(
        avg_snr_db=18, avg_sinr_db=16, doppler_hz=5,
        interference_level="low", channel_type="awgn",
        node_count=50, mobility_level="low", spectrum_congestion="high",
    ),
    "anti_jamming": EnvironmentSpec(
        avg_snr_db=5, avg_sinr_db=0, doppler_hz=30,
        interference_level="high", channel_type="fading",
        node_count=8, mobility_level="low", spectrum_congestion="medium",
    ),
    "low_latency": EnvironmentSpec(
        avg_snr_db=10, avg_sinr_db=8, doppler_hz=80,
        interference_level="medium", channel_type="rician",
        node_count=3, mobility_level="high", spectrum_congestion="low",
    ),
    "satellite_iot": EnvironmentSpec(
        avg_snr_db=0, avg_sinr_db=-2, doppler_hz=100,
        interference_level="low", channel_type="rician",
        node_count=100, mobility_level="high", spectrum_congestion="low",
    ),
    "balanced": EnvironmentSpec(
        avg_snr_db=8, avg_sinr_db=6, doppler_hz=20,
        interference_level="low", channel_type="rayleigh",
        node_count=10, mobility_level="medium", spectrum_congestion="medium",
    ),
}


class EnvironmentAgent(AgentBase):
    def __init__(self):
        super().__init__("EnvironmentAgent")

    def run(self, intent: IntentSpec, environment: EnvironmentSpec = None) -> EnvironmentSpec:
        self.log(f"Analyzing environment for scenario: {intent.scenario_type}")

        if environment is not None:
            self.log("Using externally provided EnvironmentSpec")
            return environment

        env = DEFAULT_ENVIRONMENT.get(intent.scenario_type, DEFAULT_ENVIRONMENT["balanced"])
        self.log(f"Generated default environment: SNR={env.avg_snr_db}dB, SINR={env.avg_sinr_db}dB")
        self.log(f"Channel: {env.channel_type}, Doppler: {env.doppler_hz}Hz, Interference: {env.interference_level}")
        return env