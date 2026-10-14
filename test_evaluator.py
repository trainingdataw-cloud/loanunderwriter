import pytest
from evaluator import evaluate_loan


class TestPositiveScenarios:
    """Test cases where applications should be approved"""

    def test_approve_ideal_applicant(self):
        """Ideal applicant - all rules pass comfortably"""
        result = evaluate_loan(
            age=35,
            annual_income=1_000_000,
            requested_loan_amount=2_000_000,
            credit_score=750,
        )
        assert result["approved"] is True
        assert result["rejection_reasons"] == []

    def test_approve_min_age(self):
        """Age at minimum boundary (21)"""
        result = evaluate_loan(
            age=21,
            annual_income=600_000,
            requested_loan_amount=2_000_000,
            credit_score=720,
        )
        assert result["approved"] is True
        assert result["rejection_reasons"] == []

    def test_approve_max_age(self):
        """Age at maximum boundary (60)"""
        result = evaluate_loan(
            age=60,
            annual_income=750_000,
            requested_loan_amount=2_500_000,
            credit_score=710,
        )
        assert result["approved"] is True
        assert result["rejection_reasons"] == []

    def test_approve_min_income(self):
        """Income at minimum boundary (500,000)"""
        result = evaluate_loan(
            age=45,
            annual_income=500_000,
            requested_loan_amount=1_500_000,
            credit_score=750,
        )
        assert result["approved"] is True
        assert result["rejection_reasons"] == []

    def test_approve_max_loan_ratio(self):
        """Loan amount at maximum ratio (5× income)"""
        result = evaluate_loan(
            age=40,
            annual_income=1_000_000,
            requested_loan_amount=5_000_000,
            credit_score=750,
        )
        assert result["approved"] is True
        assert result["rejection_reasons"] == []

    def test_approve_min_credit_score(self):
        """Credit score at minimum boundary (700)"""
        result = evaluate_loan(
            age=50,
            annual_income=700_000,
            requested_loan_amount=1_500_000,
            credit_score=700,
        )
        assert result["approved"] is True
        assert result["rejection_reasons"] == []

    def test_approve_min_loan_amount(self):
        """Loan amount at minimum boundary (50,000)"""
        result = evaluate_loan(
            age=35,
            annual_income=500_000,
            requested_loan_amount=50_000,
            credit_score=750,
        )
        assert result["approved"] is True
        assert result["rejection_reasons"] == []


class TestNegativeSingleFailures:
    """Test cases with single rule failures"""

    def test_reject_age_too_young(self):
        """Age below 21 minimum"""
        result = evaluate_loan(
            age=20,
            annual_income=750_000,
            requested_loan_amount=2_000_000,
            credit_score=750,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["age_invalid"]

    def test_reject_age_too_old(self):
        """Age exceeds 60 maximum"""
        result = evaluate_loan(
            age=61,
            annual_income=800_000,
            requested_loan_amount=2_500_000,
            credit_score=720,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["age_invalid"]

    def test_reject_income_insufficient(self):
        """Income below 500,000 minimum"""
        result = evaluate_loan(
            age=35,
            annual_income=499_999,
            requested_loan_amount=1_500_000,
            credit_score=750,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["income_insufficient"]

    def test_reject_loan_exceeds_limit(self):
        """Loan amount exceeds 5× income limit"""
        result = evaluate_loan(
            age=45,
            annual_income=1_000_000,
            requested_loan_amount=5_000_001,
            credit_score=750,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["loan_amount_exceeds_limit"]

    def test_reject_credit_score_low(self):
        """Credit score below 700 minimum"""
        result = evaluate_loan(
            age=40,
            annual_income=600_000,
            requested_loan_amount=1_800_000,
            credit_score=699,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["credit_score_insufficient"]

    def test_reject_loan_too_low(self):
        """Loan amount below 50,000 minimum"""
        result = evaluate_loan(
            age=35,
            annual_income=500_000,
            requested_loan_amount=49_999,
            credit_score=750,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["loan_amount_too_low"]


class TestNegativeMultipleFailures:
    """Test cases with multiple rule failures"""

    def test_reject_all_four_rules(self):
        """All four rules fail"""
        result = evaluate_loan(
            age=18,
            annual_income=400_000,
            requested_loan_amount=3_000_000,
            credit_score=600,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == [
            "age_invalid",
            "income_insufficient",
            "loan_amount_exceeds_limit",
            "credit_score_insufficient",
        ]

    def test_reject_three_rules(self):
        """Three rules fail (age, income, loan); credit score passes"""
        result = evaluate_loan(
            age=19,
            annual_income=450_000,
            requested_loan_amount=3_000_000,
            credit_score=750,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == [
            "age_invalid",
            "income_insufficient",
            "loan_amount_exceeds_limit",
        ]

    def test_reject_age_and_income(self):
        """Age and income rules fail"""
        result = evaluate_loan(
            age=20,
            annual_income=400_000,
            requested_loan_amount=1_500_000,
            credit_score=750,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["age_invalid", "income_insufficient"]

    def test_reject_income_and_credit(self):
        """Income and credit score rules fail"""
        result = evaluate_loan(
            age=35,
            annual_income=400_000,
            requested_loan_amount=1_500_000,
            credit_score=650,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == [
            "income_insufficient",
            "credit_score_insufficient",
        ]

    def test_reject_very_high_loan_request(self):
        """Loan far exceeds 5× income limit, other rules pass"""
        result = evaluate_loan(
            age=50,
            annual_income=600_000,
            requested_loan_amount=10_000_000,
            credit_score=800,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["loan_amount_exceeds_limit"]

    def test_reject_age_and_loan_too_low(self):
        """Age and loan amount both fail"""
        result = evaluate_loan(
            age=19,
            annual_income=600_000,
            requested_loan_amount=25_000,
            credit_score=750,
        )
        assert result["approved"] is False
        assert result["rejection_reasons"] == ["age_invalid", "loan_amount_too_low"]
