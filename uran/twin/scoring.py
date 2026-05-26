from uran.ai.intent_schema import IntentSpec

WEIGHTS_BY_PRIORITY = {
    "reliability": {
        "reliability": 0.40, "throughput": 0.15, "latency": 0.15,
        "energy": 0.10, "robustness": 0.20,
    },
    "throughput": {
        "reliability": 0.15, "throughput": 0.45, "latency": 0.15,
        "energy": 0.10, "robustness": 0.15,
    },
    "latency": {
        "reliability": 0.20, "throughput": 0.15, "latency": 0.40,
        "energy": 0.10, "robustness": 0.15,
    },
    "energy": {
        "reliability": 0.20, "throughput": 0.15, "latency": 0.10,
        "energy": 0.40, "robustness": 0.15,
    },
    "balanced": {
        "reliability": 0.25, "throughput": 0.25, "latency": 0.20,
        "energy": 0.10, "robustness": 0.20,
    },
    "anti_jamming": {
        "reliability": 0.30, "throughput": 0.15, "latency": 0.15,
        "energy": 0.05, "robustness": 0.35,
    },
}


class TwinScorer:
    def score(self, metrics: dict, intent: IntentSpec, fault_metrics=None):
        reliability_score = self._reliability_score(metrics, intent)
        throughput_score = self._throughput_score(metrics, intent)
        latency_score = self._latency_score(metrics, intent)
        energy_score = self._energy_score(metrics)
        robustness_score = self._robustness_score(metrics, fault_metrics)

        weights = WEIGHTS_BY_PRIORITY.get(intent.priority, WEIGHTS_BY_PRIORITY["balanced"])

        final_score = (
            reliability_score * weights["reliability"]
            + throughput_score * weights["throughput"]
            + latency_score * weights["latency"]
            + energy_score * weights["energy"]
            + robustness_score * weights["robustness"]
        )

        return {
            "reliability_score": reliability_score,
            "throughput_score": throughput_score,
            "latency_score": latency_score,
            "energy_score": energy_score,
            "robustness_score": robustness_score,
            "final_score": final_score,
        }

    def _reliability_score(self, metrics: dict, intent: IntentSpec) -> float:
        bler = metrics.get("bler", 0)
        target = max(intent.target_bler, 0.001)
        if bler <= target:
            return 100.0
        return max(0, 100 * target / bler)

    def _throughput_score(self, metrics: dict, intent: IntentSpec) -> float:
        throughput = metrics.get("throughput_kbps", 0)
        target = max(intent.min_throughput_kbps, 1)
        if throughput >= target:
            return 100.0
        return max(0, 100 * throughput / target)

    def _latency_score(self, metrics: dict, intent: IntentSpec) -> float:
        latency = metrics.get("latency_ms", 0)
        target = max(intent.max_latency_ms, 1)
        if latency <= target:
            return 100.0
        return max(0, 100 * target / latency)

    def _energy_score(self, metrics: dict) -> float:
        energy = metrics.get("energy_cost", 0.1)
        return max(0, min(100, 100 - energy * 10))

    def _robustness_score(self, base_metrics: dict, fault_metrics=None) -> float:
        if not fault_metrics:
            return 100.0

        fault_bler_avg = sum(x["bler"] for x in fault_metrics) / len(fault_metrics)
        base_thr = max(base_metrics.get("throughput_kbps", 1), 1e-6)
        fault_thr_avg = sum(x["throughput_kbps"] for x in fault_metrics) / len(fault_metrics)
        throughput_ratio = fault_thr_avg / base_thr

        bler_part = max(0, 100 * (1 - fault_bler_avg))
        thr_part = max(0, min(100, 100 * throughput_ratio))

        return 0.6 * bler_part + 0.4 * thr_part