"""
metrics.py — Post-prediction agronomic and sustainability metrics.
NOT used in ML training — computed AFTER prediction.
"""

def compute_metrics(input_data, predicted_yield):
    water     = float(input_data["Water_Usage"])
    csfi      = float(input_data["CSFI"])
    pesticide = float(input_data["Pesticide_Used"])
    area      = float(input_data["Farm_Area"])

    # Guard zero division
    if water     <= 0: water     = 1e-6
    if csfi      <= 0: csfi      = 1e-6
    if area      <= 0: area      = 1e-6

    # 1️⃣  Water Productivity Index — yield per m³ water
    WPI = predicted_yield / water

    # 2️⃣  Nutrient Efficiency Score — yield per unit soil fertility
    NES = predicted_yield / csfi

    # 3️⃣  Input Intensity Index — total input load per acre
    # ✅ FIXED: csfi * 10 scales the dimensionless [0,1] CSFI
    #    to a fertilizer-equivalent (tons) before adding pesticide (kg/2.5 scale)
    #    so both terms are in comparable magnitude before dividing by area
    III = (csfi * 10 + pesticide) / area

    # 4️⃣  Sustainability Risk Score — all components clamped to [0,1]
    MAX_WATER     = 6000.0   # m³/season — matches actual data range
    MAX_CSFI      = 1.0      # CSFI is already [0,1]
    MAX_PESTICIDE = 2.5      # max trained value (High = 2.5)

    SRS = (
        0.4 * min(water     / MAX_WATER,     1.0) +
        0.3 * min(csfi      / MAX_CSFI,      1.0) +
        0.3 * min(pesticide / MAX_PESTICIDE, 1.0)
    )

    return {
        "WPI": round(WPI, 4),
        "NES": round(NES, 4),
        "III": round(III, 4),
        "SRS": round(SRS, 4)
    }