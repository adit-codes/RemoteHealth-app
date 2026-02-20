import streamlit as st
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="AI Health Agent", page_icon="🩺")

st.title("🩺 AI Medical Monitoring Portal")

tab1, tab2 = st.tabs(["Glucose Monitoring", "Schedule Appointment"])

# --- TAB 1: SIMULTANEOUS GLUCOSE MONITORING ---
with tab1:
    st.markdown("Enter your glucose readings for analysis.")
    with st.form("health_entry"):
        patient_name = st.text_input("Patient Name", value="John Doe")
        
        # Dual inputs for same-time submission
        col1, col2 = st.columns(2)
        with col1:
            pre_meal = st.number_input("Pre-Meal Glucose (mg/dL)", min_value=20, max_value=500, value=100)
        with col2:
            post_meal = st.number_input("Post-Meal Glucose (mg/dL)", min_value=20, max_value=500, value=140)
        
        notes = st.text_area("Notes", placeholder="How are you feeling?")
        submit_button = st.form_submit_button("Submit Both Readings")

    if submit_button:
        WEBHOOK_URL = "https://byte-bees.app.n8n.cloud/webhook-test/GLUCOSE-LEVEL"
        
        # Sending both readings in one structured payload
        payload = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Patient_Name": patient_name,
            "Readings": [
                {"Glucose_Level": pre_meal, "Reading_Type": "Pre-Meal"},
                {"Glucose_Level": post_meal, "Reading_Type": "Post-Meal"}
            ],
            "Notes": notes
        }
        
        with st.spinner("Agent checking trends..."):
            try:
                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 200:
                    result = response.text.strip().lower()
                    if result == "true":
                        st.error("🚨 **RISK DETECTED:** The agent flagged a dangerous trend.")
                    else:
                        st.success("✅ **STABLE:** No immediate risks detected.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- TAB 2: APPOINTMENT SCHEDULING ---
with tab2:
    st.subheader("📅 Doctor's Schedule")
    
    # Trigger to fetch slots
    if st.button("Check Doctor Availability"):
        with st.spinner("Fetching slots..."):
            try:
                # Replace with your actual n8n GET slots URL
                slot_url = "https://adi440.app.n8n.cloud/webhook-test/GET-SLOTS"
                res = requests.get(slot_url)
                if res.status_code == 200:
                    # Store slots in session state so they persist
                    st.session_state.slots = res.json().get("slots", [])
                else:
                    st.error("Failed to load slots.")
            except:
                st.error("Agent is offline.")

    # If slots are loaded, show selection
    if "slots" in st.session_state and st.session_state.slots:
        selected_date = st.selectbox("Select an available date/time:", st.session_state.slots)
        
        if st.button("Confirm Selection"):
            with st.spinner("Syncing with Agent..."):
                try:
                    confirm_url = "https://adi440.app.n8n.cloud/webhook-test/CONFIRM-APPOINTMENT"
                    conf_res = requests.post(confirm_url, json={
                        "selected_date": selected_date,
                        "patient": patient_name
                    })
                    
                    if conf_res.status_code == 200:
                        # Display specific confirmation text
                        st.success(f"Successfully Displayed: Appointment confirmed for {selected_date}")
                        st.balloons()
                    else:
                        st.error("Agent failed to book the slot.")
                except Exception as e:
                    st.error(f"Error: {e}")
