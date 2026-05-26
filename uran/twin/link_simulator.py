import math
from typing import Optional
from uran.ai.plan_schema import PlanSpec
from uran.ai.intent_schema import EnvironmentSpec
from uran.common.band_config import BandConfig
from uran.common.demo_defaults import (
    CODING_GAIN_DB,
    PILOT_GAIN_DB,
    PILOT_EFFICIENCY,
    MODULATION_PENALTY_DB,
    MODULATION_THRESHOLD_DB,
    MODULATION_BITS_PER_SYMBOL,
    INTERFERENCE_PENALTY_DB,
    CODING_DELAY_MS,
    SCHEDULER_DELAY_MS,
)


class LinkLevelSimulator:
    def __init__(self, bandwidth_khz: float = 1000, band_config: Optional[BandConfig] = None):
        if band_config is not None:
            self.bandwidth_khz = band_config.bandwidth_khz
            self.freq_penalty_db = band_config.freq_penalty_db
        else:
            self.bandwidth_khz = bandwidth_khz
            self.freq_penalty_db = 0.0

    def simulate(self, plan: PlanSpec, environment: EnvironmentSpec):
        eff_sinr = environment.avg_sinr_db

        eff_sinr -= self.freq_penalty_db

        eff_sinr += CODING_GAIN_DB.get(plan.coding_scheme, 3)
        eff_sinr += PILOT_GAIN_DB.get(plan.pilot_density, 1)
        eff_sinr += self._harq_gain(plan.harq_max_retx if plan.harq_enabled else 0)
        eff_sinr += self._power_gain(plan.tx_power_dbm)
        eff_sinr -= MODULATION_PENALTY_DB.get(plan.modulation, 4)
        eff_sinr += INTERFERENCE_PENALTY_DB.get(environment.interference_level, -2)

        threshold = MODULATION_THRESHOLD_DB.get(plan.modulation, 4)
        bler = 1.0 / (1.0 + math.exp(eff_sinr - threshold))
        bler = min(max(bler, 0.0001), 0.999)

        se = MODULATION_BITS_PER_SYMBOL.get(plan.modulation, 2) * plan.coding_rate
        pilot_eff = PILOT_EFFICIENCY.get(plan.pilot_density, 0.88)
        harq_eff = 1.0 / (1.0 + 0.25 * (plan.harq_max_retx if plan.harq_enabled else 0))

        throughput = self.bandwidth_khz * se * (1.0 - bler) * pilot_eff * harq_eff

        latency = self._latency(plan)
        energy = self._energy_cost(plan)

        return {
            "effective_sinr_db": eff_sinr,
            "bler": bler,
            "throughput_kbps": throughput,
            "latency_ms": latency,
            "spectral_efficiency": se,
            "energy_cost": energy,
        }

    def _harq_gain(self, harq_max_retx: int) -> float:
        return harq_max_retx * 1.2

    def _power_gain(self, tx_power_dbm: float) -> float:
        return max(0.0, min(4.0, (tx_power_dbm - 10.0) / 5.0))

    def _latency(self, plan: PlanSpec) -> float:
        base_latency = 10.0
        harq_latency = (plan.harq_max_retx if plan.harq_enabled else 0) * 8
        coding_delay = CODING_DELAY_MS.get(plan.coding_scheme, 8)
        scheduler_delay = SCHEDULER_DELAY_MS.get(plan.scheduler, 5)
        return base_latency + harq_latency + coding_delay + scheduler_delay

    def _energy_cost(self, plan: PlanSpec) -> float:
        base_energy = 10 ** (plan.tx_power_dbm / 10.0) / 1000.0
        harq_penalty = 1 + 0.05 * (plan.harq_max_retx if plan.harq_enabled else 0)
        return base_energy * harq_penalty