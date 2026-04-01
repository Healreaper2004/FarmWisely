from datetime import datetime, timezone
import uuid

# ── Unit normalization ───────────────────────────────────────────
def normalize_water(water_value, unit="mm"):
    """
    Converts water into mm (standard unit)

    1 mm over 1 acre ≈ 4.046 m³
    """
    try:
        water_value = float(water_value)
    except:
        return 0

    if unit == "m3":
        return water_value / 4.046   # m³ → mm

    return water_value


# ── Main builder ─────────────────────────────────────────────────
def build_raw_submission(data: dict) -> dict:
    """
    Wraps raw farmer input for private storage.
    Ensures:
    - unit consistency
    - safe numeric values
    """

    # Normalize water BEFORE storing
    water = normalize_water(data.get("Water_Usage", 0), unit="mm")

    clean_data = {
        "Crop_Type":       data.get("Crop_Type"),
        "Soil_Type":       data.get("Soil_Type"),
        "Irrigation_Type": data.get("Irrigation_Type"),
        "Season":          data.get("Season"),
        "Farm_Area":       float(data.get("Farm_Area", 0)),
        "CSFI":            float(data.get("CSFI", 0)),
        "Pesticide_Used":  float(data.get("Pesticide_Used", 0)),
        "Water_Usage":     water   # ALWAYS mm
    }

    return {
        "submission_id": f"RS-{uuid.uuid4().hex[:8]}",
        "input":          clean_data,
        "submitted_at":   datetime.now(timezone.utc).isoformat(),
        "privacy_level":  "private"
    }