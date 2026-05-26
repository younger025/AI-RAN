from copy import deepcopy
from uran.ai.intent_schema import EnvironmentSpec


class FaultInjector:
    def apply(self, environment: EnvironmentSpec, fault_type: str) -> EnvironmentSpec:
        env = deepcopy(environment)

        if fault_type == "sudden_snr_drop":
            env.avg_snr_db -= 10
            env.avg_sinr_db -= 10
        elif fault_type == "burst_interference":
            env.interference_level = "high"
            env.avg_sinr_db -= 5
        elif fault_type == "high_mobility":
            env.doppler_hz *= 3
            env.avg_sinr_db -= 2
        elif fault_type == "power_limit":
            env.avg_sinr_db -= 3
        elif fault_type == "module_failure":
            env.avg_sinr_db -= 8

        return env