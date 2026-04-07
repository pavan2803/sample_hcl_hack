def calculate_health_risk(bp, sugar, age):
    """
    Simple AI heuristic to calculate health risk.
    Risk score: 0 (Normal) to 10 (Critical)
    """
    score = 0
    
    # BP Score (Systolic)
    if bp > 180: score += 5
    elif bp > 140: score += 3
    elif bp > 120: score += 1
    
    # Sugar Score
    if sugar > 250: score += 4
    elif sugar > 180: score += 2
    elif sugar > 140: score += 1
    
    # Age factor
    if age > 60: score += 1
    
    # Normalize
    if score >= 8: return "Critical"
    elif score >= 5: return "High Risk"
    elif score >= 3: return "Moderate"
    return "Low Risk/Stable"

def get_risk_recommendation(risk_level):
    recs = {
        "Critical": ["Emergency consultation required", "Strict sodium & sugar restriction", "Immediate medication review"],
        "High Risk": ["Twice daily monitoring", "Consult doctor within 24h", "Strict carb control"],
        "Moderate": ["Weekly monitoring", "Light exercise", "Maintain balanced diet"],
        "Low Risk/Stable": ["Monthly checkup", "Regular physical activity", "Stay hydrated"]
    }
    return recs.get(risk_level, ["Continue regular health monitoring"])
