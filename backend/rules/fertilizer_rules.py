def get_fertilizer(crop_type, soil_type, season):
    crop_type = crop_type.lower()
    soil_type = soil_type.lower()
    season    = season.lower()

    # Default recommendation
    recommendation = {
        "name":     "General NPK (10-10-10)",
        "quantity": "40 kg per acre",
        "timing":   "After soil preparation"
    }

    # 🌾 Rice
    if crop_type == "rice":
        recommendation = {
            "name":     "Urea",
            "quantity": "50 kg per acre",
            "timing":   "20–25 days after sowing"
        }
        if soil_type in ("clay", "clayey"):      # ✅ FIXED: was == "clay"
            recommendation["quantity"] = "45 kg per acre"
        if season == "rabi":
            recommendation["quantity"] = "40 kg per acre"

    # 🌽 Maize
    elif crop_type == "maize":
        recommendation = {
            "name":     "DAP",
            "quantity": "60 kg per acre",
            "timing":   "Basal application before sowing"
        }
        if soil_type == "sandy":
            recommendation["quantity"] = "70 kg per acre"
            recommendation["timing"]   = "Split: half basal, half at knee-height stage"

    # 🌾 Wheat
    elif crop_type == "wheat":
        recommendation = {
            "name":     "Urea + DAP",
            "quantity": "55 kg per acre",
            "timing":   "Basal DAP at sowing; Urea top-dress at crown root stage"
        }
        if soil_type == "sandy":
            recommendation["quantity"] = "60 kg per acre"
        if season == "kharif":
            recommendation["timing"] = "Apply early; watch for leaching on sandy soils"

    # 🎋 Sugarcane
    elif crop_type == "sugarcane":
        recommendation = {
            "name":     "NPK (12-32-16) + Urea",
            "quantity": "100 kg per acre",
            "timing":   "Split into 3 doses: planting, 2 months, 4 months after planting"
        }
        if soil_type == "loamy":
            recommendation["quantity"] = "90 kg per acre"

    # 🌿 Cotton
    elif crop_type == "cotton":
        recommendation = {
            "name":     "NPK (20-20-0) + Potash",
            "quantity": "75 kg per acre",
            "timing":   "Basal at sowing; top-dress at squaring stage"
        }
        if season == "kharif":
            recommendation["timing"] = "Apply before first rain; repeat at boll formation"

    # 🥔 Potato
    elif crop_type == "potato":
        recommendation = {
            "name":     "NPK (10-26-26)",
            "quantity": "80 kg per acre",
            "timing":   "At planting time; apply Urea top-dress at tuber initiation"
        }
        if soil_type in ("clay", "clayey"):      # ✅ FIXED: was == "clay"
            recommendation["quantity"] = "70 kg per acre"

    # 🌱 Pulses / Soybean / Chickpea / Mustard
    elif crop_type in ("pulses", "chickpea", "soybean", "mustard"):
        recommendation = {
            "name":     "DAP + Rhizobium inoculant",
            "quantity": "25 kg per acre",
            "timing":   "Seed treatment + basal DAP at sowing"
        }

    return recommendation