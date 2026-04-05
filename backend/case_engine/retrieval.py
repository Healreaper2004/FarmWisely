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

    # 🔥 NEW: feedback impact
    feedback = db_case.get("feedback", {})

    if feedback.get("useful") == True:
        score += 2

    if feedback.get("rating"):
        score += feedback["rating"] * 0.5

    return score


def get_top_cases(input_case, cases, top_k=3):
    scored = []

    for case in cases:
        sim = calculate_similarity(input_case, case)
        yield_score = case.get("outcome", {}).get("yield", 0)

        scored.append((sim, yield_score, case))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    return [c[2] for c in scored[:top_k] if c[0] > 0]