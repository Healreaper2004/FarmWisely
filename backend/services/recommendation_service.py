from db.mongo import get_cases_collection
from backend.case_engine.retrieval import get_top_cases

def get_recommendation(input_case):
    collection = get_cases_collection()
    
    cases = list(collection.find({}))
    
    similar_cases = get_top_cases(input_case, cases)
    
    if similar_cases:
        return {
            "type": "CBR",
            "cases_used": len(similar_cases),
            "recommendation": similar_cases[0]["solution"],
            "reason": "Based on similar past cases"
        }
    
    return {"type": "ML_FALLBACK"}