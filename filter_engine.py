def filter_leads(projects, user_filters):
    import re
    filtered = []
    
    # Get states from user filters as a list of abbreviations
    # Ensure states_str is a string to avoid 'int' object has no attribute 'split' error
    states_str = str(user_filters.get("states", ""))
    state_filters = [s.strip().upper() for s in states_str.split(",") if s.strip()]
    
    # Get keywords
    keywords = [kw.strip().lower() for kw in user_filters.get("keywords", "").split(",")]

    # State abbreviation patterns
    state_patterns = {}
    for abbr in state_filters:
        # Skip numeric values from old database rows that might have been converted to strings
        if abbr.isdigit():
            continue
        state_patterns[abbr] = re.compile(r"\b" + abbr + r"\b")
    
    # State full name patterns (for each abbr in filter, add its full name)
    state_names = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
        "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
        "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
        "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
        "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
        "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
        "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
    }
    
    for abbr in state_filters:
        if abbr in state_names and abbr in state_patterns:
            state_patterns[abbr + "_name"] = re.compile(r"\b" + state_names[abbr] + r"\b", re.IGNORECASE)

    for proj in projects:
        desc = proj.get("description", "")
        desc_lower = desc.lower()
        
        # Check for keywords match (OR logic - any keyword match is sufficient)
        has_any_keyword_match = False
        if keywords:  # Only check if keywords were specified
            for kw in keywords:
                if kw and kw in desc_lower:
                    has_any_keyword_match = True
                    break
        else:
            # If no keywords specified, consider it a match
            has_any_keyword_match = True
        
        # Check for state match
        matches_state = False
        if state_filters:  # Only check if states were specified
            for abbr in state_filters:
                # Skip numeric values that were converted to strings
                if abbr.isdigit():
                    continue
                    
                # Check for state abbreviation
                if abbr in state_patterns and state_patterns[abbr].search(desc):
                    matches_state = True
                    break
                    
                # Check for full state name
                if abbr + "_name" in state_patterns and state_patterns[abbr + "_name"].search(desc):
                    matches_state = True
                    break
        else:
            # If no states specified, consider it a match
            matches_state = True
            
        # If both keyword and state match, include the project
        if has_any_keyword_match and matches_state:
            filtered.append(proj)

    return filtered