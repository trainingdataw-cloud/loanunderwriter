def evaluate_loan(
    age: int,
    annual_income: float,
    requested_loan_amount: float,
    credit_score: int,
) -> dict:
    """
    Evaluate loan eligibility against all 4 rules.
    Always checks all rules (no short-circuit).

    Args:
        age: Applicant age in years
        annual_income: Annual income in currency units
        requested_loan_amount: Requested loan amount in currency units
        credit_score: Credit score (typically 0-850)

    Returns:
        dict with keys:
            - approved: bool (True if all rules pass)
            - rejection_reasons: list[str] (empty if approved)
    """
    rejection_reasons = []

    # Rule 1: Age (21-60 inclusive) - Applicant must be within working age range
    if not (21 <= age <= 60):
        rejection_reasons.append("age_invalid")

    # Rule 2: Income >= 500,000
    if annual_income < 500_000:
        rejection_reasons.append("income_insufficient")

    # Rule 3: Loan <= 5× income
    if requested_loan_amount > (annual_income * 5):
        rejection_reasons.append("loan_amount_exceeds_limit")

    # Rule 4: Credit score >= 700
    if credit_score < 700:
        rejection_reasons.append("credit_score_insufficient")

    # Rule 5: Loan amount >= 50,000
    if requested_loan_amount < 50_000:
        rejection_reasons.append("loan_amount_too_low")

    return {
        "approved": len(rejection_reasons) == 0,
        "rejection_reasons": rejection_reasons,
    }
