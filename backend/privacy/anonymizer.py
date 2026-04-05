"""
anonymizer.py
Privacy-preserving anonymization for FarmWisely (CBR + ML ready)

Enhancements:
  - Compatible with case-based reasoning (CBR)
  - Stronger quasi-identifier protection
  - Region generalization
  - Unified anonymization pipeline
"""

# ── Suppression thresholds ──────────────────────────────────────────────────
SUPPRESSION_RULES = {
    "farm_area":      (0.1,   50.0),
    "csfi":           (0.0,    1.0),
    "pesticide_used": (0.0,    3.0),
    "water_usage":    (300.0, 2000.0),
}

SUPPRESSED = "suppressed"

# ── Explicit identifiers ──────────────────────────────────────────────────
EXPLICIT_IDENTIFIERS = {
    "name", "farmer_name", "full_name",
    "phone", "mobile", "contact",
    "email",
    "address", "village", "district", "taluk",
    "gps_lat", "gps_lng", "latitude", "longitude", "exact_location",
    "aadhar", "voter_id", "id", "farmer_id",
}

# ── Helper: bucket mapping ─────────────────────────────────────────────────
def _bucket(value: float, breakpoints: list, labels: list) -> str:
    for bp, label in zip(breakpoints, labels):
        if value <= bp:
            return label
    return labels[-1]


# ── Generalisation functions ───────────────────────────────────────────────
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
            "poor",
            "moderate",
            "good",
            "excellent"
        ]
    )


def _generalise_pesticide(kg: float) -> str:
    return _bucket(
        kg,
        [0.5, 1.5, 3.0],
        [
            "minimal",
            "low",
            "moderate",
            "high"
        ]
    )


def _generalise_water(mm: float) -> str:
    return _bucket(
        mm,
        [500, 1000, 1500, 2000],
        [
            "very low",
            "low",
            "moderate",
            "high",
            "very high"
        ]
    )


def _generalise_region(region: str) -> str:
    """
    Generalize location to prevent re-identification
    Example:
      "Chennai Rural" → "Tamil Nadu Region"
    """
    if not region:
        return "unknown region"
    
    return region.split()[0] + " Region"


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
            except:
                result[field] = SUPPRESSED

    return result


# ── Step 3: Generalise values ──────────────────────────────────────────────
def _generalise(data: dict) -> dict:
    anon = {}

    # Core context (CBR compatible)
    anon["context"] = {
        "crop": data.get("crop_type", "unknown"),
        "soil": data.get("soil_type", "unknown"),
        "season": data.get("season", "unknown"),
        "irrigation": data.get("irrigation_type", "unknown"),
        "region": _generalise_region(data.get("region"))
    }

    # Helper
    def _safe(field, fn):
        val = data.get(field)

        if val is None:
            return "not provided"
        if val == SUPPRESSED:
            return SUPPRESSED
        
        try:
            return fn(float(val))
        except:
            return SUPPRESSED

    anon["farm_size_bucket"] = _safe("farm_area", _generalise_farm_area)
    anon["csfi_bucket"] = _safe("csfi", _generalise_csfi)
    anon["pesticide_bucket"] = _safe("pesticide_used", _generalise_pesticide)
    anon["water_bucket"] = _safe("water_usage", _generalise_water)

    return anon


# ── Optional: k-anonymity placeholder (for future extension) ───────────────
def enforce_k_anonymity(cases, k=3):
    """
    Ensures at least k similar records exist before storing.
    (Currently placeholder for research/demo)
    """
    return len(cases) >= k


# ── Public API ─────────────────────────────────────────────────────────────
def anonymize(raw_data: dict) -> dict:
    """
    Full anonymization pipeline
    """

    data = _strip(raw_data)
    data = _suppress(data)
    anon = _generalise(data)

    anon["_privacy"] = {
        "identifiers_removed": True,
        "quasi_identifiers_generalised": True,
        "outliers_suppressed": True,
        "region_generalized": True,
        "method": "strip + suppress + range-bucketing + region masking"
    }

    return anon