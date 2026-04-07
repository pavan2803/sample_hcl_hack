from backend.database import SessionLocal
from backend.models import Patient, HealthRecord

db = SessionLocal()
patients = db.query(Patient).all()
records = db.query(HealthRecord).all()

def check_ascii(s, context):
    if s and not all(ord(c) < 128 for c in s):
        print(f"Non-ASCII found in {context}: {s}")

for p in patients:
    check_ascii(p.name, f"Patient {p.id} Name")
    check_ascii(p.phone_number, f"Patient {p.id} Phone")

for r in records:
    check_ascii(r.doctor_name, f"Record {r.id} Doctor")
    check_ascii(r.medicine, f"Record {r.id} Medicine")

db.close()
print("Check completed.")
