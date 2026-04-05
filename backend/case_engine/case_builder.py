import uuid
from datetime import datetime, timezone
from db.mongo import get_cases_collection
from backend.privacy.anonymizer import anonymize


# ─────────────────────────────────────────────────────────────
# 🚨 NEW: Normalize water units (standard = mm)
# ─────────────────────────────────────────────────────────────
def normalize_water(water_value, unit="mm"):
    """
    Convert water to mm if needed.
    Assumes 1 acre: 1 mm ≈ 4.046 m³
    """
    try:
        water_value = float(water_value)
    except (TypeError, ValueError):
        return None

    if unit == "m3":
        return round(water_value / 4.046, 2)

    return water_value


# ─────────────────────────────────────────────────────────────
# 🚨 NEW: Irrigation validation
# ─────────────────────────────────────────────────────────────
def validate_irrigation(crop, irrigation):
    crop = str(crop).lower()
    irrigation = str(irrigation).lower()

    if crop == "rice" and irrigation == "drip":
        return "Warning: Drip irrigation is uncommon for rice. Consider flood or SRI method."

    return None


# ─────────────────────────────────────────────────────────────
def infer_problem(predicted_yield):
    """Yield is in metric tons."""
    if predicted_yield < 3:
        return "Low yield"
    elif predicted_yield < 6:
        return "Moderate yield"
    else:
        return "Yield optimization"


# ─────────────────────────────────────────────────────────────
def build_case(data, predicted_yield, recommendations, metrics):
    """
    Anonymizes raw farmer data and builds + stores a CASE object.
    Ensures:
      - Water units are standardized (mm)
      - Irrigation is validated
      - Safe handling of missing values
    """

    # ── 1. Normalize water BEFORE anonymization ───────────────
    if "water_usage" in data:
        data["water_usage"] = normalize_water(data.get("water_usage"), unit="mm")

    # ── 2. Validate irrigation ───────────────────────────────
    irrigation_warning = validate_irrigation(
        data.get("crop_type"),
        data.get("irrigation_type")
    )

    # ── 3. Anonymize input ───────────────────────────────────
    anon = anonymize(data)

    # ── 4. Build case object ─────────────────────────────────
    case = {
        "case_id": f"FW-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6]}",

        # Context (ANONYMIZED ONLY)
        "context": {
            "crop":              anon.get("crop_type"),
            "soil":              anon.get("soil_type"),
            "season":            anon.get("season"),
            "irrigation":        anon.get("irrigation_type"),
            "farm_size_range":   anon.get("farm_area_range"),
            "csfi_range":        anon.get("csfi_range"),
            "pesticide_range":   anon.get("pesticide_range"),
            "water_usage_range": anon.get("water_usage_range"),
        },

        "problem": infer_problem(predicted_yield),

        # ── 5. Solution block ────────────────────────────────
        "solution": {
            "fertilizer":          recommendations.get("fertilizer"),
            "irrigation_strategy": recommendations.get("water_usage"),
            "improvements":        recommendations.get("improvements", []),
            "next_crop":           recommendations.get("next_crop"),
        },

        # Add irrigation warning if exists
        "alerts": {
            "irrigation_warning": irrigation_warning
        } if irrigation_warning else {},

        # ── 6. Outcome ───────────────────────────────────────
        "outcome": {
            "predicted_yield": predicted_yield,
            "unit": "tons",
            "source": "AI prediction"
        },

        # ── 7. Metrics (safe access) ─────────────────────────
        "metrics": {
            "WPI": metrics.get("WPI"),
            "NES": metrics.get("NES"),
            "III": metrics.get("III"),
            "SRS": metrics.get("SRS")
        },

        # ── 8. Privacy metadata ──────────────────────────────
        "privacy": anon.get("_privacy", {
            "identifiers_removed": True,
            "quasi_identifiers_generalised": True,
            "outliers_suppressed": True,
        }),

        # ── 9. Feedback ───────────────────────────────
        "feedback": {
            "useful": None,
            "rating": None
        },

        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # ─ 10. Save to MongoDB ───────────────────────────────────
    result = cases_collection.insert_one(dict(case))
    case["_id"] = str(result.inserted_id)

    return case