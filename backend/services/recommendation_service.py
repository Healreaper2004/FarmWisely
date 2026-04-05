from db.mongo import get_cases_collection
from backend.case_engine.retrieval import get_top_cases

def get_recommendation(input_case):
    collection = get_cases_collection()

    cases = list(collection.find({}))

    similar_cases = get_top_cases(input_case, cases)

    if similar_cases:
        best = similar_cases[0]   # ✅ DEFINE IT HERE

        return {
            "type": "CBR",
            "cases_used": len(similar_cases),
            "recommendation": best.get("solution", {}),
            "reason": "Based on similar past farmer cases",
            "case_id": best.get("case_id")   # ✅ NOW SAFE
        }

    return {"type": "ML_FALLBACK"}