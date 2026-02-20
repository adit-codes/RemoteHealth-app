import streamlit as st
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="AI Health Agent", page_icon="🩺")

st.title("🩺 AI Medical Monitoring Portal")

# TABS FOR BETTER ORGANIZATION
tab1, tab2 = st.tabs(["Glucose Monitoring", "Schedule Appointment"])

# --- TAB 1: GLUCOSE MONITORING ---
with tab1:
    st.markdown("Enter your daily glucose reading for risk analysis.")
    with st.form("health_entry"):
        patient_name = st.text_input("Patient Name", value="John Doe")
        col1, col2 = st.columns(2)
        with col1:
            glucose_value = st.number_input("Glucose Level (mg/dL)", min_value=20, max_value=500, value=120)
        with col2:
            reading_type = st.selectbox("Reading Type", ["Pre-Meal", "Post-Meal"])
        
        notes = st.text_area("How are you feeling today?", placeholder="Optional...")
        submit_button = st.form_submit_button("Submit & Analyze Trend")

    if submit_button:
        WEBHOOK_URL = "https://adi440.app.n8n.cloud/webhook-test/GLUCOSE-LEVEL"
        payload = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Glucose_Level": glucose_value,
            "Reading_Type": reading_type,
            "Patient_Name": patient_name
        }
        
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 200:
                    agent_result = response.text.strip().lower()
                    if agent_result == "true":
                        st.error("🚨 **DANGEROUS CONDITION DETECTED**")
                    else:
                        st.success("✅ **NO IMMEDIATE RISK DETECTED**")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- TAB 2: APPOINTMENT SCHEDULING ---
with tab2:
    st.subheader("📅 Book a Follow-up")
    
    # 1. FETCH SLOTS
    if st.button("Find Available Slots"):
        with st.spinner("Checking doctor's schedule..."):
            try:
                # Request slots from your agent
                slot_url = "https://adi440.app.n8n.cloud/webhook-test/GET-SLOTS"
                res = requests.get(slot_url)
                
                if res.status_code == 200:
                    # Expecting agent to return a list like ["2026-02-21 10:00", "2026-02-21 14:00"]
                    st.session_state.available_slots = res.json().get("slots", [])
                else:
                    st.error("Could not retrieve slots.")
            except Exception as e:
                st.error(f"Error fetching schedule: {e}")

    # 2. SELECT AND CONFIRM
    if "available_slots" in st.session_state and st.session_state.available_slots:
        selected_slot = st.selectbox("Choose a time:", st.session_state.available_slots)
        
        if st.button("Confirm Appointment"):
            with st.spinner("Booking..."):
                try:
                    confirm_url = "https://adi440.app.n8n.cloud/webhook-test/CONFIRM-APPOINTMENT"
                    conf_payload = {"selected_date": selected_slot, "patient": patient_name}
                    conf_res = requests.post(confirm_url, json=conf_payload)
                    
                    if conf_res.status_code == 200:
                        st.balloons()
                        st.success(f"🎊 Successfully Displayed! Your appointment for **{selected_slot}** is confirmed.")
                    else:
                        st.error("Confirmation failed.")
                except Exception as e:
                    st.error(f"Error sending selection: {e}")
    elif "available_slots" in st.session_state:
        st.info("No free slots detected for the upcoming days.")

st.divider()
st.caption("Hackathon Prototype - Agentic AI Remote Monitoring")
