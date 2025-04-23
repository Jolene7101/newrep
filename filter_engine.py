def filter_leads(projects, user_filters):
    from parser import parse_valuation_and_stories
    filtered = []
    min_val = user_filters.get("valuation_min", 0)
    min_stories = user_filters.get("min_stories", 0)
    keywords = [kw.strip().lower() for kw in user_filters.get("keywords", "").split(",")]

    for proj in projects:
        desc = proj.get("description", "").lower()
        matches_keyword = any(kw in desc for kw in keywords if kw)
        valuation, stories = parse_valuation_and_stories(desc)
        matches_value = valuation >= min_val if valuation else False
        matches_stories = stories >= min_stories if stories else False
        if matches_keyword or matches_value or matches_stories:
            filtered.append(proj)

    return filtered