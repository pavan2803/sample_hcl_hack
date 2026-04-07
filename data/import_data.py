import pandas as pd
import os
import sys

# Add the project root to sys.path so we can import backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend import models

# Ensure tables are created (especially with the new schema)
models.Base.metadata.create_all(bind=engine)

def import_csv():
    # Load cleaned data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "cleaned_patient_records.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run data_analysis.py first.")
        return

    df = pd.read_csv(csv_path)
    db = SessionLocal()

    print(f"Starting import of {len(df)} records...")
    
    try:
        for index, row in df.iterrows():
            # 1. Create Patient
            # Note: since user_id is optional, we leave it as None for bulk imports
            db_patient = models.Patient(
                name=row['patient_name'],
                age=int(row['patient_age']),
                phone_number=str(row['patient_number'])
            )
            db.add(db_patient)
            db.flush() # Get the patient ID
            
            # 2. Create Health Record
            db_record = models.HealthRecord(
                patient_id=db_patient.id,
                bp=float(row['bp']),
                sugar=float(row['sugar']),
                doctor_name=row['doctor_name'],
                medicine=row['medicine']
            )
            db.add(db_record)

        db.commit()
        print("Import completed successfully! ✅")
    except Exception as e:
        db.rollback()
        print(f"Error during import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_csv()
