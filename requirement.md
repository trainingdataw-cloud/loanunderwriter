# Loan Underwriter System - Requirements Document

## Problem Statement

Financial institutions need an automated system to evaluate loan applications based on standardized underwriting criteria. Currently, loan approval decisions require manual review of multiple parameters (age, income, credit score, loan amount) which is time-consuming and inconsistent. The system must provide quick, rule-based loan eligibility decisions while capturing all rejection reasons for transparency and customer communication.

---

## Project Objectives

1. **Automate Loan Eligibility Assessment**: Evaluate loan applications against predefined underwriting rules in real-time
2. **Ensure Consistency**: Apply uniform, objective criteria to all applicants
3. **Provide Transparency**: Return detailed rejection reasons when applications fail
4. **Enable Fast Processing**: Deliver approval/rejection decisions via API within milliseconds
5. **Support Integration**: Provide RESTful API that can be integrated into customer-facing and internal systems

---

## Functional Requirements

### FR-1: Loan Application Submission
- **Description**: Accept loan application requests via HTTP POST endpoint
- **Input**: Single loan application with applicant details (name, age, annual income, requested loan amount, credit score)
- **Processing**: Validate all input fields are present and properly formatted
- **Output**: Validation errors if input is malformed or missing

### FR-2: Eligibility Rule Evaluation
- **Description**: Evaluate the application against all four underwriting rules
- **Processing**: 
  - Rule 1: Verify applicant age is within acceptable range
  - Rule 2: Verify annual income meets minimum threshold
  - Rule 3: Verify requested loan does not exceed income multiple
  - Rule 4: Verify credit score meets minimum requirement
- **Decision Logic**: Application is APPROVED only if ALL rules pass
- **Output**: Approval decision (true/false)

### FR-3: Rejection Reason Reporting
- **Description**: When application is rejected, provide all failed rule codes/identifiers
- **Processing**: Check all rules regardless of how many fail (don't short-circuit)
- **Output**: List of failed rule identifiers (e.g., ['age_invalid', 'income_insufficient'])
- **Edge Case**: If no rules fail, application is approved (no rejection reasons returned)

### FR-4: Successful Application Response
- **Description**: Return structured response for approved applications
- **Output**: 
  - Approval status: `true`
  - Approval message or confirmation
  - Applicant reference information

### FR-5: Failed Application Response
- **Description**: Return structured response for rejected applications
- **Output**:
  - Approval status: `false`
  - List of all failed rule codes
  - No additional analysis or contextual messages

---

## Non-Functional Requirements

### NFR-1: Performance
- API response time: < 100ms for loan decision (p99)
- Throughput: Support minimum 100 requests per second

### NFR-2: Reliability
- System uptime: 99% availability during business hours
- No data persistence required (stateless operation)

### NFR-3: Code Quality
- Type safety: Use Pydantic for request/response validation
- Framework: FastAPI for HTTP API implementation
- Language: Python 3.8+

### NFR-4: Maintainability
- Business rules should be easily modifiable without code changes
- Clear separation between validation logic and API layer
- Well-documented decision flow

### NFR-5: Security Considerations
- Input validation for all numeric fields (prevent injection, overflow)
- No sensitive data logging
- No authentication/authorization required for MVP

### NFR-6: API Standards
- RESTful API design principles
- Proper HTTP status codes (200 for success, 400 for bad request, 500 for errors)
- JSON request/response format
- Meaningful error messages for debugging

---

## Input Fields and Output Format

### Request Schema

**Endpoint**: `POST /api/loan/evaluate`

**Request Body** (JSON):
```json
{
  "applicant_name": "string (optional, for reference)",
  "age": "integer (years)",
  "annual_income": "number (currency units)",
  "requested_loan_amount": "number (currency units)",
  "credit_score": "integer (0-850 or similar scale)"
}
```

**Field Validation**:
- `age`: Required, integer, must be numeric
- `annual_income`: Required, numeric (integer or float), must be greater than 0
- `requested_loan_amount`: Required, numeric (integer or float), must be greater than 0 (cannot be zero or negative)
- `credit_score`: Required, integer, typically 0-850 range
- `applicant_name`: Optional, for reference/logging only

### Response Schema - Approved Application

**HTTP Status**: 200 OK

```json
{
  "approved": true,
  "message": "Application approved",
  "applicant_name": "string (echo from request or reference)",
  "decision_timestamp": "ISO8601 timestamp"
}
```

### Response Schema - Rejected Application

**HTTP Status**: 200 OK

```json
{
  "approved": false,
  "rejection_reasons": [
    "age_invalid",
    "income_insufficient",
    "loan_amount_exceeds_limit",
    "credit_score_insufficient"
  ]
}
```

**Possible Rejection Codes**:
- `age_invalid`: Applicant age outside 21-60 range
- `income_insufficient`: Annual income below 500,000
- `loan_amount_exceeds_limit`: Requested amount > 5 × annual income
- `credit_score_insufficient`: Credit score below 700
- `loan_amount_too_low`: Requested amount < 50,000

### Error Response

**HTTP Status**: 400 Bad Request (for validation errors)

```json
{
  "error": "Validation error",
  "details": [
    {
      "field": "age",
      "message": "age must be an integer"
    }
  ]
}
```

---

## Loan Approval Business Rules

### Rule 1: Applicant Age
- **Condition**: Applicant age must be between 21 years and 60 years (inclusive)
- **Validation**: 21 ≤ age ≤ 60
- **Rejection Code**: `age_invalid`
- **Rationale**: Age represents creditworthiness and employment stability windows

### Rule 2: Annual Income
- **Condition**: Annual income must be at least 500,000
- **Validation**: annual_income ≥ 500,000
- **Rejection Code**: `income_insufficient`
- **Rationale**: Minimum income threshold ensures debt servicing capability

### Rule 3: Loan Amount Limit
- **Condition**: Requested loan amount must not exceed 5 times annual income
- **Validation**: requested_loan_amount ≤ (annual_income × 5)
- **Rejection Code**: `loan_amount_exceeds_limit`
- **Rationale**: Debt-to-income ratio cap limits risk exposure

### Rule 4: Credit Score
- **Condition**: Credit score must be at least 700
- **Validation**: credit_score ≥ 700
- **Rejection Code**: `credit_score_insufficient`
- **Rationale**: Credit score indicates repayment history and creditworthiness

### Rule 5: Minimum Loan Amount
- **Condition**: Requested loan amount must be at least 50,000
- **Validation**: requested_loan_amount ≥ 50,000
- **Rejection Code**: `loan_amount_too_low`
- **Rationale**: Ensures meaningful loan amounts to avoid administrative overhead

### Approval Decision Logic
- **APPROVED**: If and only if ALL five rules pass
- **REJECTED**: If one or more rules fail
- **Return All Failures**: Always evaluate all rules; return all failure codes if rejection occurs

---

## Positive Scenarios (Expected to Pass)

### Scenario 1: Ideal Applicant
- **Input**: 
  - Age: 35 years
  - Annual Income: 1,000,000
  - Requested Loan: 2,000,000
  - Credit Score: 750
- **Expected Output**: `approved: true`
- **Rationale**: All rules satisfied comfortably

### Scenario 2: Minimum Age Threshold
- **Input**:
  - Age: 21 years
  - Annual Income: 600,000
  - Requested Loan: 2,000,000
  - Credit Score: 720
- **Expected Output**: `approved: true`
- **Rationale**: Age at lower boundary is acceptable

### Scenario 3: Maximum Age Threshold
- **Input**:
  - Age: 60 years
  - Annual Income: 750,000
  - Requested Loan: 2,500,000
  - Credit Score: 710
- **Expected Output**: `approved: true`
- **Rationale**: Age at upper boundary is acceptable

### Scenario 4: Minimum Income Threshold
- **Input**:
  - Age: 45 years
  - Annual Income: 500,000 (exactly minimum)
  - Requested Loan: 1,500,000
  - Credit Score: 750
- **Expected Output**: `approved: true`
- **Rationale**: Income at minimum threshold is acceptable

### Scenario 5: Maximum Loan-to-Income Ratio
- **Input**:
  - Age: 40 years
  - Annual Income: 1,000,000
  - Requested Loan: 5,000,000 (exactly 5× income)
  - Credit Score: 750
- **Expected Output**: `approved: true`
- **Rationale**: Loan at maximum allowed multiple is acceptable

### Scenario 6: Minimum Credit Score Threshold
- **Input**:
  - Age: 50 years
  - Annual Income: 700,000
  - Requested Loan: 1,500,000
  - Credit Score: 700 (exactly minimum)
- **Expected Output**: `approved: true`
- **Rationale**: Credit score at minimum threshold is acceptable

---

## Negative Scenarios (Expected to Fail)

### Scenario 1: Age Too Young
- **Input**:
  - Age: 20 years
  - Annual Income: 750,000
  - Requested Loan: 2,000,000
  - Credit Score: 750
- **Expected Output**: `approved: false, rejection_reasons: ['age_invalid']`
- **Rationale**: Age below 21 minimum

### Scenario 2: Age Too Old
- **Input**:
  - Age: 61 years
  - Annual Income: 800,000
  - Requested Loan: 2,500,000
  - Credit Score: 720
- **Expected Output**: `approved: false, rejection_reasons: ['age_invalid']`
- **Rationale**: Age exceeds 60 maximum

### Scenario 3: Income Insufficient
- **Input**:
  - Age: 35 years
  - Annual Income: 499,999
  - Requested Loan: 1,500,000
  - Credit Score: 750
- **Expected Output**: `approved: false, rejection_reasons: ['income_insufficient']`
- **Rationale**: Income below 500,000 minimum

### Scenario 4: Loan Amount Exceeds Limit
- **Input**:
  - Age: 45 years
  - Annual Income: 1,000,000
  - Requested Loan: 5,000,001 (exceeds 5×)
  - Credit Score: 750
- **Expected Output**: `approved: false, rejection_reasons: ['loan_amount_exceeds_limit']`
- **Rationale**: Loan exceeds 5× income limit

### Scenario 5: Credit Score Too Low
- **Input**:
  - Age: 40 years
  - Annual Income: 600,000
  - Requested Loan: 1,800,000
  - Credit Score: 699
- **Expected Output**: `approved: false, rejection_reasons: ['credit_score_insufficient']`
- **Rationale**: Credit score below 700 minimum

### Scenario 6: Multiple Failures - All Rules Fail
- **Input**:
  - Age: 18 years
  - Annual Income: 400,000
  - Requested Loan: 3,000,000
  - Credit Score: 600
- **Expected Output**: `approved: false, rejection_reasons: ['age_invalid', 'income_insufficient', 'loan_amount_exceeds_limit', 'credit_score_insufficient']`
- **Rationale**: All four rules fail; return all rejection codes

### Scenario 7: Multiple Failures - Three Rules Fail
- **Input**:
  - Age: 19 years
  - Annual Income: 450,000
  - Requested Loan: 3,000,000
  - Credit Score: 750
- **Expected Output**: `approved: false, rejection_reasons: ['age_invalid', 'income_insufficient', 'loan_amount_exceeds_limit']`
- **Rationale**: Three rules fail (age, income, loan amount); credit score passes

### Scenario 8: Edge Case - Very High Loan Request
- **Input**:
  - Age: 50 years
  - Annual Income: 600,000
  - Requested Loan: 10,000,000
  - Credit Score: 800
- **Expected Output**: `approved: false, rejection_reasons: ['loan_amount_exceeds_limit']`
- **Rationale**: Loan far exceeds 5× income limit, but all other rules pass

### Scenario 9: Validation Error - Zero Loan Amount
- **Input**:
  - Age: 35 years
  - Annual Income: 600,000
  - Requested Loan: 0
  - Credit Score: 750
- **Expected Output**: HTTP 422 Validation Error
- **Rationale**: Loan amount must be greater than 0 (input validation)

### Scenario 10: Validation Error - Negative Loan Amount
- **Input**:
  - Age: 35 years
  - Annual Income: 600,000
  - Requested Loan: -500,000
  - Credit Score: 750
- **Expected Output**: HTTP 422 Validation Error
- **Rationale**: Loan amount cannot be negative (input validation)

### Scenario 11: Business Rule - Loan Amount Too Low
- **Input**:
  - Age: 35 years
  - Annual Income: 600,000
  - Requested Loan: 49,999
  - Credit Score: 750
- **Expected Output**: `approved: false, rejection_reasons: ['loan_amount_too_low']`
- **Rationale**: Loan amount below 50,000 minimum

### Scenario 12: Business Rule - Loan Amount At Minimum
- **Input**:
  - Age: 35 years
  - Annual Income: 600,000
  - Requested Loan: 50,000
  - Credit Score: 750
- **Expected Output**: `approved: true`
- **Rationale**: Loan amount at minimum threshold is acceptable

---

## Acceptance Criteria

### API Functionality
- ✅ **AC-1**: API endpoint `/api/loan/evaluate` accepts POST requests with loan application JSON
- ✅ **AC-2**: For each request, all four business rules are evaluated
- ✅ **AC-3**: If all rules pass, response contains `approved: true`
- ✅ **AC-4**: If any rule fails, response contains `approved: false` and list of all failed rule codes
- ✅ **AC-5**: Rejection reasons list is in consistent order across multiple calls with same input
- ✅ **AC-6**: API returns HTTP 200 for both approved and rejected applications
- ✅ **AC-7**: API returns HTTP 400 for malformed/missing required fields

### Input Validation
- ✅ **AC-8**: API validates all required fields are present (age, annual_income, requested_loan_amount, credit_score)
- ✅ **AC-9**: API validates age is a valid integer
- ✅ **AC-10**: API validates annual_income is a valid positive number
- ✅ **AC-11**: API validates requested_loan_amount is a valid positive number
- ✅ **AC-12**: API validates credit_score is a valid integer
- ✅ **AC-13**: API returns meaningful error messages for validation failures

### Business Rule Implementation
- ✅ **AC-14**: Rule 1 (age 21-60): Approved if age within range, rejected with `age_invalid` if outside
- ✅ **AC-15**: Rule 2 (income ≥500k): Approved if income meets threshold, rejected with `income_insufficient` if below
- ✅ **AC-16**: Rule 3 (loan ≤ 5× income): Approved if within limit, rejected with `loan_amount_exceeds_limit` if exceeded
- ✅ **AC-17**: Rule 4 (credit score ≥700): Approved if score meets threshold, rejected with `credit_score_insufficient` if below
- ✅ **AC-18**: Decision logic: Application approved only if ALL rules pass
- ✅ **AC-19**: Multiple failures: All failed rule codes are returned in rejection response

### Response Format
- ✅ **AC-20**: Success response includes `approved: true` and optional confirmation message
- ✅ **AC-21**: Failure response includes `approved: false` and array of rejection reason codes
- ✅ **AC-22**: Responses use valid JSON format
- ✅ **AC-23**: Error responses include meaningful error descriptions

### Edge Cases & Boundary Testing
- ✅ **AC-24**: Boundary test: Age = 21 (minimum): Should pass age rule
- ✅ **AC-25**: Boundary test: Age = 60 (maximum): Should pass age rule
- ✅ **AC-26**: Boundary test: Annual income = 500,000 (minimum): Should pass income rule
- ✅ **AC-27**: Boundary test: Loan amount = 5× income: Should pass loan limit rule
- ✅ **AC-28**: Boundary test: Credit score = 700 (minimum): Should pass credit rule
- ✅ **AC-29**: Decimal values in numeric fields are handled correctly

### Code Quality
- ✅ **AC-30**: Type hints used throughout (Pydantic models for request/response)
- ✅ **AC-31**: Business logic is separate from API routing logic
- ✅ **AC-32**: Code follows PEP-8 style guidelines
- ✅ **AC-33**: All public functions/endpoints have docstrings

### Performance
- ✅ **AC-34**: API response time < 100ms per request (in normal conditions)
- ✅ **AC-35**: No unnecessary computations or loops in decision logic

---

## Assumptions & Constraints

### Assumptions
1. **Numeric Precision**: Annual income, loan amounts, and age are assumed to be positive values
2. **Credit Score Scale**: Credit score is expected to be a standard scale (0-850), but no strict range validation is applied
3. **No State Management**: Each request is independent; no session or state tracking required
4. **No Persistence**: No database or storage layer required; all processing is stateless
5. **No Authentication**: Public endpoint; no user authentication or authorization required
6. **Business Rules are Fixed**: Thresholds (21, 60, 500000, 5, 700) are fixed at deployment time
7. **Single Application Processing**: API processes one application per request

### Constraints
- No database required
- No authentication/authorization required
- No logging/audit trail required
- Stateless operation only
- Synchronous processing only (no async/queuing)

---

## Future Enhancements (Out of Scope)

1. Batch loan processing endpoint
2. Loan amount recommendation based on income
3. Detailed decision explanations (contextual messages)
4. Audit logging and traceability
5. Configuration management (dynamic rule thresholds)
6. Integration with credit bureaus or income verification services
7. Machine learning scoring models
8. Loan approval probability percentages
