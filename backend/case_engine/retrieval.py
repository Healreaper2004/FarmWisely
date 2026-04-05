def calculate_similarity(input_case, db_case):
    score = 0
    
    if input_case["crop"] == db_case["context"]["crop"]:
        score += 3
    if input_case["soil"] == db_case["context"]["soil"]:
        score += 2
    if input_case["season"] == db_case["context"]["season"]:
        score += 2
    if input_case["irrigation"] == db_case["context"]["irrigation"]:
        score += 1
        
    return score


def get_top_cases(input_case, cases):
    scored = []
    
    for case in cases:
        sim = calculate_similarity(input_case, case)
        yield_score = case["outcome"]["yield"]
        scored.append((sim, yield_score, case))
    
    scored.sort(reverse=True)
    
    return [c[2] for c in scored[:3]]