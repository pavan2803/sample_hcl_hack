from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(
        name=patient.name, 
        age=patient.age, 
        user_id=patient.user_id,
        phone_number=patient.phone_number
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def add_health_record(db: Session, record: schemas.HealthCreate):
    db_record = models.HealthRecord(
        patient_id=record.patient_id,
        bp=record.bp,
        sugar=record.sugar,
        doctor_name=record.doctor_name,
        medicine=record.medicine
    )
    db.add(db_record)
    db.commit()
    return db_record

def get_records(db: Session, patient_id: int):
    return db.query(models.HealthRecord).filter(
        models.HealthRecord.patient_id == patient_id
    ).all()

def get_all_patients(db: Session):
    return db.query(models.Patient).all()

def get_patient_by_user_id(db: Session, user_id: int):
    return db.query(models.Patient).filter(models.Patient.user_id == user_id).first()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- New v2.0 CRUD ---

def create_appointment(db: Session, appt: schemas.AppointmentCreate):
    db_appt = models.Appointment(**appt.dict())
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    return db_appt

def get_appointments_by_patient(db: Session, patient_id: int):
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()

def get_appointments_by_doctor(db: Session, doctor_id: int):
    return db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).all()

def create_medication(db: Session, med: schemas.MedicationCreate):
    db_med = models.Medication(**med.dict())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med

def get_medications_by_patient(db: Session, patient_id: int):
    return db.query(models.Medication).filter(models.Medication.patient_id == patient_id).all()

def update_medication_status(db: Session, med_id: int, is_taken: int):
    db_med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if db_med:
        db_med.is_taken = is_taken
        db.commit()
    return db_med