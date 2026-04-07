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
        st.sidebar.subheader("Doctor Registration")
        reg_user = st.sidebar.text_input("Username")
        reg_pass = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Register as Doctor"):
            res = requests.post(f"{API}/register/", json={
                "username": reg_user,
                "password": reg_pass,
                "role": "doctor"
            })
            if res.status_code == 200:
                st.sidebar.success("Doctor account created! Please login.")
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
        menu = ["Monitoring", "New Patient", "Appointments", "Prescribe"]
        tab1, tab2, tab3, tab4 = st.tabs(menu)
        
        with tab1:
            st.header("📋 Patient Analytics")
            res = requests.get(f"{API}/doctor/patients/")
            if res.status_code == 200:
                data = res.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    pid = st.selectbox("Select Patient for deep analysis", df['id'].tolist())
                    if st.button("Generate AI Risk Scan"):
                        risk_res = requests.get(f"{API}/health/risk/{pid}")
                        if risk_res.status_code == 200:
                            risk_data = risk_res.json()
                            st.metric("AI Risk Status", risk_data['risk'])
                            for r in risk_data['recommendations']:
                                st.warning(r)
                else:
                    st.write("No patients registered.")
        
        with tab2:
            st.header("📝 Register New Patient")
            with st.form("new_patient_form"):
                new_p_name = st.text_input("Full Name")
                new_p_age = st.number_input("Age", 1, 120, 30)
                new_p_phone = st.text_input("Phone Number")
                st.divider()
                st.subheader("Patient Login Credentials")
                new_p_user = st.text_input("Username")
                new_p_pass = st.text_input("Password", type="password")
                
                if st.form_submit_button("Register Patient & Create Account"):
                    if new_p_name and new_p_phone and new_p_user and new_p_pass:
                        u_res = requests.post(f"{API}/register/", json={"username": new_p_user, "password": new_p_pass, "role": "patient"})
                        if u_res.status_code == 200:
                            uid = u_res.json()["id"]
                            requests.post(f"{API}/patients/", json={"name": new_p_name, "age": new_p_age, "phone_number": new_p_phone, "user_id": uid})
                            st.success(f"Patient {new_p_name} registered successfully!")
                            st.rerun()

        with tab3:
            st.header("📅 Appointments Center")
            appt_res = requests.get(f"{API}/appointments/doctor/{user['id']}")
            if appt_res.status_code == 200:
                appts = appt_res.json()
                if appts:
                    st.table(pd.DataFrame(appts))
                else:
                    st.info("No appointments scheduled for your profile.")

        with tab4:
            st.header("💊 Prescription Management")
            res = requests.get(f"{API}/doctor/patients/")
            if res.status_code == 200:
                patients = res.json()
                p_names = {p["id"]: p["name"] for p in patients}
                with st.form("prescribe_form"):
                    pid = st.selectbox("Patient", options=list(p_names.keys()), format_func=lambda x: p_names[x])
                    med_name = st.text_input("Medication Name")
                    dosage = st.text_input("Dosage")
                    timing = st.selectbox("Timing", ["Morning", "Afternoon", "Evening", "Night"])
                    if st.form_submit_button("Add Medication"):
                        requests.post(f"{API}/medications/", json={"patient_id": pid, "drug_name": med_name, "dosage": dosage, "time": timing})
                        st.success("Prescription added!")

    elif user["role"] == "patient":
        st.title("👤 Patient Health Portal")
        if not user["patient_id"]:
            st.warning("No patient record linked to this account.")
        else:
            pid = user["patient_id"]
            risk_res = requests.get(f"{API}/health/risk/{pid}")
            if risk_res.status_code == 200:
                risk_data = risk_res.json()
                if risk_data["risk"] == "Critical":
                    st.error("🚨 **CRITICAL ALERT**: Emergency consultation required!")
                elif risk_data["risk"] == "High Risk":
                    st.warning("⚠️ **HIGH RISK**: Consult your doctor soon.")

            st.divider()
            menu = ["My Trends", "Medication Tracker", "Doctor Recommendations", "Reports"]
            t1, t2, t3, t4 = st.tabs(menu)
            
            with t1:
                st.header("📈 Health Statistics")
                rec_res = requests.get(f"{API}/health/recommend/{pid}")
                if rec_res.status_code == 200:
                    health_status = rec_res.json()
                    c1, c2 = st.columns(2)
                    c1.metric("Current BP", health_status.get("bp", "N/A"))
                    c2.metric("Current Sugar", health_status.get("sugar", "N/A"))
                    chart_data = pd.DataFrame({"Metric": ["Target", "Current"], "Value": [120, health_status.get("bp", 120)]}).set_index("Metric")
                    st.line_chart(chart_data)

            with t2:
                st.header("💊 Daily Medication Tracker")
                med_res = requests.get(f"{API}/medications/patient/{pid}")
                if med_res.status_code == 200:
                    meds = med_res.json()
                    for m in meds:
                        taken = st.checkbox(f"{m['drug_name']} ({m['dosage']})", value=bool(m['is_taken']), key=f"med_{m['id']}")
                        if taken != bool(m['is_taken']):
                            requests.patch(f"{API}/medications/{m['id']}", params={"is_taken": int(taken)})

            with t3:
                st.header("🩺 Doctor's Note")
                if risk_res.status_code == 200:
                    st.subheader(f"Risk Rating: {risk_data['risk']}")
                    for rec in risk_data['recommendations']:
                        st.success(f"• {rec}")

            with t4:
                st.header("📄 Download Center")
                
                # Use session state to keep the download button visible after generation
                if "pdf_report" not in st.session_state:
                    st.session_state.pdf_report = None
                
                if st.button("Generate Medical PDF"):
                    with st.spinner("Generating Report..."):
                        report_res = requests.get(f"{API}/patients/{pid}/report")
                        if report_res.status_code == 200:
                            st.session_state.pdf_report = report_res.content
                            st.success("Report Generated!")
                        else:
                            st.error(f"Failed to fetch report: {report_res.status_code} - {report_res.text}")

                if st.session_state.pdf_report:
                    st.download_button(
                        label="📥 Click here to Download PDF",
                        data=st.session_state.pdf_report,
                        file_name=f"health_report_{pid}.pdf",
                        mime="application/pdf",
                        key="download_btn_final"
                    )

    elif user["role"] == "admin":
        st.title("🛡️ Hospital Administration")
        stats_res = requests.get(f"{API}/admin/stats")
        if stats_res.status_code == 200:
            stats = stats_res.json()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Patients", stats["total_patients"])
            col2.metric("Total Records", stats["total_records"])
            col3.metric("Appointments", stats["total_appointments"])
            st.divider()
            st.success("✅ System Status: ALL SYSTEMS OPERATIONAL")