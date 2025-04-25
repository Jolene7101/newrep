"""
Location detection utilities for fireproofing lead scraping.

Provides functions to extract US state information from text.
"""
import re
from typing import Optional, Dict, List

# Map of US state abbreviations to full names
US_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
}

# Create a reverse mapping from state name to abbreviation
STATE_ABBREVS = {v.lower(): k for k, v in US_STATES.items()}

# Common descriptive patterns that might indicate a state reference
STATE_PATTERNS = [
    r'\bin\s+([A-Z]{2})\b',                      # "in TX"
    r'\bin\s+([A-Za-z]+),\s+([A-Z]{2})\b',       # "in Austin, TX"
    r'\b([A-Za-z\s]+),\s+([A-Z]{2})\b',          # "Austin, TX"
    r'\blocated\s+in\s+([A-Za-z\s]+)\b',         # "located in Texas"
    r'\b(project|building|facility)\s+in\s+([A-Za-z\s]+)\b',  # "project in Texas"
    r'\b([A-Z]{2})\s+project\b'                  # "TX project"
]

# Default project type patterns (can be overridden)
DEFAULT_PROJECT_TYPES = {
    'hospital': [r'\bhospital\b', r'\bmedical center\b', r'\bhealthcare\b'],
    'tower': [r'\btower\b', r'\bskyscraper\b', r'\bhigh-rise\b'],
    'data_center': [r'\bdata center\b', r'\bdatacenter\b', r'\bserver\b'],
    'multi_story': [r'\b(\d+)\s+stor(y|ies)\b', r'\bover\s+(\d+)\s+stor(y|ies)\b'],
    'large_area': [r'\b(\d+),?(\d+)?\s+(sq\.?\s*ft|square\s+feet|SF)\b'],
    'high_value': [r'\$(\d+\.?\d*)\s*million\b', r'\$(\d+\.?\d*)\s*billion\b']
}

# Active project types (can be updated at runtime)
PROJECT_TYPES = DEFAULT_PROJECT_TYPES.copy()


def extract_state(text: str) -> Optional[str]:
    """
    Extract state information from text using regex patterns.
    
    Args:
        text: Text to analyze for state references
        
    Returns:
        Two-letter state code if found, None otherwise
    """
    if not text:
        return None
        
    text = text.strip()
    
    # Direct match for state abbreviation patterns
    for pattern in STATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns with multiple capture groups
                    for group in match:
                        # Check if it's a state abbreviation
                        if group.upper() in US_STATES:
                            return group.upper()
                        # Check if it's a state name
                        elif group.lower() in STATE_ABBREVS:
                            return STATE_ABBREVS[group.lower()]
                else:
                    # Single capture group
                    if match.upper() in US_STATES:
                        return match.upper()
                    elif match.lower() in STATE_ABBREVS:
                        return STATE_ABBREVS[match.lower()]
    
    # If no direct patterns matched, search for full state names
    for abbr, name in US_STATES.items():
        if re.search(r'\b' + re.escape(name) + r'\b', text, re.IGNORECASE):
            return abbr
    
    return None


def detect_project_type(text: str) -> List[str]:
    """
    Detect possible project types from text.
    
    Args:
        text: Text to analyze for project type mentions
        
    Returns:
        List of detected project types
    """
    if not text:
        return []
        
    text = text.strip()
    found_types = []
    
    for project_type, patterns in PROJECT_TYPES.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_types.append(project_type)
                break  # Only add each type once
                
    return found_types
