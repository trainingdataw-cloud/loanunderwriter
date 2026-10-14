from datetime import datetime, timezone
from fastapi import FastAPI
from models import LoanApplication, LoanEvaluationResponse
from evaluator import evaluate_loan

app = FastAPI(title="Loan Underwriter API")


@app.get("/health")
def health_check() -> dict:
    """Simple health check endpoint"""
    return {"status": "ok"}


@app.post("/api/loan/evaluate")
def submit_loan_application(
    application: LoanApplication,
) -> LoanEvaluationResponse:
    """
    Evaluate loan application against underwriting rules.

    Returns:
        - approved: true if ALL rules pass
        - rejection_reasons: list of failed rule codes if ANY rule fails
    """
    result = evaluate_loan(
        age=application.age,
        annual_income=application.annual_income,
        requested_loan_amount=application.requested_loan_amount,
        credit_score=application.credit_score,
    )

    return LoanEvaluationResponse(
        approved=result["approved"],
        message="Application approved" if result["approved"] else None,
        rejection_reasons=result["rejection_reasons"],
        applicant_name=application.applicant_name,
        decision_timestamp=datetime.now(timezone.utc).isoformat(),
    )
