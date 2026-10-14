import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test the /health endpoint"""

    def test_health_check_returns_ok(self):
        """Health check should return 200 with status ok"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestLoanEvaluationApproved:
    """Test loan evaluation endpoint with approved applications"""

    def test_approve_ideal_applicant(self):
        """Ideal applicant should be approved"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 1_000_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is True
        assert data["message"] == "Application approved"
        assert data["rejection_reasons"] == []
        assert "decision_timestamp" in data

    def test_approve_with_applicant_name(self):
        """Approved response should include applicant name"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "applicant_name": "John Doe",
                "age": 35,
                "annual_income": 1_000_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is True
        assert data["applicant_name"] == "John Doe"

    def test_approve_min_age(self):
        """Minimum age boundary should be approved"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 21,
                "annual_income": 600_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 720,
            },
        )
        assert response.status_code == 200
        assert response.json()["approved"] is True

    def test_approve_max_age(self):
        """Maximum age boundary should be approved"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 60,
                "annual_income": 750_000,
                "requested_loan_amount": 2_500_000,
                "credit_score": 710,
            },
        )
        assert response.status_code == 200
        assert response.json()["approved"] is True

    def test_approve_min_loan_amount(self):
        """Minimum loan amount boundary (50,000) should be approved"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 500_000,
                "requested_loan_amount": 50_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 200
        assert response.json()["approved"] is True


class TestLoanEvaluationRejected:
    """Test loan evaluation endpoint with rejected applications"""

    def test_reject_age_too_young(self):
        """Age below 21 should be rejected"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 20,
                "annual_income": 750_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is False
        assert "age_invalid" in data["rejection_reasons"]
        assert data["message"] is None

    def test_reject_income_insufficient(self):
        """Income below 500,000 should be rejected"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 400_000,
                "requested_loan_amount": 1_500_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is False
        assert "income_insufficient" in data["rejection_reasons"]

    def test_reject_loan_exceeds_limit(self):
        """Loan exceeding 5× income should be rejected"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 45,
                "annual_income": 1_000_000,
                "requested_loan_amount": 5_000_001,
                "credit_score": 750,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is False
        assert "loan_amount_exceeds_limit" in data["rejection_reasons"]

    def test_reject_credit_score_low(self):
        """Credit score below 700 should be rejected"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 40,
                "annual_income": 600_000,
                "requested_loan_amount": 1_800_000,
                "credit_score": 699,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is False
        assert "credit_score_insufficient" in data["rejection_reasons"]

    def test_reject_loan_too_low(self):
        """Loan amount below 50,000 should be rejected"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 500_000,
                "requested_loan_amount": 49_999,
                "credit_score": 750,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is False
        assert "loan_amount_too_low" in data["rejection_reasons"]

    def test_reject_all_four_rules(self):
        """All four rules failing should return all rejection reasons"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 18,
                "annual_income": 400_000,
                "requested_loan_amount": 3_000_000,
                "credit_score": 600,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is False
        assert len(data["rejection_reasons"]) == 4
        assert "age_invalid" in data["rejection_reasons"]
        assert "income_insufficient" in data["rejection_reasons"]
        assert "loan_amount_exceeds_limit" in data["rejection_reasons"]
        assert "credit_score_insufficient" in data["rejection_reasons"]


class TestValidationErrors:
    """Test input validation and error handling"""

    def test_missing_age_field(self):
        """Missing age field should return 400"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "annual_income": 600_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_missing_income_field(self):
        """Missing income field should return 400/422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_missing_loan_field(self):
        """Missing loan field should return 400/422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 600_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_missing_credit_score_field(self):
        """Missing credit score field should return 400/422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 600_000,
                "requested_loan_amount": 2_000_000,
            },
        )
        assert response.status_code == 422

    def test_invalid_age_type_string(self):
        """Age as string should return 422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": "thirty-five",
                "annual_income": 600_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_invalid_income_type_string(self):
        """Income as string should return 422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": "six-hundred",
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_negative_income(self):
        """Negative income should return 422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": -100_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_negative_loan(self):
        """Negative loan amount should return 422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 600_000,
                "requested_loan_amount": -500_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_zero_income(self):
        """Zero income should return 422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 0,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_zero_loan_amount(self):
        """Zero loan amount should return 422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 600_000,
                "requested_loan_amount": 0,
                "credit_score": 750,
            },
        )
        assert response.status_code == 422

    def test_empty_request(self):
        """Empty request body should return 422"""
        response = client.post("/api/loan/evaluate", json={})
        assert response.status_code == 422

    def test_very_small_positive_loan_amount(self):
        """Very small positive loan amount should be rejected (below 50k minimum)"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 600_000,
                "requested_loan_amount": 0.01,
                "credit_score": 750,
            },
        )
        assert response.status_code == 200
        assert response.json()["approved"] is False
        assert "loan_amount_too_low" in response.json()["rejection_reasons"]

    def test_invalid_credit_score_type(self):
        """Credit score as string should return 422"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 600_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": "seven-hundred",
            },
        )
        assert response.status_code == 422


class TestResponseStructure:
    """Test response structure and format"""

    def test_approved_response_structure(self):
        """Approved response should have all expected fields"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 1_000_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        data = response.json()
        assert "approved" in data
        assert "message" in data
        assert "rejection_reasons" in data
        assert "applicant_name" in data
        assert "decision_timestamp" in data

    def test_rejected_response_structure(self):
        """Rejected response should have all expected fields"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 20,
                "annual_income": 600_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        data = response.json()
        assert "approved" in data
        assert "rejection_reasons" in data
        assert isinstance(data["rejection_reasons"], list)
        assert len(data["rejection_reasons"]) > 0

    def test_timestamp_format(self):
        """Timestamp should be ISO8601 format"""
        response = client.post(
            "/api/loan/evaluate",
            json={
                "age": 35,
                "annual_income": 1_000_000,
                "requested_loan_amount": 2_000_000,
                "credit_score": 750,
            },
        )
        data = response.json()
        timestamp = data["decision_timestamp"]
        assert "T" in timestamp or timestamp.endswith("Z")

    def test_rejection_reasons_consistency(self):
        """Same input should produce same rejection reasons order"""
        request_data = {
            "age": 18,
            "annual_income": 400_000,
            "requested_loan_amount": 3_000_000,
            "credit_score": 600,
        }
        response1 = client.post("/api/loan/evaluate", json=request_data)
        response2 = client.post("/api/loan/evaluate", json=request_data)

        assert response1.json()["rejection_reasons"] == response2.json()[
            "rejection_reasons"
        ]
