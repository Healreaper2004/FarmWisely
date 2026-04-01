"""
metrics.py — Post-prediction agronomic and sustainability metrics.

NOT used in ML training — computed AFTER prediction.

ALL UNITS STANDARDIZED:
- Water Usage → mm per season
- Yield → tons (TOTAL)
- Area → acres
- Pesticide → kg
- CSFI → 0–1
"""

def compute_metrics(input_data, predicted_yield):
    """
    predicted_yield → TOTAL yield in tons
    """

    # ── Extract inputs safely ─────────────────────────────────────
    try:
        water     = float(input_data.get("Water_Usage", 0))      # mm
        csfi      = float(input_data.get("CSFI", 0))             # 0–1
        pesticide = float(input_data.get("Pesticide_Used", 0))   # kg
        area      = float(input_data.get("Farm_Area", 1))        # acres
    except:
        return {
            "WPI": 0,
            "NES": 0,
            "III": 0,
            "SRS": 0
        }

    # ── Guards (avoid division errors) ────────────────────────────
    water = max(water, 1e-6)
    area  = max(area, 1e-6)
    csfi  = max(csfi, 1e-6)

    # ── Convert yield → kg ───────────────────────────────────────
    yield_kg = predicted_yield * 1000   # tons → kg

    # ─────────────────────────────────────────────────────────────
    # 1️⃣ Water Productivity Index (WPI)
    # kg yield per mm water
    # Realistic range: 2 – 6 kg/mm (rice typical)
    # ─────────────────────────────────────────────────────────────
    WPI = yield_kg / water

    # ─────────────────────────────────────────────────────────────
    # 2️⃣ Nutrient Efficiency Score (NES)
    # kg yield per "effective nutrient factor"
    # CSFI acts as proxy → better soil = better efficiency
    # ─────────────────────────────────────────────────────────────
    NES = yield_kg / (csfi * 150)  
    # scaled better → avoids inflated values

    # ─────────────────────────────────────────────────────────────
    # 3️⃣ Input Intensity Index (III)
    # Total input pressure per acre
    # Includes fertilizer proxy + pesticide
    # ─────────────────────────────────────────────────────────────
    fertilizer_proxy = 60 + (1 - csfi) * 40  
    # low CSFI → more fertilizer needed

    III = (fertilizer_proxy + pesticide) / area

    # ─────────────────────────────────────────────────────────────
    # 4️⃣ Sustainability Risk Score (SRS)
    # Weighted multi-factor risk model
    # ─────────────────────────────────────────────────────────────
    risk = 0

    # 💧 Water Risk
    if water > 1400:
        risk += 0.3
    elif water > 1000:
        risk += 0.2

    # 🌱 Soil Risk (LOW CSFI = HIGH risk)
    if csfi < 0.4:
        risk += 0.4
    elif csfi < 0.65:
        risk += 0.2

    # 🧪 Pesticide Risk
    if pesticide > 2:
        risk += 0.3
    elif pesticide > 1:
        risk += 0.15

    SRS = min(risk, 1.0)

    # ─────────────────────────────────────────────────────────────
    # FINAL OUTPUT
    # ─────────────────────────────────────────────────────────────
    return {
        "WPI": round(WPI, 2),   # kg/mm
        "NES": round(NES, 2),
        "III": round(III, 2),
        "SRS": round(SRS, 3)
    }