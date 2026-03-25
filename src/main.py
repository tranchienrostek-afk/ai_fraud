from fastapi import FastAPI, Depends, HTTPException
from src.models import ClaimRequest, AnalysisResult, ClaimSQL
from src.orchestrator import process_claim_orchestrator
from src.database import engine, Base, get_db
from sqlalchemy.orm import Session
import uuid

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Layered Fraud Detection System")


@app.post("/api/claim", response_model=AnalysisResult)
async def submit_claim(claim: ClaimRequest, db: Session = Depends(get_db)):
    try:
        # Convert Pydantic to Dict
        claim_data = claim.dict()

        # Run Orchestrator
        result = await process_claim_orchestrator(claim_data, db)

        # Save Result to DB
        db_claim = ClaimSQL(
            id=claim.claim_id,
            user_id=claim.user_id,
            policy_number=claim.policy_number,
            claim_amount=claim.claim_amount,
            diagnosis_code=claim.diagnosis_code,
            diagnosis_desc=claim.diagnosis_desc,
            status=result.risk_level,
            score_agent_4=result.final_score,
            explanation_agent_5=result.explanation,
        )
        db.add(db_claim)
        db.commit()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "ok"}
