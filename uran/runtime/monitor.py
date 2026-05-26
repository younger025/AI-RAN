class RuntimeMonitor:
    def __init__(self):
        self.history = []

    def append(self, kpi):
        self.history.append(kpi)

    def recent_bad_bler_count(self, threshold=0.5, window=5):
        recent = self.history[-window:]
        return sum(1 for x in recent if x.get("bler", 0) > threshold)

    def summary(self):
        if not self.history:
            return {
                "avg_bler": 0,
                "avg_throughput_kbps": 0,
                "avg_latency_ms": 0,
                "steps": 0,
            }

        n = len(self.history)
        return {
            "avg_bler": sum(h.get("bler", 0) for h in self.history) / n,
            "avg_throughput_kbps": sum(h.get("throughput_kbps", 0) for h in self.history) / n,
            "avg_latency_ms": sum(h.get("latency_ms", 0) for h in self.history) / n,
            "steps": n,
        }