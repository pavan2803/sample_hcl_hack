from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    name: str
    age: int
    phone_number: Optional[str] = None

class PatientCreate(PatientBase):
    user_id: Optional[int] = None

class PatientResponse(PatientBase):
    id: int
    user_id: Optional[int]
    class Config:
        from_attributes = True

class HealthBase(BaseModel):
    bp: float
    sugar: float
    doctor_name: Optional[str] = None
    medicine: Optional[str] = None

class HealthCreate(HealthBase):
    patient_id: int

class HealthResponse(HealthBase):
    id: int
    patient_id: int
    class Config:
        from_attributes = True