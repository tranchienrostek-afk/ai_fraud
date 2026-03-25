import streamlit as st
import requests
import json
import uuid
from datetime import date

st.set_page_config(page_title="Fraud Detective AI", layout="wide")

st.title("🛡️ AI Fraud Detection System")
st.markdown("### Multi-Layered Sieve Demonstration")

# Sidebar for Input
with st.sidebar:
    st.header("New Claim Submission")
    user_id = st.text_input("User ID", "U-1001")
    policy_no = st.text_input("Policy Number", "POL-999")
    amount = st.number_input("Claim Amount (VND)", value=5000000)
    diagnosis_code = st.text_input("ICD-10 Code", "A90")
    diagnosis_desc = st.text_input("Diagnosis Description", "Dengue fever")
    phone = st.text_input("Phone Number", "0901234567")
    treatment_date = st.date_input("Treatment Date", date.today())

    if st.button("Analyze Claim"):
        payload = {
            "claim_id": str(uuid.uuid4()),
            "user_id": user_id,
            "policy_number": policy_no,
            "claim_amount": amount,
            "diagnosis_code": diagnosis_code,
            "diagnosis_desc": diagnosis_desc,
            "treatment_date": treatment_date.isoformat(),
            "phone_number": phone,
            "hospital_name": "General Hospital",
            "doctor_id": "D-555",
        }

        with st.spinner("🕵️ Agents are investigating..."):
            try:
                # Call local API
                res = requests.post("http://localhost:8000/api/claim", json=payload)
                if res.status_code == 200:
                    st.session_state["result"] = res.json()
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# Main Display
if "result" in st.session_state:
    res = st.session_state["result"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Final Fraud Score", f"{res['final_score']}/100")
    with col2:
        color = "red" if res["risk_level"] in ["HIGH", "CRITICAL"] else "green"
        st.markdown(f"**Risk Level:** :{color}[{res['risk_level']}]")
    with col3:
        st.metric("Action", res["action"])

    st.divider()

    st.subheader("📝 Agent 05 Explanation (The Narrator)")
    st.info(res["explanation"])

    st.divider()
    st.markdown("#### System Logs")
    st.json(res)
