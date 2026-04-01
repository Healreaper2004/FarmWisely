def get_fertilizer(crop_type, soil_type, season, csfi, irrigation_type=None):
    crop_type = crop_type.lower()
    soil_type = soil_type.lower()
    season    = season.lower()
    irrigation_type = (irrigation_type or "").lower()

    # ─────────────────────────────────────────────
    # 🔧 Helper: Adjust fertilizer using CSFI
    # ─────────────────────────────────────────────
    def adjust_quantity(base_qty):
        if csfi < 0.4:
            return int(base_qty * 1.2)
        elif csfi > 0.75:
            return int(base_qty * 0.85)
        return int(base_qty)

    # ─────────────────────────────────────────────
    # 🌾 DEFAULT
    # ─────────────────────────────────────────────
    recommendation = {
        "name":     "General NPK (10-10-10)",
        "quantity": f"{adjust_quantity(40)} kg per acre",
        "timing":   "After soil preparation"
    }

    # ─────────────────────────────────────────────
    # 🌾 RICE (FINAL FIXED)
    # ─────────────────────────────────────────────
    if crop_type == "rice":

        dap   = adjust_quantity(50)
        urea  = adjust_quantity(100)
        mop   = adjust_quantity(25)

        recommendation = {
            "name": "Urea + DAP + MOP",
            "quantity": {
                "DAP":  f"{dap} kg/acre (basal)",
                "Urea": f"{urea} kg/acre (split: basal, tillering, panicle)",
                "MOP":  f"{mop} kg/acre"
            },
            "timing": "Basal + Tillering + Panicle Initiation",
            "note": "Balanced NPK improves yield and grain filling"
        }

        # 🌱 Micronutrient addition (important for rice)
        if csfi < 0.6:
            recommendation["micronutrient"] = "Apply Zinc sulphate (5–10 kg/acre)"

        # 🌾 Soil logic
        if soil_type in ("clay", "clayey"):
            recommendation["note"] += "; clay soil retains nutrients, avoid overwatering"

        # 💧 Irrigation logic (IMPROVED)
        if irrigation_type == "drip":
            recommendation["warning"] = (
                "Drip irrigation is uncommon for rice. Use frequent cycles or consider SRI method."
            )
            recommendation["adjustment"] = "Reduce water but maintain nutrient supply in splits"

    # ─────────────────────────────────────────────
    # 🌽 MAIZE
    # ─────────────────────────────────────────────
    elif crop_type == "maize":
        qty = adjust_quantity(60)

        recommendation = {
            "name":     "DAP + Urea",
            "quantity": f"{qty} kg/acre",
            "timing":   "Basal + knee-height stage",
            "note":     "Ensure nitrogen availability during rapid growth phase"
        }

        if soil_type == "sandy":
            recommendation["quantity"] = f"{adjust_quantity(70)} kg/acre"
            recommendation["note"] += "; split application recommended to reduce leaching"

    # ─────────────────────────────────────────────
    # 🌾 WHEAT
    # ─────────────────────────────────────────────
    elif crop_type == "wheat":
        qty = adjust_quantity(55)

        recommendation = {
            "name":     "Urea + DAP",
            "quantity": f"{qty} kg/acre",
            "timing":   "Basal + crown root stage",
            "note":     "Nitrogen critical at crown root initiation"
        }

        if soil_type == "sandy":
            recommendation["quantity"] = f"{adjust_quantity(60)} kg/acre"

    # ─────────────────────────────────────────────
    # 🎋 SUGARCANE
    # ─────────────────────────────────────────────
    elif crop_type == "sugarcane":
        qty = adjust_quantity(100)

        recommendation = {
            "name":     "NPK + Urea",
            "quantity": f"{qty} kg/acre",
            "timing":   "Split: planting, 2 months, 4 months",
            "note":     "Heavy feeder crop; requires consistent nutrient supply"
        }

        if soil_type == "loamy":
            recommendation["quantity"] = f"{adjust_quantity(90)} kg/acre"

    # ─────────────────────────────────────────────
    # 🌿 COTTON
    # ─────────────────────────────────────────────
    elif crop_type == "cotton":
        qty = adjust_quantity(75)

        recommendation = {
            "name":     "NPK + Potash",
            "quantity": f"{qty} kg/acre",
            "timing":   "Basal + squaring stage",
            "note":     "Potassium improves boll development"
        }

        if season == "kharif":
            recommendation["note"] += "; apply before rains and monitor runoff"

    # ─────────────────────────────────────────────
    # 🥔 POTATO
    # ─────────────────────────────────────────────
    elif crop_type == "potato":
        qty = adjust_quantity(80)

        recommendation = {
            "name":     "NPK (10-26-26) + Urea",
            "quantity": f"{qty} kg/acre",
            "timing":   "Basal + tuber initiation",
            "note":     "Phosphorus important for root/tuber formation"
        }

        if soil_type in ("clay", "clayey"):
            recommendation["quantity"] = f"{adjust_quantity(70)} kg/acre"

    # ─────────────────────────────────────────────
    # 🌱 PULSES
    # ─────────────────────────────────────────────
    elif crop_type in ("pulses", "chickpea", "soybean", "mustard"):
        qty = adjust_quantity(25)

        recommendation = {
            "name":     "DAP + Rhizobium",
            "quantity": f"{qty} kg/acre",
            "timing":   "Seed treatment + basal",
            "note":     "Biological nitrogen fixation reduces fertilizer need"
        }

    return recommendation