import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Loan Underwriter",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000/api/loan/evaluate"

st.title("💰 Loan Underwriter")
st.markdown("Submit your loan application and get an instant decision")

with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    **How to use:**
    1. Fill in your application details
    2. Click "Evaluate Application"
    3. View your decision instantly

    **Business Rules:**
    - Age: 21-60 years
    - Income: ≥ 500,000
    - Loan: ≤ 5× income
    - Credit Score: ≥ 700
    """)

col1, col2 = st.columns([2, 1])

with col1:
    with st.form("loan_application"):
        st.subheader("Application Details")

        applicant_name = st.text_input(
            "Applicant Name",
            placeholder="John Doe",
            help="Optional - for reference only"
        )

        age = st.number_input(
            "Age (years)",
            min_value=0,
            max_value=120,
            value=35,
            step=1
        )

        annual_income = st.number_input(
            "Annual Income",
            min_value=0.0,
            value=600000.0,
            step=50000.0,
            format="%.0f"
        )

        requested_loan = st.number_input(
            "Requested Loan Amount",
            min_value=0.0,
            value=200000.0,
            step=50000.0,
            format="%.0f"
        )

        credit_score = st.number_input(
            "Credit Score",
            min_value=0,
            max_value=850,
            value=750,
            step=1
        )

        submitted = st.form_submit_button(
            "Evaluate Application",
            use_container_width=True,
            type="primary"
        )

if submitted:
    if annual_income <= 0:
        st.warning("⚠️ Annual income must be greater than 0")
    elif requested_loan <= 0:
        st.warning("⚠️ Requested loan amount must be greater than 0")
    else:
        payload = {
            "applicant_name": applicant_name if applicant_name else None,
            "age": int(age),
            "annual_income": float(annual_income),
            "requested_loan_amount": float(requested_loan),
            "credit_score": int(credit_score)
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=5)

            if response.status_code == 200:
                result = response.json()

                if result.get("approved"):
                    st.success("✅ **Application Approved!**")
                    st.markdown(f"**Applicant:** {result.get('applicant_name', 'N/A')}")
                    st.markdown(f"**Decision:** {result.get('message', 'Application approved')}")
                else:
                    st.error("❌ **Application Rejected**")

                    rejection_reasons = result.get("rejection_reasons", [])
                    if rejection_reasons:
                        st.markdown("**Reason(s) for rejection:**")
                        reason_descriptions = {
                            "age_invalid": "Age must be between 21-60 years",
                            "income_insufficient": "Annual income must be at least 500,000",
                            "loan_amount_exceeds_limit": "Requested loan exceeds 5× annual income",
                            "credit_score_insufficient": "Credit score must be at least 700",
                            "loan_amount_too_low": "Requested loan must be at least 50,000"
                        }

                        for reason in rejection_reasons:
                            description = reason_descriptions.get(reason, reason)
                            st.markdown(f"- {description}")

                    st.info("💡 **Tip:** Review the sidebar guidelines and adjust your application details.")

            elif response.status_code == 422:
                st.error("❌ **Validation Error**")
                try:
                    error_detail = response.json()
                    st.markdown("**Error details:**")
                    st.code(json.dumps(error_detail, indent=2))
                except:
                    st.error("Invalid input data provided")

            else:
                st.error(f"❌ **API Error:** Received status code {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("❌ **Connection Error**")
            st.markdown("""
            The API server is not running or not accessible.

            **To start the API server:**
            ```bash
            uvicorn main:app --reload
            ```
            Make sure the API is running on http://127.0.0.1:8000
            """)

        except requests.exceptions.Timeout:
            st.error("❌ **Request Timeout**")
            st.markdown("The API server took too long to respond. Please try again.")

        except Exception as e:
            st.error(f"❌ **Unexpected Error:** {str(e)}")
            st.markdown("Please try again or contact support if the issue persists.")
