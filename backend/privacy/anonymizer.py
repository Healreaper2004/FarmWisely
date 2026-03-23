"""
anonymizer.py
Privacy-preserving anonymization for FarmWisely (CSFI-based model)

Units:
  - farm_area       : acres
  - csfi            : 0–1 (Soil Fertility Index)
  - pesticide_used  : kg per season
  - water_usage     : m³ per season

Strategy:
  1. Strip       — remove explicit identifiers
  2. Suppress    — remove extreme/outlier values
  3. Generalise  — convert numbers into safe range buckets
"""

# ── Suppression thresholds ──────────────────────────────────────────────────
SUPPRESSION_RULES = {
    "farm_area":      (0.1,   50.0),
    "csfi":           (0.0,    1.0),
    "pesticide_used": (0.0,    3.0),
    "water_usage":    (50.0, 6000.0),
}

SUPPRESSED = "suppressed"

# ── Explicit identifiers to remove ──────────────────────────────────────────
EXPLICIT_IDENTIFIERS = {
    "name", "farmer_name", "full_name",
    "phone", "mobile", "contact",
    "email",
    "address", "village", "district", "taluk",
    "gps_lat", "gps_lng", "latitude", "longitude", "exact_location",
    "aadhar", "voter_id", "id", "farmer_id",
}

# ── Helper: bucket mapping ──────────────────────────────────────────────────
def _bucket(value: float, breakpoints: list, labels: list) -> str:
    for bp, label in zip(breakpoints, labels):
        if value <= bp:
            return label
    return labels[-1]


# ── Generalisation functions ────────────────────────────────────────────────
def _generalise_farm_area(acres: float) -> str:
    return _bucket(
        acres,
        [1.0, 2.0, 5.0, 10.0],
        ["<1 acre", "1–2 acres", "2–5 acres", "5–10 acres", "10+ acres"]
    )


def _generalise_csfi(csfi: float) -> str:
    return _bucket(
        csfi,
        [0.30, 0.60, 0.80],
        [
            "poor (0–0.30)",
            "moderate (0.30–0.60)",
            "good (0.60–0.80)",
            "excellent (0.80–1.0)"
        ]
    )


def _generalise_pesticide(kg: float) -> str:
    return _bucket(
        kg,
        [0.5, 1.5, 3.0],
        [
            "minimal (<0.5 kg)",
            "low (0.5–1.5 kg)",
            "moderate (1.5–3 kg)",
            "high (>3 kg)"
        ]
    )


def _generalise_water(m3: float) -> str:
    return _bucket(
        m3,
        [500, 1500, 3000, 5000],
        [
            "very low (<500 m³)",
            "low (500–1500 m³)",
            "moderate (1.5–3k m³)",
            "high (3–5k m³)",
            "very high (>5k m³)"
        ]
    )


# ── Step 1: Remove identifiers ─────────────────────────────────────────────
def _strip(data: dict) -> dict:
    return {
        k: v for k, v in data.items()
        if k.lower() not in EXPLICIT_IDENTIFIERS
    }


# ── Step 2: Suppress outliers ──────────────────────────────────────────────
def _suppress(data: dict) -> dict:
    result = dict(data)

    for field, (lo, hi) in SUPPRESSION_RULES.items():
        if field in result:
            try:
                val = float(result[field])
                if val < lo or val > hi:
                    result[field] = SUPPRESSED
            except (TypeError, ValueError):
                result[field] = SUPPRESSED

    return result


# ── Step 3: Generalise values ──────────────────────────────────────────────
def _generalise(data: dict) -> dict:
    anon = {}

    # Safe categorical fields
    for field in ("crop_type", "soil_type", "irrigation_type", "season"):
        if field in data:
            anon[field] = data[field]

    # Helper
    def _safe(field, fn, output_key):
        val = data.get(field)

        if val is None:
            anon[output_key] = "not provided"
        elif val == SUPPRESSED:
            anon[output_key] = SUPPRESSED
        else:
            try:
                anon[output_key] = fn(float(val))
            except (TypeError, ValueError):
                anon[output_key] = SUPPRESSED

    _safe("farm_area", _generalise_farm_area, "farm_area_range")
    _safe("csfi", _generalise_csfi, "csfi_range")  # ✅ NEW
    _safe("pesticide_used", _generalise_pesticide, "pesticide_range")
    _safe("water_usage", _generalise_water, "water_usage_range")

    return anon


# ── Public API ─────────────────────────────────────────────────────────────
def anonymize(raw_data: dict) -> dict:
    """
    Full anonymization pipeline

    Input  : raw farmer submission
    Output : anonymized safe case data
    """

    data = _strip(raw_data)
    data = _suppress(data)
    anon = _generalise(data)

    anon["_privacy"] = {
        "identifiers_removed": True,
        "quasi_identifiers_generalised": True,
        "outliers_suppressed": True,
        "method": "strip + suppress + range-bucketing",
    }

    return anon