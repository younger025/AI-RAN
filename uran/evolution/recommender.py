class SimpleRecommender:
    def recommend(self, scenario_type: str, data_lake, strategy_memory, n: int = 3):
        history = data_lake.query_by_scenario(scenario_type)
        best_strategies = strategy_memory.get_best(scenario_type, n)

        recommendations = []
        for s in best_strategies:
            recommendations.append({
                "plan": s["plan"],
                "score": s["score"],
                "twin_score": s["twin_score"],
                "reason": f"Historical best strategy for {scenario_type} scenario.",
            })

        if not recommendations and history:
            latest = history[-1]
            recommendations.append({
                "plan": latest.get("plan", {}),
                "score": latest.get("twin_score", 0),
                "twin_score": latest.get("twin_score", 0),
                "reason": "Latest historical data (insufficient samples for strategy ranking).",
            })

        return recommendations