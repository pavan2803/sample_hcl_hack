def get_recommendation(bp, sugar):
    result = []

    if bp > 140:
        result.append("High BP -> Visit doctor immediately")

    if sugar > 180:
        result.append("High Sugar -> Follow strict diet")

    if bp <= 140 and sugar <= 180:
        result.append("Normal -> Maintain healthy lifestyle")

    return result