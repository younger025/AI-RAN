class SafetyGuard:
    def __init__(self, max_bler=0.5, bad_steps=5):
        self.max_bler = max_bler
        self.bad_steps = bad_steps

    def should_fallback(self, state, modules, monitor):
        for m in modules:
            if not m.health_check():
                return True, f"Module health check failed: {m.module_id}"

        threshold = max(1, int(self.bad_steps * 0.6))
        if monitor.recent_bad_bler_count(self.max_bler, self.bad_steps) >= threshold:
            return True, f"Consecutive high BLER detected ({threshold}/{self.bad_steps} recent steps above {self.max_bler})"

        return False, None