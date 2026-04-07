import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Patient System", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

def login_user(username, password):
    res = requests.post(f"{API}/login/", json={"username": username, "password": password})
    if res.status_code == 200:
        st.session_state.user = res.json()
        st.success(f"Welcome {username}!")
        st.rerun()
    else:
        st.error("Invalid credentials")

def logout_user():
    st.session_state.user = None
    st.rerun()

# --- Sidebar ---
st.sidebar.title("Smart Patient System")

if st.session_state.user:
    st.sidebar.write(f"Logged in as: **{st.session_state.user['username']}** ({st.session_state.user['role']})")
    if st.sidebar.button("Logout"):
        logout_user()
else:
    choice = st.sidebar.selectbox("Action", ["Login", "Register"])
    
    if choice == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            login_user(username, password)
    else:
        reg_user = st.sidebar.text_input("New Username")
        reg_pass = st.sidebar.text_input("New Password", type="password")
        role = st.sidebar.selectbox("Role", ["patient", "doctor"])
        
        # If registering as patient, we need patient details
        p_name = ""
        p_age = 0
        if role == "patient":
            p_name = st.sidebar.text_input("Full Name")
            p_age = st.sidebar.number_input("Age", min_value=1, max_value=120)

        if st.sidebar.button("Register"):
            res = requests.post(f"{API}/register/", json={
                "username": reg_user,
                "password": reg_pass,
                "role": role
            })
            if res.status_code == 200:
                user_data = res.json()
                if role == "patient":
                    # Link user to patient
                    requests.post(f"{API}/patients/", json={
                        "name": p_name,
                        "age": p_age,
                        "user_id": user_data["id"]
                    })
                st.sidebar.success("Account created! Please login.")
            else:
                st.sidebar.error("Registration failed or username exists.")

# --- Main Page Content ---
if not st.session_state.user:
    st.title("Welcome to the Smart Patient Monitoring System")
    st.info("Please login or register from the sidebar to continue.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("For Doctors")
        st.write("- Monitor all patient health data in real-time.")
        st.write("- Get system alerts for critical conditions.")
        st.write("- View patient history and recommendations.")
    with col2:
        st.subheader("For Patients")
        st.write("- View your health records anytime.")
        st.write("- Get personalized AI health recommendations.")
        st.write("- Download professional medical reports.")

else:
    user = st.session_state.user
    
    if user["role"] == "doctor":
        st.title("🩺 Doctor Dashboard")
        
        menu = ["Patient Monitoring", "Add Health Records"]
        tab1, tab2 = st.tabs(menu)
        
        with tab1:
            st.header("Active Patient Monitoring")
            res = requests.get(f"{API}/doctor/patients/")
            if res.status_code == 200:
                data = res.json()
                if data:
                    df = pd.DataFrame(data)
                    # Color background based on status
                    def color_status(val):
                        color = 'red' if val == "Check" else 'green'
                        return f'background-color: {color}'
                    
                    st.dataframe(df.style.applymap(color_status, subset=['status']), use_container_width=True)
                    
                    # Selection for detailed view
                    selected_patient = st.selectbox("Select Patient for detailed report", df['name'].tolist())
                    patient_id = df[df['name'] == selected_patient]['id'].iloc[0]
                    
                    if st.button("Generate Detailed Recommendation"):
                        rec_res = requests.get(f"{API}/health/recommend/{patient_id}")
                        if rec_res.status_code == 200:
                            st.json(rec_res.json())
                else:
                    st.write("No patients registered yet.")
        
        with tab2:
            st.header("Add Patient Health Data")
            # Get list of patients for selection
            res = requests.get(f"{API}/doctor/patients/")
            if res.status_code == 200:
                patients = res.json()
                p_names = {p["id"]: p["name"] for p in patients}
                if p_names:
                    pid = st.selectbox("Select Patient", options=list(p_names.keys()), format_func=lambda x: p_names[x])
                    bp = st.number_input("Blood Pressure (systolic)", min_value=50, max_value=250, value=120)
                    sugar = st.number_input("Sugar Level", min_value=50, max_value=500, value=100)
                    
                    if st.button("Submit Data"):
                        res = requests.post(f"{API}/health/", json={
                            "patient_id": pid,
                            "bp": bp,
                            "sugar": sugar
                        })
                        if res.status_code == 200:
                            st.success("Health record added!")
                            st.rerun()
                else:
                    st.warning("No patients found to add data for.")

    elif user["role"] == "patient":
        st.title("👤 Patient Portal")
        
        if not user["patient_id"]:
            st.warning("No patient record linked to this account. Please contact your doctor.")
        else:
            pid = user["patient_id"]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.header("My Health Records")
                rec_res = requests.get(f"{API}/health/recommend/{pid}")
                if rec_res.status_code == 200:
                    health_status = rec_res.json()
                    st.metric("Latest BP", health_status.get("bp", "N/A"))
                    st.metric("Latest Sugar", health_status.get("sugar", "N/A"))
                    
                    st.subheader("Doctor Recommendation")
                    for r in health_status.get("recommendation", ["No recommendations yet"]):
                        st.info(r)
                else:
                    st.write("No health records found yet.")
            
            with col2:
                st.header("Actions")
                report_url = f"{API}/patients/{pid}/report"
                
                if st.button("Generate & Download PDF Report"):
                    res = requests.get(report_url)
                    if res.status_code == 200:
                        st.download_button(
                            label="Click here to download",
                            data=res.content,
                            file_name=f"health_report_{pid}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Failed to generate report.")