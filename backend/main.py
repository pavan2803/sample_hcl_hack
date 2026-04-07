from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from . import database, models, schemas, crud
from .recommendation import get_recommendation
from .analytics import calculate_health_risk, get_risk_recommendation
from fpdf import FPDF
import io

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

# Initialize App
app = FastAPI()

# DB Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- New v2.0 Endpoints ---

@app.get("/health/risk/{patient_id}")
def get_risk_analysis(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    records = crud.get_records(db, patient_id)
    if not records:
        return {"risk": "Unknown", "recommendations": ["No data detected"]}
    
    latest = records[-1]
    risk = calculate_health_risk(latest.bp, latest.sugar, patient.age)
    recs = get_risk_recommendation(risk)
    return {"risk": risk, "recommendations": recs}

@app.post("/appointments/", response_model=schemas.AppointmentResponse)
def create_appointment(appt: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    return crud.create_appointment(db, appt)

@app.get("/appointments/patient/{patient_id}", response_model=list[schemas.AppointmentResponse])
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    return crud.get_appointments_by_patient(db, patient_id)

@app.get("/appointments/doctor/{doctor_id}", response_model=list[schemas.AppointmentResponse])
def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):
    return crud.get_appointments_by_doctor(db, doctor_id)

@app.post("/medications/", response_model=schemas.MedicationResponse)
def create_medication(med: schemas.MedicationCreate, db: Session = Depends(get_db)):
    return crud.create_medication(db, med)

@app.get("/medications/patient/{patient_id}", response_model=list[schemas.MedicationResponse])
def get_patient_medications(patient_id: int, db: Session = Depends(get_db)):
    return crud.get_medications_by_patient(db, patient_id)

@app.patch("/medications/{med_id}")
def toggle_medication(med_id: int, is_taken: int, db: Session = Depends(get_db)):
    return crud.update_medication_status(db, med_id, is_taken)

@app.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    total_patients = db.query(models.Patient).count()
    total_records = db.query(models.HealthRecord).count()
    total_appointments = db.query(models.Appointment).count()
    return {
        "total_patients": total_patients,
        "total_records": total_records,
        "total_appointments": total_appointments
    }

# --- Core Authentication & Patient Endpoints ---

@app.post("/register/", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user or not crud.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    patient = crud.get_patient_by_user_id(db, db_user.id)
    return {
        "id": db_user.id,
        "username": db_user.username,
        "role": db_user.role,
        "patient_id": patient.id if patient else None
    }

@app.post("/patients/", response_model=schemas.PatientResponse)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db, patient)

@app.post("/health/", response_model=schemas.HealthResponse)
def add_health(record: schemas.HealthCreate, db: Session = Depends(get_db)):
    return crud.add_health_record(db, record)

@app.get("/doctor/patients/")
def get_all_patients_data(db: Session = Depends(get_db)):
    patients = crud.get_all_patients(db)
    result = []
    for p in patients:
        records = crud.get_records(db, p.id)
        latest = records[-1] if records else None
        result.append({
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "latest_bp": latest.bp if latest else "N/A",
            "latest_sugar": latest.sugar if latest else "N/A",
            "status": "Check" if latest and (latest.bp > 140 or latest.sugar > 180) else "Stable"
        })
    return result

@app.get("/health/recommend/{patient_id}")
def recommend(patient_id: int, db: Session = Depends(get_db)):
    records = crud.get_records(db, patient_id)
    if not records:
        return {"msg": "No records found"}
    latest = records[-1]
    rec = get_recommendation(latest.bp, latest.sugar)
    return {
        "bp": latest.bp,
        "sugar": latest.sugar,
        "recommendation": rec
    }

@app.get("/patients/{patient_id}/report")
def generate_report(patient_id: int, db: Session = Depends(get_db)):
    try:
        patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        records = crud.get_records(db, patient_id)
        
        def clean(text):
            if text is None: return ""
            return str(text).encode("latin-1", "replace").decode("latin-1")

        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, txt=clean("Medical Health Report"), ln=1, align='C')
        pdf.ln(10)
        
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, txt=clean(f"Patient Name: {patient.name}"), ln=1)
        pdf.cell(0, 10, txt=clean(f"Age: {patient.age}"), ln=1)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(60, 10, clean("Record Details"), border=1)
        pdf.cell(60, 10, clean("BP Status"), border=1)
        pdf.cell(60, 10, clean("Sugar Level"), border=1)
        pdf.ln()
        
        pdf.set_font("Helvetica", size=11)
        for i, r in enumerate(records):
            pdf.cell(60, 10, clean(f"Record {i+1}"), border=1)
            pdf.cell(60, 10, clean(str(r.bp)), border=1)
            pdf.cell(60, 10, clean(str(r.sugar)), border=1)
            pdf.ln()
        
        if records:
            latest = records[-1]
            rec = get_recommendation(latest.bp, latest.sugar)
            pdf.ln(10)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, txt=clean("Latest Medical Recommendations:"), ln=1)
            pdf.set_font("Helvetica", size=11)
            for line in rec:
                pdf.multi_cell(190, 10, txt=clean(f"- {line}"))

        return Response(
            content=bytes(pdf.output()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{patient_id}.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))