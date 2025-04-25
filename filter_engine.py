def filter_leads(projects, user_filters):
    import re
    filtered = []
    
    # Get states from user filters as a list of abbreviations
    states_str = user_filters.get("states", "")
    state_filters = [s.strip().upper() for s in states_str.split(",") if s.strip()]
    
    # Get keywords
    keywords = [kw.strip().lower() for kw in user_filters.get("keywords", "").split(",")]

    # State abbreviation patterns
    state_patterns = {
        abbr: re.compile(r"\b" + abbr + r"\b") for abbr in state_filters
    }
    
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
        if abbr in state_names:
            state_patterns[abbr + "_name"] = re.compile(r"\b" + state_names[abbr] + r"\b", re.IGNORECASE)

    for proj in projects:
        desc = proj.get("description", "")
        desc_lower = desc.lower()
        
        # Check for keywords match
        matches_keyword = any(kw in desc_lower for kw in keywords if kw)
        
        # Check for state match
        matches_state = False
        if state_filters:  # Only check if states were specified
            for abbr in state_filters:
                # Check for state abbreviation
                if state_patterns[abbr].search(desc):
                    matches_state = True
                    break
                    
                # Check for full state name
                if abbr + "_name" in state_patterns and state_patterns[abbr + "_name"].search(desc):
                    matches_state = True
                    break
        else:
            # If no states specified, consider it a match
            matches_state = True
            
        # If either keyword or state matches, include the project
        if matches_keyword and matches_state:
            filtered.append(proj)

    return filtered