from datetime import datetime
from sqlalchemy.orm import Session
from src.models import ClaimSQL
from src.database import get_db


class Agent01Gatekeeper:
    def __init__(self):
        self.name = "The Gatekeeper"

    def check_rules(self, claim_data: dict, db: Session) -> dict:
        """
        Applies rigid IF-THEN rules.
        Returns: {"passed": bool, "reason": str}
        """
        # 1. Completeness Check
        required_fields = [
            "user_id",
            "claim_amount",
            "diagnosis_code",
            "treatment_date",
        ]
        for field in required_fields:
            if not claim_data.get(field):
                return {"passed": False, "reason": f"Missing mandatory field: {field}"}

        # 2. Temporal Logic
        # Parse dates. Note: In a real app, ensure format is ISO 8601
        try:
            treatment_date = datetime.fromisoformat(claim_data["treatment_date"])
            submission_date = datetime.now()

            if treatment_date > submission_date:
                return {"passed": False, "reason": "Treatment date is in the future."}
        except ValueError:
            return {"passed": False, "reason": "Invalid date format."}

        # 3. Policy & Financial Check (Mocked Logic)
        # In reality, we'd query a 'Policies' table here.
        # Rule: Max claim amount for 'Silver' policy is 50M.
        if claim_data["claim_amount"] < 0:
            return {"passed": False, "reason": "Negative claim amount."}

        if claim_data["claim_amount"] > 100_000_000:  # 100M VND
            return {"passed": False, "reason": "Claim exceeds global policy limit."}

        return {"passed": True, "reason": "All hygiene checks passed."}


agent_01 = Agent01Gatekeeper()
