class Agent04Scoring:
    def __init__(self):
        self.name = "The Actuary"

    def calculate_score(
        self, graph_res: dict, anomaly_res: dict, rule_res: dict
    ) -> dict:
        """
        Aggregates scores from previous agents.
        """
        # Feature Weights (Simple Linear Model for Demo)
        w_graph = 0.5
        w_anomaly = 0.3
        w_base = 0.2

        graph_score = graph_res.get("score", 0)
        anomaly_score = anomaly_res.get("score", 0)

        # Base score from Rule Agent (if it flagged something but didn't reject)
        base_score = 0
        if not rule_res["passed"]:
            base_score = 100  # Should have been rejected already, but safe guard.

        final_score = (
            (graph_score * w_graph)
            + (anomaly_score * w_anomaly)
            + (base_score * w_base)
        )
        final_score = min(final_score, 100)

        # Risk Classification
        if final_score < 20:
            level = "LOW"
        elif final_score < 60:
            level = "MEDIUM"
        elif final_score < 85:
            level = "HIGH"
        else:
            level = "CRITICAL"

        return {
            "final_score": round(final_score, 2),
            "risk_level": level,
            "details": {
                "graph_contrib": graph_score * w_graph,
                "anomaly_contrib": anomaly_score * w_anomaly,
            },
        }


agent_04 = Agent04Scoring()
