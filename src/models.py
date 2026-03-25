from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from src.database import Base

# --- SQLAlchemy Models (Table Definitions) ---


class ClaimSQL(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, index=True)  # e.g., "C-1001"
    user_id = Column(String, index=True)
    policy_number = Column(String)
    claim_amount = Column(Float)
    diagnosis_code = Column(String)  # ICD-10
    diagnosis_desc = Column(String)
    treatment_date = Column(DateTime)
    submission_date = Column(DateTime, default=func.now())

    # Status
    status = Column(String, default="PENDING")  # PENDING, APPROVED, REJECTED, REVIEW

    # Scores from Agents
    score_agent_1 = Column(Boolean, nullable=True)  # Pass/Fail
    score_agent_2 = Column(Float, nullable=True)  # Graph Score
    score_agent_3 = Column(Float, nullable=True)  # Anomaly Score
    score_agent_4 = Column(Float, nullable=True)  # Final Risk Score

    # Explanation
    explanation_agent_5 = Column(String, nullable=True)


# --- Pydantic Models (API Data Transfer Objects) ---


class ClaimRequest(BaseModel):
    claim_id: str
    user_id: str
    policy_number: str
    claim_amount: float
    diagnosis_code: str
    diagnosis_desc: str
    hospital_name: str
    doctor_id: str
    treatment_date: str  # ISO format YYYY-MM-DD
    phone_number: str
    device_id: Optional[str] = None
    ip_address: Optional[str] = None


class AnalysisResult(BaseModel):
    claim_id: str
    final_score: float
    risk_level: str
    action: str
    explanation: str
