def filter_leads(projects, user_filters):
    filtered = []
    min_val = user_filters.get("valuation_min", 0)
    min_stories = user_filters.get("min_stories", 0)
    keywords = [kw.strip().lower() for kw in user_filters.get("keywords", "").split(",")]

    for proj in projects:
        desc = proj.get("description", "").lower()
        if all(kw in desc for kw in keywords):
            # Fake parse for valuation/story count (demo only)
            if "million" in desc or "$" in desc or "story" in desc:
                filtered.append(proj)

    return filtered