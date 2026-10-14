# Loan Underwriter API

A fast, RESTful API that evaluates loan applications against underwriting rules and returns approval/rejection decisions within milliseconds.

## Features

- ✅ Automated loan eligibility assessment
- ✅ Consistent rule-based evaluation
- ✅ Transparent rejection reasons
- ✅ Millisecond response times
- ✅ Simple web UI for easy access

## Technology Stack

- **Backend:** Python 3.8+, FastAPI
- **Data Validation:** Pydantic
- **Frontend:** Streamlit
- **Testing:** pytest

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web API framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `streamlit` - Web UI framework
- `requests` - HTTP client library
- `pytest` & `httpx` - Testing tools

## Running the Application

### Option 1: Run Both API and UI (Recommended)

**Terminal 1 - Start the API:**
```bash
uvicorn main:app --reload
```
The API will be available at: `http://127.0.0.1:8000`
- API endpoint: `http://127.0.0.1:8000/api/loan/evaluate`
- Health check: `http://127.0.0.1:8000/health`

**Terminal 2 - Start the Streamlit UI:**
```bash
streamlit run streamlit_app.py
```
The UI will open automatically at: `http://localhost:8501`

### Option 2: API Only

If you want to use only the API without the UI, run:

```bash
uvicorn main:app --reload
```

Then test with curl:
```bash
curl -X POST "http://127.0.0.1:8000/api/loan/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "John Doe",
    "age": 35,
    "annual_income": 1000000,
    "requested_loan_amount": 2000000,
    "credit_score": 750
  }'
```

## Using the Web UI

1. Open the Streamlit app (http://localhost:8501)
2. Fill in the loan application form:
   - **Applicant Name** (optional)
   - **Age** (years)
   - **Annual Income**
   - **Requested Loan Amount**
   - **Credit Score**
3. Click "Evaluate Application"
4. View your decision:
   - **Approved:** Green checkmark with confirmation
   - **Rejected:** Red X with reasons for rejection

## Business Rules

An application is **APPROVED** only if ALL rules pass:

1. **Age Rule:** 21-60 years (inclusive)
2. **Income Rule:** Annual income ≥ 500,000
3. **Loan Amount Rule:** Requested loan ≤ 5× annual income
4. **Credit Score Rule:** Credit score ≥ 700
5. **Minimum Loan Rule:** Requested loan ≥ 50,000

If any rule fails, the application is rejected and all failure reasons are returned.

## API Endpoints

### POST /api/loan/evaluate

Evaluate a loan application.

**Request Body:**
```json
{
  "applicant_name": "John Doe",
  "age": 35,
  "annual_income": 1000000,
  "requested_loan_amount": 2000000,
  "credit_score": 750
}
```

**Success Response (200 OK - Approved):**
```json
{
  "approved": true,
  "message": "Application approved",
  "applicant_name": "John Doe",
  "decision_timestamp": "2024-01-15T10:30:45.123456+00:00"
}
```

**Success Response (200 OK - Rejected):**
```json
{
  "approved": false,
  "rejection_reasons": [
    "income_insufficient",
    "credit_score_insufficient"
  ],
  "applicant_name": "John Doe",
  "decision_timestamp": "2024-01-15T10:30:45.123456+00:00"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Validation error",
  "details": [...]
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Running Tests

Run all tests:
```bash
pytest -v
```

Run only unit tests:
```bash
pytest test_evaluator.py -v
```

Run only API tests:
```bash
pytest test_api.py -v
```

Run a specific test:
```bash
pytest test_evaluator.py::test_age_rule_passes_for_valid_age -v
```

## Project Structure

```
loanunderwriter/
├── main.py                    # FastAPI application & endpoints
├── evaluator.py               # Business logic (loan evaluation rules)
├── models.py                  # Pydantic models for validation
├── streamlit_app.py          # Streamlit web UI
├── test_evaluator.py         # Unit tests for business logic
├── test_api.py               # Integration tests for API
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── requirement.md            # Detailed requirements document
└── CLAUDE.md                 # Project development guide
```

## Examples

### Approved Application Example

**Scenario:** Ideal applicant
- Age: 35
- Annual Income: 1,000,000
- Requested Loan: 2,000,000 (2× income)
- Credit Score: 750

**Result:** ✅ APPROVED

### Rejected Application Example

**Scenario:** Multiple rule failures
- Age: 18 (too young)
- Annual Income: 400,000 (too low)
- Requested Loan: 3,000,000 (exceeds 5× income)
- Credit Score: 600 (too low)

**Result:** ❌ REJECTED
- Reasons:
  - Age must be between 21-60 years
  - Annual income must be at least 500,000
  - Requested loan exceeds 5× annual income
  - Credit score must be at least 700

## Development

### Adding a New Business Rule

1. Update the rule in `evaluator.py`
2. Add corresponding tests in `test_evaluator.py` and `test_api.py`
3. Run tests to verify: `pytest -v`
4. Update documentation

### Code Style

- Follow PEP-8 style guide
- Use type hints for all functions
- Write clear, self-explanatory variable names
- Add tests for any new functionality

## Troubleshooting

### Streamlit can't connect to API

**Problem:** "Connection Error - The API server is not running"

**Solution:** Make sure the API is running in another terminal:
```bash
uvicorn main:app --reload
```

### Port already in use

**Problem:** "Address already in use" error

**Solution:** The port is already occupied. Either:
- Stop the process using the port
- Run on a different port: `uvicorn main:app --reload --port 8001`

### Module not found errors

**Problem:** "ModuleNotFoundError" when running the app

**Solution:** Make sure dependencies are installed:
```bash
pip install -r requirements.txt
```

## Performance

- API response time: < 100ms per request
- Supports 100+ requests per second
- Stateless operation (no database)

## License

This project is provided as-is for educational purposes.
