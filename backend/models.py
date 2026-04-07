from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String) # "doctor" or "patient"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    age = Column(Integer)
    phone_number = Column(String)

    user = relationship("User")
    records = relationship("HealthRecord", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    medications = relationship("Medication", back_populates="patient")

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    bp = Column(Float)
    sugar = Column(Float)
    doctor_name = Column(String)
    medicine = Column(String)

    patient = relationship("Patient", back_populates="records")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String)
    time = Column(String)
    status = Column(String, default="Pending") # Pending, Confirmed, Completed

    patient = relationship("Patient", back_populates="appointments")

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    drug_name = Column(String)
    dosage = Column(String)
    time = Column(String) # Morning, Evening, etc.
    is_taken = Column(Integer, default=0) # 0 or 1

    patient = relationship("Patient", back_populates="medications")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True)
    name = Column(String)
    phone = Column(String)
    relation = Column(String)