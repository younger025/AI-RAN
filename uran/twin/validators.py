from uran.ai.plan_schema import PlanSpec
from uran.ai.intent_schema import IntentSpec
from uran.common.demo_defaults import (
    SUPPORTED_MODULATIONS,
    SUPPORTED_CODING_SCHEMES,
    SUPPORTED_PILOT_DENSITIES,
    SUPPORTED_SCHEDULERS,
    SUPPORTED_POWER_CONTROL,
)


class InterfaceValidator:
    def validate(self, plan: PlanSpec):
        errors = []
        required_fields = [
            "modulation", "coding_scheme", "coding_rate", "mcs",
            "harq_enabled", "harq_max_retx", "pilot_density",
            "tx_power_dbm", "scheduler", "power_control",
        ]

        for field in required_fields:
            if not hasattr(plan, field):
                errors.append(f"Missing required field: {field}")
                continue
            value = getattr(plan, field)
            if value is None:
                errors.append(f"Field '{field}' is None")

        return len(errors) == 0, errors


class ConstraintValidator:
    def validate(self, plan: PlanSpec, intent: IntentSpec):
        errors = []
        warnings = []

        if plan.modulation not in SUPPORTED_MODULATIONS:
            errors.append(f"Unsupported modulation: '{plan.modulation}'. Must be one of {SUPPORTED_MODULATIONS}")

        if plan.coding_scheme not in SUPPORTED_CODING_SCHEMES:
            errors.append(f"Unsupported coding scheme: '{plan.coding_scheme}'. Must be one of {SUPPORTED_CODING_SCHEMES}")

        if plan.coding_rate < 0.1 or plan.coding_rate > 0.95:
            errors.append(f"Coding rate {plan.coding_rate} out of range [0.1, 0.95]")

        if plan.mcs < 0 or plan.mcs > 28:
            errors.append(f"MCS {plan.mcs} out of range [0, 28]")

        if plan.harq_max_retx < 0 or plan.harq_max_retx > 8:
            errors.append(f"HARQ max retx {plan.harq_max_retx} out of range [0, 8]")

        if plan.tx_power_dbm < 0 or plan.tx_power_dbm > 30:
            errors.append(f"TX power {plan.tx_power_dbm} dBm out of range [0, 30]")

        if plan.pilot_density not in SUPPORTED_PILOT_DENSITIES:
            errors.append(f"Unsupported pilot density: '{plan.pilot_density}'. Must be one of {SUPPORTED_PILOT_DENSITIES}")

        if plan.scheduler not in SUPPORTED_SCHEDULERS:
            errors.append(f"Unsupported scheduler: '{plan.scheduler}'. Must be one of {SUPPORTED_SCHEDULERS}")

        if plan.power_control not in SUPPORTED_POWER_CONTROL:
            errors.append(f"Unsupported power control: '{plan.power_control}'. Must be one of {SUPPORTED_POWER_CONTROL}")

        if plan.tx_power_dbm > intent.max_tx_power_dbm:
            errors.append(
                f"TX power {plan.tx_power_dbm} dBm exceeds maximum allowed {intent.max_tx_power_dbm} dBm"
            )

        if intent.priority == "reliability" and plan.modulation in ["64QAM"]:
            warnings.append(
                "64QAM modulation may be unreliable under reliability-constrained scenarios."
            )

        if intent.priority == "latency" and plan.harq_max_retx >= 4:
            warnings.append(
                "High HARQ retransmission count may increase latency beyond latency-constrained objectives."
            )

        if intent.priority == "energy" and plan.tx_power_dbm > 20:
            warnings.append(
                "TX power exceeds typical energy-saving range for low-power scenarios."
            )

        if intent.priority == "throughput" and plan.modulation == "BPSK":
            warnings.append(
                "BPSK modulation limits throughput and may not meet high-throughput requirements."
            )

        return len(errors) == 0, errors, warnings