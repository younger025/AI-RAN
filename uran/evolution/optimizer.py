class HeuristicOptimizer:
    def recommend(self, intent, plan, runtime_kpis):
        changes = {}
        reasons = []

        bler = runtime_kpis.get("avg_bler", runtime_kpis.get("bler", 0))
        throughput = runtime_kpis.get("avg_throughput_kbps", runtime_kpis.get("throughput_kbps", 0))
        latency = runtime_kpis.get("avg_latency_ms", runtime_kpis.get("latency_ms", 0))

        target_bler = getattr(intent, "target_bler", 0.08)
        min_throughput = getattr(intent, "min_throughput_kbps", 200)
        max_latency = getattr(intent, "max_latency_ms", 100)

        if bler > target_bler:
            reasons.append(f"Observed BLER {bler:.3f} exceeds target {target_bler:.3f}")
            changes["increase_reliability"] = [
                "降低调制阶数",
                "降低 MCS",
                "增加 HARQ 重传次数",
                "提高导频密度",
                "适度提高发射功率",
            ]

        if throughput < min_throughput:
            reasons.append(f"Observed throughput {throughput:.1f} kbps below target {min_throughput:.1f} kbps")
            changes["increase_throughput"] = [
                "提高调制阶数",
                "提高编码率",
                "降低导频开销",
                "减少 HARQ 开销",
            ]

        if latency > max_latency:
            reasons.append(f"Observed latency {latency:.1f} ms exceeds target {max_latency:.1f} ms")
            changes["reduce_latency"] = [
                "减少 HARQ 次数",
                "切换 latency_first scheduler",
                "选择低复杂度编码",
            ]

        if not reasons:
            reasons.append("Current plan satisfies major intent constraints.")
            changes["fine_tuning"] = [
                "保持当前策略",
                "尝试小幅提高 MCS 以提升吞吐",
                "继续收集更多样本",
            ]

        return {
            "reasons": reasons,
            "changes": changes,
            "expected_improvement": "基于启发式规则，预计下一轮可改善主要瓶颈指标。",
        }