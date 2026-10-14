# Loan Underwriter System - Project Guide

## Project Purpose

A RESTful API that automatically evaluates loan applications against underwriting rules and returns approval/rejection decisions within milliseconds. The system takes applicant information (age, income, loan amount, credit score) and checks it against 4 business rules to determine eligibility.

**Why this matters**: Manual loan review is slow and inconsistent. This API makes decisions automatically using the same rules for every applicant.

---

## Technology Stack

- **Language**: Python 3.8+
- **Web Framework**: FastAPI (lightweight, fast HTTP API framework)
- **Data Validation**: Pydantic (ensures request/response data is correct type and format)
- **Testing**: pytest (test framework) and httpx (for testing HTTP requests)

**No databases, no authentication, no extra frameworks** — just pure business logic wrapped in a web API.

---


## Folder Structure

```
loanunderwriter/
├── CLAUDE.md                    # This file - project guidance
├── requirement.md               # Full business requirements
├── main.py                      # FastAPI application entry point
├── models.py                    # Pydantic models for request/response validation
├── evaluator.py                 # Core loan evaluation logic (business rules)
├── test_evaluator.py            # Unit tests for business logic
├── test_api.py                  # Integration tests for API endpoints
├── .gitignore                   # Git ignore file
├── requirements.txt             # Python dependencies (pip packages)
└── README.md                    # Quick start guide for running the app
```

**Key Principle**: Keep it simple. Each file has one clear job:
- `models.py` = data validation (what we accept/return)
- `evaluator.py` = business logic (the 4 rules)
- `main.py` = API endpoints (how to call the logic via HTTP)
- `test_*` = verify everything works correctly

---

## Business Rules & Constraints

### The 4 Loan Approval Rules

An application is **APPROVED** only if **ALL** 4 rules pass. If any rule fails, the app is **REJECTED** and we return which rules failed.

1. **Age Rule**: Applicant must be 21-60 years old (inclusive)
   - Rejection code: `age_invalid`

2. **Income Rule**: Annual income must be at least 500,000
   - Rejection code: `income_insufficient`

3. **Loan Amount Rule**: Requested loan cannot exceed 5× annual income
   - Rejection code: `loan_amount_exceeds_limit`
   - Example: If income is 1,000,000, max loan is 5,000,000

4. **Credit Score Rule**: Credit score must be at least 700
   - Rejection code: `credit_score_insufficient`

### Critical Constraint: Check ALL Rules

Even if the first rule fails, we still check all 4 rules and return every failure. **Never stop checking early** (no short-circuit logic).

**Example**: Age 18, Income 400,000, Loan 3,000,000, Credit Score 600
- Returns: `['age_invalid', 'income_insufficient', 'loan_amount_exceeds_limit', 'credit_score_insufficient']` (all 4 fail)

### Other Constraints

- **No database**: Everything is stateless. Each request is independent.
- **No persistence**: Don't save applications or decisions.
- **No authentication**: Public endpoint, no login needed.
- **Synchronous only**: Process requests immediately, don't queue them.
- **Single application per request**: One loan app per API call.

---

## Coding Conventions

### 1. Type Hints - Always Use Them

Type hints tell Python (and future readers) what type of data a function expects and returns.

```python
# Good ✓
def check_age(age: int) -> bool:
    return 21 <= age <= 60

# Bad ✗
def check_age(age):
    return 21 <= age <= 60
```

### 2. Pydantic Models for Data Validation

Use Pydantic to define what data is valid. It automatically validates and converts types.

```python
from pydantic import BaseModel, Field

class LoanApplication(BaseModel):
    age: int
    annual_income: float = Field(..., gt=0)  # Must be greater than 0
    requested_loan_amount: float = Field(..., gt=0)
    credit_score: int
    applicant_name: str | None = None  # Optional field
```

Pydantic automatically:
- Checks types (rejects `"abc"` for an int field)
- Validates ranges (if you define them)
- Returns helpful error messages if data is invalid

### 3. Separate Business Logic from API

**Business logic** (`evaluator.py`) = Pure Python functions that evaluate rules. No FastAPI imports here.

**API code** (`main.py`) = FastAPI routes that call the business logic and return HTTP responses. Can depend on `evaluator.py` but not vice versa.

This makes testing easier and business logic reusable.

```python
# evaluator.py (no FastAPI here)
def evaluate_loan(age: int, annual_income: float, 
                  requested_loan: float, credit_score: int) -> dict:
    rejection_reasons = []
    # Check each rule...
    return {"approved": len(rejection_reasons) == 0, "rejection_reasons": rejection_reasons}

# main.py (uses evaluator)
from fastapi import FastAPI
from evaluator import evaluate_loan

app = FastAPI()

@app.post("/api/loan/evaluate")
def submit_loan(application: LoanApplication):
    result = evaluate_loan(application.age, ...)
    return result
```

### 4. No Comments Needed For Obvious Code

Code should be clear enough to read without comments. Only add comments if the WHY is non-obvious.

```python
# Good ✓ - Code is self-explanatory
if 21 <= age <= 60:
    return True

# Unnecessary ✗
# Check if age is between 21 and 60
if 21 <= age <= 60:
    return True
```

### 5. Function Naming - Be Explicit

Function names should say what they do.

```python
# Good ✓
def is_age_valid(age: int) -> bool:
def get_rejection_reasons(application: dict) -> list:
def evaluate_loan(application: dict) -> dict:

# Bad ✗
def check(age: int) -> bool:
def get_reasons(x: dict) -> list:
def eval(application: dict) -> dict:
```

### 6. Follow PEP-8 Style Guide

- Use lowercase with underscores for function/variable names: `evaluate_loan`, not `evaluateLoan`
- Use 4 spaces for indentation (not tabs)
- Max line length ~88 characters (split long lines)
- Two blank lines between top-level functions

---

## Dependencies and Installation

### Step 1: Install Python 3.8+

Check your Python version:
```bash
python --version
```

### Step 2: Install Dependencies

All dependencies are listed in `requirements.txt`:

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pytest==7.4.3
httpx==0.25.2
```

Install them:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install fastapi uvicorn pydantic pytest httpx
```

**What each does:**
- `fastapi` — Web framework for building the API
- `uvicorn` — Server that runs the FastAPI app
- `pydantic` — Data validation library
- `pytest` — Testing framework
- `httpx` — Send HTTP requests (used in tests)

### Step 3: Running the Application

Start the API server:
```bash
uvicorn main:app --reload
```

Output should show:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test it works** (open another terminal):
```bash
curl -X POST "http://127.0.0.1:8000/api/loan/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"age": 35, "annual_income": 1000000, "requested_loan_amount": 2000000, "credit_score": 750}'
```

Expected response:
```json
{"approved": true, "message": "Application approved"}
```

### Step 4: Running Tests

Run all tests:
```bash
pytest
```

Run tests with verbose output (shows each test):
```bash
pytest -v
```

Run only unit tests:
```bash
pytest test_evaluator.py
```

Run only API tests:
```bash
pytest test_api.py
```

Run a specific test:
```bash
pytest test_evaluator.py::test_age_rule_passes_for_valid_age
```

**Test output example:**
```
test_evaluator.py::test_age_rule_passes_for_valid_age PASSED    [10%]
test_evaluator.py::test_age_rule_fails_for_too_young PASSED     [20%]
...
======================== 10 passed in 0.23s ========================
```

---

## Testing Guidelines

### Write Tests When You Add Business Logic

**Important Rule**: Every piece of business logic must have tests. If you add a new rule or change existing logic, write tests first.

### Test Structure

Two types of tests:

1. **Unit Tests** (`test_evaluator.py`) — Test business logic in isolation
   - Test individual rules
   - Test edge cases (boundaries: age 21, 60; income exactly 500000)
   - Test multiple failures

2. **Integration Tests** (`test_api.py`) — Test the full API
   - Test HTTP requests/responses
   - Test error handling
   - Test actual API behavior

### Example Test (Unit)

```python
def test_age_rule_fails_for_age_too_young():
    """Age below 21 should be invalid"""
    result = evaluate_loan(age=20, annual_income=600000, 
                          requested_loan=2000000, credit_score=750)
    assert result["approved"] == False
    assert "age_invalid" in result["rejection_reasons"]
```

### Example Test (Integration)

```python
def test_api_returns_rejected_for_low_age():
    """API should return 400 if age is not an integer"""
    response = client.post("/api/loan/evaluate", json={
        "age": "twenty",  # Invalid: should be int
        "annual_income": 600000,
        "requested_loan_amount": 2000000,
        "credit_score": 750
    })
    assert response.status_code == 400
```

### Test Naming Convention

Name tests so they describe what they test:

```python
# Good ✓
def test_age_rule_passes_for_valid_age():
def test_age_rule_fails_when_age_too_young():
def test_multiple_rules_fail_all_returned():
def test_api_returns_400_for_invalid_input():

# Bad ✗
def test_age():
def test_validation():
def test_1():
```

### Never Claim Tests Pass Without Running Them

**Critical Rule**: Do not say "I added tests" or "tests pass" unless you actually ran them.

Always run tests after adding logic:
```bash
pytest -v
```

Verify output shows `PASSED` for new tests, not `FAILED` or `ERROR`.

---

## Development Workflow

### Adding a New Rule

1. **Write the test first** (Test-Driven Development)
   - Add test case in `test_evaluator.py`
   - Test should fail initially (because rule doesn't exist yet)

2. **Implement the rule** in `evaluator.py`
   - Add logic to check the rule
   - Run tests to verify they pass

3. **Update API response** if needed in `main.py`
   - Make sure new rejection codes are returned properly

4. **Test the full API** 
   - Run integration tests: `pytest test_api.py`
   - Manually test with curl or Postman

### Modifying Business Rules

Example: Change minimum income from 500,000 to 600,000

1. Update requirement in `requirement.md`
2. Update the constant/rule in `evaluator.py`
3. Update affected tests in `test_evaluator.py`
4. Run tests: `pytest -v`
5. Verify they all pass before committing

---

## Key Principles to Remember

1. **Keep it simple** — No unnecessary abstractions. Straight-forward code is best.
2. **Test everything** — If you write code, write tests. Always run them.
3. **Type everything** — Use type hints so code is clear and catches errors early.
4. **Separate concerns** — Business logic away from API layer.
5. **No databases** — This is stateless and should stay that way.
6. **No frameworks creep** — Only use FastAPI, Pydantic, and pytest. Nothing else.
7. **Explain in conversations** — Keep explanations beginner-friendly and clear.
8. **No short-circuits** — Always evaluate all 4 rules, even if one fails.

---

## Useful Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn main:app --reload

# Run all tests
pytest -v

# Run only unit tests
pytest test_evaluator.py -v

# Run only API tests
pytest test_api.py -v

# Run tests with coverage (how much code is tested)
pytest --cov=. --cov-report=html

# Run a single test
pytest test_evaluator.py::test_age_rule_passes_for_valid_age -v

# Stop the API server (in terminal)
# Press Ctrl+C
```

---

## When to Ask Questions

Unclear about:
- The 4 business rules or how they interact?
- How Pydantic validation works?
- Why we separate business logic from API?
- How to write a specific test?
- What a specific error message means?

**Ask!** Better to clarify now than implement the wrong thing.


<!-- ##Introducing hooks -->
