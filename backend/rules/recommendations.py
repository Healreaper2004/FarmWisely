from backend.rules.nutrient_rules import get_nutrient_advisory

def get_recommendations(data, predicted_yield, fertilizer, metrics, csfi=0.5):

    recommendations = {}

    crop       = data["crop_type"]
    irrigation = data["irrigation_type"]
    season     = data["season"]
    soil       = data["soil_type"]

    # ─────────────────────────────────────────────
    # 1️⃣ Fertilizer
    # ─────────────────────────────────────────────
    recommendations["fertilizer"] = fertilizer

    # ─────────────────────────────────────────────
    # 2️⃣ Nutrient Advisory (NEW)
    # ─────────────────────────────────────────────
    recommendations["nutrient_advisory"] = get_nutrient_advisory(
        crop_type=crop,
        csfi=csfi
    )

    # ─────────────────────────────────────────────
    # 3️⃣ Water Recommendation
    # ─────────────────────────────────────────────
    irrigation_warning = None

    if crop == "Rice":
        if irrigation == "Drip":
            irrigation_warning = "Drip irrigation is uncommon for rice. Use aerobic/SRI method."
            recommendations["water_usage"] = "900–1100 mm per season"
        else:
            recommendations["water_usage"] = "1200–1500 mm per season"
    else:
        if irrigation == "Drip":
            recommendations["water_usage"] = "500–700 mm per season"
        else:
            recommendations["water_usage"] = "800–1000 mm per season"

    if irrigation_warning:
        recommendations["irrigation_warning"] = irrigation_warning

    # ─────────────────────────────────────────────
    # 4️⃣ Improvements
    # ─────────────────────────────────────────────
    improvements = []

    # Yield logic
    if predicted_yield < 2.5:
        improvements.extend([
            "Low predicted yield detected.",
            "Improve seed quality, irrigation timing, and nutrient management.",
            "Conduct detailed soil testing."
        ])
    elif predicted_yield < 5:
        improvements.append("Moderate yield predicted. Optimise nutrient and water usage.")
    else:
        if csfi < 0.30:
            improvements.append("High yield but poor soil fertility — input-driven and unsustainable.")
        elif csfi < 0.60:
            improvements.append("Good yield with moderate soil fertility. Improve soil health gradually.")
        else:
            improvements.append("Good yield and healthy soil. Maintain current practices.")

    # CSFI-based
    if csfi < 0.5:
        improvements.append("Improve soil fertility using compost, green manure, or biofertilisers.")

    # Irrigation
    if irrigation != "Drip":
        improvements.append("Consider drip irrigation to improve water efficiency.")

    # ─────────────────────────────────────────────
    # 5️⃣ Metrics-based (FIXED LOGIC)
    # ─────────────────────────────────────────────

    # Water productivity
    if metrics["WPI"] < 3:
        improvements.append("Low water productivity. Optimise irrigation scheduling.")

    # Nutrient efficiency
    if metrics["NES"] < 40:
        improvements.append("Low nutrient efficiency. Improve balanced fertilisation.")

    # Input Intensity (FIXED)
    iii = metrics.get("III", 0)

    if iii > 35:
        improvements.append("High input usage per acre. Reduce excessive fertiliser and pesticide use.")
    elif iii > 20:
        improvements.append("Moderate input usage. Optimise fertiliser application for better efficiency.")
    else:
        improvements.append("Low input usage. Ensure sufficient nutrients for optimal yield.")

    # Sustainability Risk
    if metrics["SRS"] > 0.6:
        improvements.append("High sustainability risk. Adopt eco-friendly farming practices.")

    # Remove duplicates
    improvements = list(dict.fromkeys(improvements))
    recommendations["improvements"] = improvements

    # ─────────────────────────────────────────────
    # 6️⃣ Crop Rotation (IMPROVED)
    # ─────────────────────────────────────────────

    crop_rotation_rules = {
        "Rice": {
            "Kharif": ["Pulses", "Maize"],
            "Rabi":   ["Pulses", "Vegetables"],
            "Zaid":   ["Maize", "Pulses"],
        },
        "Maize": {
            "Kharif": ["Pulses", "Wheat"],   # ✅ IMPROVED
            "Rabi":   ["Pulses"],
            "Zaid":   ["Pulses", "Vegetables"],
        },
        "Wheat": {
            "Rabi":   ["Rice", "Maize"],
            "Kharif": ["Pulses"],
        },
        "Soybean": {
            "Kharif": ["Wheat", "Chickpea"],
            "Rabi":   ["Maize"],
        }
    }

    possible_next_crops = crop_rotation_rules.get(crop, {}).get(season)

    if possible_next_crops:
        recommendations["next_crop"] = possible_next_crops[0]
    else:
        recommendations["next_crop"] = "Pulses"

    return recommendations