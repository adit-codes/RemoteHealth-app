import streamlit as st
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="AI Health Agent", page_icon="🩺")

# Change these to your actual n8n Webhook URLs
URL_GLUCOSE_ANALYSIS = "https://byte-bees.app.n8n.cloud/webhook/12e2a32e-2034-4ee2-8eec-8fbb4b5c270c"
URL_GET_SLOTS = "https://byte-bees.app.n8n.cloud/webhook-test/calendar"
URL_CONFIRM_APPOINTMENT = "https://byte-bees.app.n8n.cloud/webhook/3e3e8ef7-a4ca-447e-b527-879e34a68104"

st.title("🩺 AI Medical Monitoring Portal")

tab1, tab2 = st.tabs(["Glucose Monitoring", "Schedule Appointment"])

# --- TAB 1: GLUCOSE MONITORING ---
with tab1:
    st.markdown("Enter your glucose readings for analysis.")
    with st.form("health_entry"):
        patient_name = st.text_input("Patient Name", value="John Doe")
        
        col1, col2 = st.columns(2)
        with col1:
            pre_meal = st.number_input("Pre-Meal Glucose (mg/dL)", min_value=20, max_value=500, value=100)
        with col2:
            post_meal = st.number_input("Post-Meal Glucose (mg/dL)", min_value=20, max_value=500, value=140)
        
        notes = st.text_area("Notes", placeholder="How are you feeling?")
        submit_button = st.form_submit_button("Submit Both Readings")

    if submit_button:
        payload = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Patient_Name": patient_name,
            "Readings": [
                {"Glucose_Level": pre_meal, "Reading_Type": "Pre-Meal"},
                {"Glucose_Level": post_meal, "Reading_Type": "Post-Meal"}
            ],
            "Notes": notes
        }
        
        with st.spinner("Agent checking trends..."):
            try:
                response = requests.post(URL_GLUCOSE_ANALYSIS, json=payload)
                if response.status_code == 200:
                    result = response.text.strip().lower()
                    if result == "true":
                        st.error("🚨 **RISK DETECTED:** The agent flagged a dangerous trend.")
                    else:
                        st.info(response.text) 
                else:
                    st.error("Error communicating with Analysis Agent.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- TAB 2: APPOINTMENT SCHEDULING ---
with tab2:
    st.subheader("📅 Doctor's Schedule")
    
    if st.button("Check Doctor Availability"):
        with st.spinner("Fetching slots..."):
            try:
                res = requests.get(URL_GET_SLOTS)
                if res.status_code == 200 and res.text:
                    data = res.json()
                    # Extract the 'slots' part
                    slots_data = data.get("slots", {})
                    
                    # Convert to list if it's a dict
                    if isinstance(slots_data, dict):
                        st.session_state.slots = list(slots_data.values())
                    else:
                        st.session_state.slots = slots_data
                    
                    st.success(f"Found {len(st.session_state.slots)} available slots!")
                else:
                    st.error(f"Error {res.status_code}: Could not retrieve slots.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    # Display Slots
    if "slots" in st.session_state and st.session_state.slots:
        st.write("Click a slot to confirm:")
