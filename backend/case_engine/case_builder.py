import uuid
from datetime import datetime, timezone
from db.mongo import cases_collection
from backend.privacy.anonymizer import anonymize


def infer_problem(predicted_yield):
    """Yield is in metric tons."""
    if predicted_yield < 3:
        return "Low yield"
    elif predicted_yield < 6:
        return "Moderate yield"
    else:
        return "Yield optimization"


def build_case(data, predicted_yield, recommendations, metrics):
    """
    Anonymizes raw farmer data and builds + stores a CASE object.
    The stored case never contains exact farm_area, csfi, pesticide,
    water_usage values — only generalised range buckets.
    """

    # 🔐 Anonymize raw input before building the case
    anon = anonymize(data)

    case = {
        "case_id": f"FW-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6]}",

        # Context uses ANONYMISED fields only
        "context": {
            "crop":              anon.get("crop_type"),
            "soil":              anon.get("soil_type"),
            "season":            anon.get("season"),
            "irrigation":        anon.get("irrigation_type"),
            "farm_size_range":   anon.get("farm_area_range"),
            "csfi_range":        anon.get("csfi_range"),        # ✅ FIXED: was "fertilizer_range"
            "pesticide_range":   anon.get("pesticide_range"),
            "water_usage_range": anon.get("water_usage_range"),
        },

        "problem": infer_problem(predicted_yield),

        "solution": {
            "fertilizer":          recommendations["fertilizer"],
            "irrigation_strategy": recommendations["water_usage"],
            "improvements":        recommendations.get("improvements", []),
            "next_crop":           recommendations.get("next_crop"),
        },

        "outcome": {
            "predicted_yield": predicted_yield,
            "unit": "tons",
            "source": "AI prediction"
        },

        "metrics": {
            "WPI": metrics["WPI"],
            "NES": metrics["NES"],
            "III": metrics["III"],
            "SRS": metrics["SRS"]
        },

        "privacy": anon.get("_privacy", {
            "identifiers_removed": True,
            "quasi_identifiers_generalised": True,
            "outliers_suppressed": True,
        }),

        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Save to MongoDB — convert _id to string immediately to avoid serialization errors
    result = cases_collection.insert_one(dict(case))
    case["_id"] = str(result.inserted_id)

    return case

    