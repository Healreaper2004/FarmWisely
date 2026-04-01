def get_nutrient_advisory(crop_type, csfi):
    crop = crop_type.lower()

    # ─────────────────────────────────────────────
    # 🌾 BASE NPK (MACRO)
    # ─────────────────────────────────────────────
    macro = {
        "N (Nitrogen)": "Essential for vegetative growth",
        "P (Phosphorus)": "Root development & early growth",
        "K (Potassium)": "Disease resistance & grain quality"
    }

    # ─────────────────────────────────────────────
    # 🌿 SECONDARY NUTRIENTS
    # ─────────────────────────────────────────────
    secondary = {
        "Ca (Calcium)": "Cell wall strength & root health",
        "Mg (Magnesium)": "Chlorophyll formation",
        "S (Sulphur)": "Protein synthesis"
    }

    # ─────────────────────────────────────────────
    # 🔬 MICRONUTRIENTS (CROP-WISE)
    # ─────────────────────────────────────────────
    micro = {
        "rice": {
            "Zn": "5–10 kg/acre (Zinc sulphate)",
            "Fe": "Foliar spray if deficiency",
            "Cu": "Rarely required",
            "Mn": "Apply if deficiency in alkaline soils",
            "B": "1–2 kg/acre (optional)",
            "Mo": "Usually sufficient in soil"
        },
        "wheat": {
            "Zn": "5 kg/acre",
            "Fe": "Spray if chlorosis",
            "Cu": "Rare",
            "Mn": "Sometimes needed",
            "B": "Low requirement",
            "Mo": "Minimal"
        },
        "maize": {
            "Zn": "5 kg/acre",
            "Fe": "Spray if deficiency",
            "Cu": "Low requirement",
            "Mn": "Moderate importance",
            "B": "1 kg/acre",
            "Mo": "Minimal"
        },
        "cotton": {
            "Zn": "5 kg/acre",
            "Fe": "Foliar spray",
            "Cu": "Low",
            "Mn": "Moderate",
            "B": "1–2 kg/acre (important)",
            "Mo": "Minimal"
        }
    }

    crop_micro = micro.get(crop, {})

    # ─────────────────────────────────────────────
    # 🧠 SMART CSFI INTERPRETATION
    # ─────────────────────────────────────────────
    if csfi < 0.4:
        status = "Low fertility — Apply all macro, secondary and micronutrients"
    elif csfi < 0.65:
        status = "Moderate fertility — Focus on balanced NPK + Zn + B"
    else:
        status = "Good fertility — Maintain NPK; micronutrients only if deficiency appears"

    # ─────────────────────────────────────────────
    # FINAL OUTPUT
    # ─────────────────────────────────────────────
    return {
        "macronutrients": macro,
        "secondary_nutrients": secondary,
        "micronutrients": crop_micro,
        "soil_status": status
    }