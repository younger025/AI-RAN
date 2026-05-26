class StrategyMemory:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        self._memory = {}

    def update(self, experience):
        scenario = experience.get("intent", {}).get("scenario_type", "unknown")
        if scenario not in self._memory:
            self._memory[scenario] = []

        score = (
            experience.get("twin_score", 0) * 0.4
            + (1 if experience.get("success", False) else 0) * 30
            + min(experience.get("runtime_kpis", {}).get("avg_throughput_kbps", 0) / 1000, 10)
            + (1 - min(experience.get("runtime_kpis", {}).get("avg_bler", 1), 1)) * 10
            + max(0, (100 - experience.get("runtime_kpis", {}).get("avg_latency_ms", 100)) / 10)
        )

        self._memory[scenario].append({
            "plan": experience.get("plan"),
            "score": score,
            "twin_score": experience.get("twin_score", 0),
        })

        self._memory[scenario].sort(key=lambda x: x["score"], reverse=True)
        self._memory[scenario] = self._memory[scenario][:self.top_k]

    def get_best(self, scenario_type: str, top_k: int = None):
        k = top_k or self.top_k
        if scenario_type not in self._memory:
            return []
        return self._memory[scenario_type][:k]