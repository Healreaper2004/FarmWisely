def get_recommendations(data, predicted_yield, fertilizer, metrics, csfi=0.5):
    """
    Rule-based recommendation engine.
    Uses:
      - predicted_yield  : from ML model (tons)
      - fertilizer       : from fertilizer_rules
      - metrics          : WPI, NES, III, SRS (post-prediction)
    """

    recommendations = {}

    crop       = data["crop_type"]
    irrigation = data["irrigation_type"]
    season     = data["season"]
    soil       = data["soil_type"]

    # 1️⃣  Fertilizer recommendation
    recommendations["fertilizer"] = fertilizer

    # 2️⃣  Water usage recommendation
    if crop == "Rice":
        recommendations["water_usage"] = (
            "700–900 mm per season" if irrigation == "Drip"
            else "1200–1500 mm per season"
        )
    else:
        recommendations["water_usage"] = (
            "500–700 mm per season" if irrigation == "Drip"
            else "800–1000 mm per season"
        )

    # 3️⃣  Improvement suggestions
    improvements = []

    # Yield-based message — CSFI-aware
    if predicted_yield < 3:
        improvements.extend([
            "Low predicted yield detected.",
            "Ensure timely irrigation and proper crop management.",
            "Consider soil testing for nutrient balance."
        ])
    elif predicted_yield < 6:
        improvements.append("Moderate yield predicted. Optimise nutrient and water usage.")
    else:
        if csfi < 0.30:
            improvements.append(
                "Good yield achieved but soil fertility is critically low (CSFI < 0.30). "
                "High inputs are compensating for poor soil — this is unsustainable. "
                "Apply organic matter or soil amendments."
            )
        elif csfi < 0.60:
            improvements.append(
                "Good yield predicted. Soil fertility is moderate — consider improving CSFI."
            )
        else:
            improvements.append("Good yield predicted. Maintain current best practices.")

    # Irrigation efficiency
    if irrigation != "Drip":
        improvements.append("Switch to drip irrigation to improve water efficiency.")

    # 4️⃣  Metric-based rules

    # Water Productivity Index
    if metrics["WPI"] < 0.003:
        improvements.append("Low water productivity. Optimise irrigation scheduling.")

    # Nutrient Efficiency Score — recalibrated for CSFI-based NES (range 3–250)
    if metrics["NES"] < 10:                          # ✅ FIXED: was < 2 (never fired)
        improvements.append("Low nutrient efficiency. Adopt balanced fertiliser application.")

    # Input Intensity Index
    if metrics["III"] > 3:
        improvements.append("High input usage per acre. Reduce excessive fertiliser/pesticide use.")

    # Sustainability Risk Score
    if metrics["SRS"] > 0.7:
        improvements.append("High sustainability risk. Adopt eco-friendly low-input practices.")

    improvements = list(dict.fromkeys(improvements))
    recommendations["improvements"] = improvements

    # 5️⃣  Crop rotation rules — all 4 trained crops × all 3 seasons covered
    crop_rotation_rules = {
        "Rice": {
            "Kharif": ["Wheat",    "Mustard"],
            "Rabi":   ["Pulses",   "Vegetables"],
            "Zaid":   ["Maize",    "Pulses"],       # ✅ ADDED
        },
        "Wheat": {
            "Rabi":   ["Rice",     "Maize"],
            "Kharif": ["Pulses"],
            "Zaid":   ["Maize",    "Vegetables"],   # ✅ ADDED
        },
        "Maize": {
            "Kharif": ["Wheat",    "Potato"],
            "Rabi":   ["Pulses"],
            "Zaid":   ["Pulses",   "Vegetables"],   # ✅ ADDED
        },
        "Cotton": {
            "Kharif": ["Soybean",  "Pulses"],
            "Rabi":   ["Chickpea"],
        },
        "Sugarcane": {
            "Kharif": ["Wheat",    "Mustard"],
            "Rabi":   ["Maize",    "Pulses"],
        },
        "Potato": {
            "Rabi":   ["Maize",    "Rice"],
            "Kharif": ["Wheat",    "Mustard"],
        },
        "Soybean": {
            "Kharif": ["Wheat",    "Chickpea"],
            "Rabi":   ["Maize"],
            "Zaid":   ["Maize",    "Pulses"],       # ✅ ADDED
        },
    }

    possible_next_crops = crop_rotation_rules.get(crop, {}).get(season)

    if possible_next_crops:
        # ✅ FIXED: added "Clayey" alongside "Clay" and "Loamy"
        if soil in ("Loamy", "Clay", "Clayey") and len(possible_next_crops) > 1:
            recommendations["next_crop"] = possible_next_crops[0]
        else:
            recommendations["next_crop"] = possible_next_crops[-1]
    else:
        recommendations["next_crop"] = "Pulses"

    return recommendations