from pydantic import BaseModel, Field


class LoanApplication(BaseModel):
    """Loan application request"""
    applicant_name: str | None = None
    age: int
    annual_income: float = Field(..., gt=0)
    requested_loan_amount: float = Field(..., gt=0)
    credit_score: int


class LoanEvaluationResponse(BaseModel):
    """Loan evaluation response"""
    approved: bool
    message: str | None = None
    rejection_reasons: list[str] = []
    applicant_name: str | None = None
    decision_timestamp: str
