from nutrient_rules import get_nutrient_advisory

def get_recommendations(data, predicted_yield, fertilizer, metrics, csfi=0.5):
    """
    Improved rule-based recommendation engine (agronomy-corrected)

    Assumptions:
      - Yield in tons (per acre or total — handled consistently upstream)
      - Water usage in mm
      - Metrics:
            WPI → kg/mm
            NES → kg yield per kg fertilizer
            III → input intensity
            SRS → 0–1 risk score
    """

    recommendations = {}

    crop       = data["crop_type"]
    irrigation = data["irrigation_type"]
    season     = data["season"]
    soil       = data["soil_type"]

    # ─────────────────────────────────────────────
    # 1️⃣ Fertilizer recommendation (already CSFI-adjusted upstream)
    # ─────────────────────────────────────────────
    recommendations["fertilizer"] = fertilizer

    # ─────────────────────────────────────────────
    # 2️⃣ Water recommendation (FIXED: agronomically correct)
    # ─────────────────────────────────────────────
    irrigation_warning = None

    if crop == "Rice":
        if irrigation == "Drip":
            # 🚨 Non-standard irrigation
            irrigation_warning = (
                "Drip irrigation is uncommon for rice. Ensure aerobic rice method is used."
            )
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
    # 3️⃣ Improvement suggestions (CSFI-aware + realistic)
    # ─────────────────────────────────────────────
    improvements = []

    # Yield interpretation (more realistic thresholds)
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
            improvements.append(
                "High yield but very low soil fertility. This is input-driven and unsustainable. Add organic matter."
            )
        elif csfi < 0.60:
            improvements.append(
                "Good yield with moderate soil fertility. Improve soil health gradually."
            )
        else:
            improvements.append("Good yield and healthy soil. Maintain current practices.")

    # CSFI-specific suggestion
    if csfi < 0.5:
        improvements.append("Improve soil fertility using compost, green manure, or biofertilisers.")

    # Irrigation efficiency
    if irrigation != "Drip":
        improvements.append("Consider drip irrigation to improve water efficiency.")

    # ─────────────────────────────────────────────
    # 4️⃣ Metric-based rules (FIXED THRESHOLDS)
    # ─────────────────────────────────────────────

    # WPI (kg/mm) — realistic threshold ~3–6
    if metrics["WPI"] < 3:
        improvements.append("Low water productivity. Optimise irrigation scheduling and reduce losses.")

    # NES (kg yield per kg fertilizer)
    if metrics["NES"] < 8:
        improvements.append("Low nutrient efficiency. Apply balanced NPK and avoid overuse of nitrogen.")

    # Input Intensity
    if metrics["III"] > 3:
        improvements.append("High input usage per acre. Reduce excessive fertiliser and pesticide use.")

    # Sustainability Risk
    if metrics["SRS"] > 0.6:
        improvements.append("Moderate to high sustainability risk. Adopt eco-friendly farming practices.")

    # Remove duplicates
    improvements = list(dict.fromkeys(improvements))
    recommendations["improvements"] = improvements

    # ─────────────────────────────────────────────
    # 5️⃣ Crop rotation (REGION-AWARE IMPROVEMENT)
    # ─────────────────────────────────────────────

    crop_rotation_rules = {
        "Rice": {
            "Kharif": ["Pulses", "Maize"],     # ✅ FIXED (removed wheat bias)
            "Rabi":   ["Pulses", "Vegetables"],
            "Zaid":   ["Maize", "Pulses"],
        },
        "Wheat": {
            "Rabi":   ["Rice", "Maize"],
            "Kharif": ["Pulses"],
            "Zaid":   ["Maize", "Vegetables"],
        },
        "Maize": {
            "Kharif": ["Wheat", "Potato"],
            "Rabi":   ["Pulses"],
            "Zaid":   ["Pulses", "Vegetables"],
        },
        "Cotton": {
            "Kharif": ["Soybean", "Pulses"],
            "Rabi":   ["Chickpea"],
        },
        "Sugarcane": {
            "Kharif": ["Wheat", "Mustard"],
            "Rabi":   ["Maize", "Pulses"],
        },
        "Potato": {
            "Rabi":   ["Maize", "Rice"],
            "Kharif": ["Wheat", "Mustard"],
        },
        "Soybean": {
            "Kharif": ["Wheat", "Chickpea"],
            "Rabi":   ["Maize"],
            "Zaid":   ["Maize", "Pulses"],
        },
    }

    possible_next_crops = crop_rotation_rules.get(crop, {}).get(season)

    if possible_next_crops:
        if soil in ("Loamy", "Clay", "Clayey") and len(possible_next_crops) > 1:
            recommendations["next_crop"] = possible_next_crops[0]
        else:
            recommendations["next_crop"] = possible_next_crops[-1]
    else:
        recommendations["next_crop"] = "Pulses"

    return recommendations