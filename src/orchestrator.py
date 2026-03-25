import asyncio
from src.agents.agent_01_gatekeeper import agent_01
from src.agents.agent_02_graph import agent_02
from src.agents.agent_03_anomaly import agent_03
from src.agents.agent_04_scoring import agent_04
from src.agents.agent_05_explanation import agent_05
from src.models import AnalysisResult


async def process_claim_orchestrator(
    claim_data: dict, db_session=None
) -> AnalysisResult:
    """
    The implementation of the 'Multi-Layered Sieve' workflow.
    """

    # --- Layer 1: Hygiene Check (Sequential) ---
    hygiene_res = agent_01.check_rules(claim_data, db_session)
    if not hygiene_res["passed"]:
        return AnalysisResult(
            claim_id=claim_data["claim_id"],
            final_score=0,
            risk_level="REJECTED_AUTO",
            action="Reject",
            explanation=hygiene_res["reason"],
        )

    # --- Layer 2 & 3: Deep Analysis (Parallel) ---
    # In a real async environment, we'd use asyncio.gather here.
    # For simplicity and thread safety with DB connections, we call them sequentially or use ThreadPoolExecutor.
    # But since these are CPU bound or I/O bound to different DBs, let's keep it simple for now.

    graph_res = agent_02.analyze(claim_data)
    anomaly_res = agent_03.analyze(claim_data)

    # --- Layer 4: Scoring (Sequential) ---
    scoring_res = agent_04.calculate_score(graph_res, anomaly_res, hygiene_res)

    final_score = scoring_res["final_score"]
    risk_level = scoring_res["risk_level"]
    action = "Approve" if final_score < 20 else "Investigate"

    explanation = ""
    # --- Layer 5: Explanation (Conditional) ---
    if final_score > 20:  # Only explain if there is risk
        explanation = agent_05.generate_explanation(claim_data, scoring_res)
    else:
        explanation = "Claim passed all checks. Low risk."

    return AnalysisResult(
        claim_id=claim_data["claim_id"],
        final_score=final_score,
        risk_level=risk_level,
        action=action,
        explanation=explanation,
    )
