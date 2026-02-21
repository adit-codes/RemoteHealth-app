import streamlit as st
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="AI Health Agent", page_icon="🩺")

# Change these to your actual n8n Webhook URLs
URL_GLUCOSE_ANALYSIS = "https://byte-bees.app.n8n.cloud/webhook/12e2a32e-2034-4ee2-8eec-8fbb4b5c270c"
URL_GET_SLOTS = "https://byte-bees.app.n8n.cloud/webhook/calendar"
URL_CONFIRM_APPOINTMENT = "https://byte-bees.app.n8n.cloud/webhook/slotbook"

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
import json

# --- TAB 2: APPOINTMENT SCHEDULING ---
with tab2:
    st.subheader("📅 Doctor's Schedule")
    
    if st.button("Check Doctor Availability"):
        with st.spinner("Fetching slots..."):
            try:
                res = requests.get(URL_GET_SLOTS)
                if res.status_code == 200 and res.text:
                    data = res.json()
                    
                    # 1. Extract the slots
                    slots_raw = data.get("slots", {})
                    
                    # 2. Handle if n8n sends slots as a JSON string instead of an object
                    if isinstance(slots_raw, str):
                        slots_raw = json.loads(slots_raw)
                    
                    # 3. Store the full Dictionary in session state (don't convert to list)
                    st.session_state.slots = slots_raw
                    
                    st.success(f"Found {len(st.session_state.slots)} available slots!")
                else:
                    st.error(f"Error {res.status_code}: Could not retrieve slots.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    # --- DISPLAY SLOTS & HANDLE CONFIRMATION ---
    # We use .get() to avoid errors if the key doesn't exist yet
    current_slots = st.session_state.get("slots", {})

    if current_slots:
        st.write("Click a slot to confirm:")
        
        # Now .items() will work because current_slots is a dictionary
        for slot_key, slot_time in current_slots.items():
            if st.button(slot_time, key=slot_key, use_container_width=True):
                
                payload = {
                    "selected_slot": slot_time,
                    "slot_id": slot_key,
                    "patient_name": patient_name, # Added this from Tab 1 for context
                    "status": "CONFIRMED"
                }
                
                try:
                    with st.spinner("Confirming..."):
                        st.write(f"Attempting to connect to: {URL_CONFIRM_APPOINTMENT}")
                        response = requests.post(URL_CONFIRM_APPOINTMENT, json=payload)
                    
                    if response.status_code == 200:
                        st.success(f"✅ Appointment confirmed for {slot_time}!")
                        # Clear state and refresh
                        st.session_state.slots = {} 
                        st.rerun()
                    else:
                        st.error(f"Failed to confirm. Error: {response.status_code}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
