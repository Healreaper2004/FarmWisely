from flask import Flask, request, jsonify, send_from_directory
from backend.services.recommendation_service import get_recommendation
from flask_cors import CORS
import joblib
import pandas as pd
import os

# ── sklearn version shim ────────────────────────────────────────────────────
try:
    import sklearn.compose._column_transformer as _ct
    if not hasattr(_ct, "_RemainderColsList"):
        class _RemainderColsList(list):
            def __init__(self, lst, future_dtype=None,
                         warning_was_emitted=False, warning_enabled=False):
                super().__init__(lst)
                self.future_dtype = future_dtype
                self.warning_was_emitted = warning_was_emitted
                self.warning_enabled = warning_enabled
        _ct._RemainderColsList = _RemainderColsList
except Exception:
    pass

from backend.rules.fertilizer_rules import get_fertilizer
from backend.rules.recommendations import get_recommendations
from backend.case_engine.case_builder import build_case
from backend.services.metrics import compute_metrics
from backend.services.raw_submission_service import build_raw_submission
from db.mongo import cases_collection, raw_collection

app = Flask(__name__)
CORS(app)

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")  # ../frontend relative to backend/

# ── Load ML model ───────────────────────────────────────────────────────────
pipeline = joblib.load(os.path.join(BASE_DIR, "yield_model.pkl"))

# ── Constants ───────────────────────────────────────────────────────────────
PESTICIDE_MAP = {"low": 0.5, "medium": 1.5, "high": 2.5}

VALID_CROPS      = {"rice", "wheat", "maize", "soybean"}
VALID_IRRIGATION = {"drip", "manual", "rainfed"}
VALID_SOIL       = {"sandy", "clayey", "loamy", "silty"}
VALID_SEASONS    = {"kharif", "rabi", "zaid"}

SOIL_TITLE_MAP = {
    "clay":   "Clayey",
    "clayey": "Clayey",
    "sandy":  "Sandy",
    "loamy":  "Loamy",
    "silty":  "Silty"
}


# ── Helpers ─────────────────────────────────────────────────────────────────
def parse_pesticide(value) -> float:
    if isinstance(value, str):
        mapped = PESTICIDE_MAP.get(value.lower())
        if mapped is None:
            raise ValueError(f"pesticide_used must be Low/Medium/High (got '{value}')")
        return mapped
    return float(value)


def normalize_input(data):
    return {
        "crop_type":       str(data["crop_type"]).lower(),
        "soil_type":       str(data["soil_type"]).lower(),
        "irrigation_type": str(data["irrigation_type"]).lower(),
        "season":          str(data["season"]).lower(),
    }


# ── Frontend serving (for deployment — serves index.html + static files) ────
@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    # API routes are handled by their own decorators above this catch-all
    return send_from_directory(FRONTEND_DIR, path)

# ── Health check ────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "FarmWisely 🌱"})


# ── Prediction endpoint ─────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # 1️⃣ Required fields
    required_fields = [
        "crop_type", "soil_type", "irrigation_type", "season",
        "farm_area", "csfi", "pesticide_used", "water_usage"
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # 2️⃣ Normalize
    norm = normalize_input(data)

    # 3️⃣ Validate categories
    errors = []
    if norm["crop_type"]       not in VALID_CROPS:
        errors.append(f"Invalid crop_type '{data['crop_type']}'")
    if norm["irrigation_type"] not in VALID_IRRIGATION:
        errors.append(f"Invalid irrigation_type '{data['irrigation_type']}'")
    if norm["soil_type"]       not in VALID_SOIL:
        errors.append(f"Invalid soil_type '{data['soil_type']}'")
    if norm["season"]          not in VALID_SEASONS:
        errors.append(f"Invalid season '{data['season']}'")
    if errors:
        return jsonify({"error": "Invalid category values", "details": errors}), 400

    try:
        pesticide_numeric = parse_pesticide(data["pesticide_used"])

        csfi_value = float(data["csfi"])
        if not (0.0 <= csfi_value <= 1.0):
            raise ValueError("CSFI must be between 0 and 1")

        farm_area   = float(data["farm_area"])
        water_usage = float(data["water_usage"])

        soil_final = SOIL_TITLE_MAP.get(norm["soil_type"], norm["soil_type"].title())

        input_case = {
            "crop": norm["crop_type"].title(),
            "soil": soil_final,
            "season": norm["season"].title(),
            "irrigation": norm["irrigation_type"].title()
        }

        cbr_result = get_recommendation(input_case)

        if cbr_result["type"] == "CBR":
            cbr_data = cbr_result
        else:
            cbr_data = None

        input_df = pd.DataFrame([{
            "Crop_Type":       norm["crop_type"].title(),
            "Irrigation_Type": norm["irrigation_type"].title(),
            "Soil_Type":       soil_final,
            "Season":          norm["season"].title(),
            "Farm_Area":       farm_area,
            "CSFI":            csfi_value,
            "Pesticide_Used":  pesticide_numeric,
            "Water_Usage":     water_usage
        }])

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid value: {str(e)}"}), 400

    # 5️⃣ Prediction
    predicted_yield = round(float(pipeline.predict(input_df)[0]), 2)

    # 6️⃣ Fertilizer recommendation
    fertilizer = get_fertilizer(
        crop_type=norm["crop_type"],
        soil_type=soil_final,
        season=norm["season"],
        csfi=csfi_value,
        irrigation_type=norm["irrigation_type"]
    )

    # 7️⃣ Metrics
    metrics = compute_metrics(
        input_data={
            "Water_Usage":    water_usage,
            "CSFI":           csfi_value,
            "Pesticide_Used": pesticide_numeric,
            "Farm_Area":      farm_area
        },
        predicted_yield=predicted_yield
    )

    # 8️⃣ Recommendations
    recommendations = get_recommendations(
        data={
            "crop_type":       norm["crop_type"].title(),
            "soil_type":       soil_final,
            "irrigation_type": norm["irrigation_type"].title(),
            "season":          norm["season"].title()
        },
        predicted_yield=predicted_yield,
        fertilizer=fertilizer,
        metrics=metrics,
        csfi=csfi_value   
    )

    # 9️⃣ Case building
    case = build_case(
        data=data,
        predicted_yield=predicted_yield,
        recommendations=recommendations,
        metrics=metrics
    )

    # 🔐 Store raw submission
    raw_doc = build_raw_submission(data)
    raw_collection.insert_one(raw_doc)

    return jsonify({
        "type": "HYBRID",
        "predicted_yield": predicted_yield,
        "yield_unit":      "tons",
        "metrics":         metrics,
        "recommendations": recommendations,
        "case_id":         case["case_id"],
        "cbr": cbr_data   
    })

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.json

    case_id = data.get("case_id")
    useful  = data.get("useful")
    rating  = data.get("rating")

    if not case_id:
        return jsonify({"error": "case_id required"}), 400

    # ✅ Build update fields safely
    update_fields = {}

    if useful is not None:
        update_fields["feedback.useful"] = useful

    if rating is not None:
        update_fields["feedback.rating"] = rating

    # ❗ If nothing to update
    if not update_fields:
        return jsonify({"error": "No feedback provided"}), 400

    # ✅ Update MongoDB
    result = cases_collection.update_one(
        {"case_id": case_id},
        {"$set": update_fields}
    )

    # ❗ If case not found
    if result.matched_count == 0:
        return jsonify({"error": "Case not found"}), 404

    return jsonify({"message": "Feedback saved successfully"})

# ── Cases endpoint ──────────────────────────────────────────────────────────
@app.route("/cases", methods=["GET"])
def get_cases():
    crop    = request.args.get("crop")
    season  = request.args.get("season")
    soil    = request.args.get("soil")
    problem = request.args.get("problem")

    try:
        page  = max(1, int(request.args.get("page",  1)))
        limit = min(50, max(1, int(request.args.get("limit", 10))))
    except ValueError:
        return jsonify({"error": "page and limit must be integers"}), 400

    query = {}
    if crop:    query["context.crop"]   = {"$regex": crop,    "$options": "i"}
    if season:  query["context.season"] = {"$regex": season,  "$options": "i"}
    if soil:    query["context.soil"]   = {"$regex": soil,    "$options": "i"}
    if problem: query["problem"]        = {"$regex": problem, "$options": "i"}

    skip  = (page - 1) * limit
    total = cases_collection.count_documents(query)
    cursor = cases_collection.find(query, {"_id": 0}) \
        .skip(skip).limit(limit).sort("created_at", -1)

    return jsonify({
        "total":  total,
        "page":   page,
        "limit":  limit,
        "pages":  (total + limit - 1) // limit,
        "cases":  list(cursor)
    })


# ── Stats endpoint ──────────────────────────────────────────────────────────
@app.route("/cases/stats", methods=["GET"])
def case_stats():
    total = cases_collection.count_documents({})

    by_crop = list(cases_collection.aggregate([
        {"$group": {
            "_id":       "$context.crop",
            "count":     {"$sum": 1},
            "avg_yield": {"$avg": "$outcome.predicted_yield"},
            "avg_wpi":   {"$avg": "$metrics.WPI"},
            "avg_srs":   {"$avg": "$metrics.SRS"}
        }},
        {"$sort": {"count": -1}}
    ]))

    by_problem = list(cases_collection.aggregate([
        {"$group": {"_id": "$problem", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))

    return jsonify({
        "total_cases": total,
        "by_crop":     by_crop,
        "by_problem":  by_problem
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)