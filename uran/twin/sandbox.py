from uran.ai.plan_schema import PlanSpec
from uran.ai.intent_schema import IntentSpec, EnvironmentSpec
from uran.twin.report import TwinValidationReport
from uran.twin.validators import InterfaceValidator, ConstraintValidator
from uran.twin.link_simulator import LinkLevelSimulator
from uran.twin.fault_injection import FaultInjector
from uran.twin.scoring import TwinScorer
from uran.common.ids import new_id
from uran.common.band_config import BandConfig
from typing import Optional


class DigitalTwinSandbox:
    def __init__(self, bandwidth_khz: float = 1000, band_config: Optional[BandConfig] = None):
        self.band_config = band_config
        self.bandwidth_khz = band_config.bandwidth_khz if band_config else bandwidth_khz
        self.interface_validator = InterfaceValidator()
        self.constraint_validator = ConstraintValidator()
        self.simulator = LinkLevelSimulator(bandwidth_khz, band_config=band_config)
        self.fault_injector = FaultInjector()
        self.scorer = TwinScorer()

    def validate(self, plan: PlanSpec, intent: IntentSpec, environment: EnvironmentSpec) -> TwinValidationReport:
        warnings = []
        errors = []

        interface_ok, interface_errors = self.interface_validator.validate(plan)
        errors.extend(interface_errors)

        constraint_ok, constraint_errors, constraint_warnings = self.constraint_validator.validate(plan, intent)
        errors.extend(constraint_errors)
        warnings.extend(constraint_warnings)

        if errors:
            return TwinValidationReport(
                report_id=new_id("report"),
                plan_id=plan.plan_id,
                passed=False,
                decision="REJECT",
                interface_check_passed=interface_ok,
                constraint_check_passed=constraint_ok,
                link_sim_passed=False,
                fault_test_passed=False,
                fallback_test_passed=False,
                bler=1.0,
                throughput_kbps=0,
                latency_ms=999,
                spectral_efficiency=0,
                energy_cost=999,
                robustness_score=0,
                final_score=0,
                warnings=warnings,
                errors=errors,
                suggestions=["Fix validation errors before re-submitting."],
            )

        metrics = self.simulator.simulate(plan, environment)

        fault_results = []
        for fault_type in ["sudden_snr_drop", "burst_interference"]:
            fault_env = self.fault_injector.apply(environment, fault_type)
            fault_metrics = self.simulator.simulate(plan, fault_env)
            fault_results.append(fault_metrics)

        score_result = self.scorer.score(metrics, intent, fault_results)
        final_score = score_result["final_score"]
        robustness_score = score_result["robustness_score"]

        link_sim_passed = (
            metrics["bler"] <= max(intent.target_bler * 3, 0.05)
            and metrics["latency_ms"] <= intent.max_latency_ms * 2
        )

        fault_test_passed = robustness_score >= 40

        fallback_test_passed = True

        if final_score >= 75 and link_sim_passed and fault_test_passed:
            decision = "ACCEPT"
            passed = True
        elif final_score >= 60:
            decision = "NEED_REVISE"
            passed = True
        else:
            decision = "REJECT"
            passed = False

        suggestions = self._generate_suggestions(metrics, intent)

        return TwinValidationReport(
            report_id=new_id("report"),
            plan_id=plan.plan_id,
            passed=passed,
            decision=decision,
            interface_check_passed=interface_ok,
            constraint_check_passed=constraint_ok,
            link_sim_passed=link_sim_passed,
            fault_test_passed=fault_test_passed,
            fallback_test_passed=fallback_test_passed,
            bler=metrics["bler"],
            throughput_kbps=metrics["throughput_kbps"],
            latency_ms=metrics["latency_ms"],
            spectral_efficiency=metrics["spectral_efficiency"],
            energy_cost=metrics["energy_cost"],
            robustness_score=robustness_score,
            final_score=final_score,
            warnings=warnings,
            errors=errors,
            suggestions=suggestions,
        )

    def _generate_suggestions(self, metrics: dict, intent: IntentSpec):
        suggestions = []

        if metrics["bler"] > intent.target_bler:
            suggestions.append(
                "BLER is above target. Consider lowering modulation order, increasing "
                "coding redundancy, increasing HARQ retransmissions, or using higher pilot density."
            )

        if metrics["throughput_kbps"] < intent.min_throughput_kbps:
            suggestions.append(
                "Throughput is below target. Consider higher-order modulation, higher "
                "coding rate, lower pilot overhead, or throughput-first scheduling."
            )

        if metrics["latency_ms"] > intent.max_latency_ms:
            suggestions.append(
                "Latency exceeds target. Consider reducing HARQ retransmissions or "
                "switching to latency-first scheduling."
            )

        if metrics["energy_cost"] > 0.2:
            suggestions.append(
                "Energy cost is relatively high. Consider reducing TX power or enabling "
                "energy-saving power control."
            )

        if not suggestions:
            suggestions.append(
                "Plan satisfies the major intent constraints in the simplified digital twin."
            )

        return suggestions