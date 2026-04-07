import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("patients_records.csv")

print("Before Cleaning:", df.shape)

# -----------------------------------
# 1. Remove Duplicate Rows
# -----------------------------------
df = df.drop_duplicates()

# -----------------------------------
# 2. Handle NULL Values (Fill instead of delete)
# -----------------------------------
df["patient_name"] = df["patient_name"].fillna("Unknown")
df["doctor_name"] = df["doctor_name"].fillna("Unknown")
df["medicine"] = df["medicine"].fillna("Not Given")

# Fill numeric columns with median (better than mean)
numeric_cols = ["patient_id","patient_number","patient_age","doctor_id","bp","sugar"]

for col in numeric_cols:
    df[col] = df[col].fillna(df[col].median())

# -----------------------------------
# 3. Handle Negative Values
# -----------------------------------
for col in numeric_cols:
    df[col] = df[col].apply(lambda x: abs(x))  # convert negative → positive

# -----------------------------------
# 4. Fix Unrealistic Values (NOT delete rows)
# -----------------------------------

# Age: replace invalid with median
df.loc[(df["patient_age"] < 0) | (df["patient_age"] > 120), "patient_age"] = df["patient_age"].median()

# BP: clamp values
df["bp"] = df["bp"].clip(80, 200)

# Sugar: clamp values
df["sugar"] = df["sugar"].clip(70, 300)

# Patient number: fix length (make 10 digits)
df["patient_number"] = df["patient_number"].astype(str).str[:10]

# -----------------------------------
# Save cleaned data
# -----------------------------------
df.to_csv("cleaned_patient_records.csv", index=False)

print("After Cleaning:", df.shape)
print("Data cleaned WITHOUT losing real data ✅")