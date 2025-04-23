import re

def parse_valuation_and_stories(text):
    valuation = 0
    stories = 0

    # Valuation patterns
    val_match = re.search(r"(\$|USD)?\s?([\d,]+)(\s?million)?", text.lower())
    if val_match:
        amount = val_match.group(2).replace(",", "")
        valuation = int(amount)
        if "million" in val_match.group(3) or (val_match.group(1) == "$" and len(amount) <= 3):
            valuation *= 1_000_000

    # Story patterns
    story_match = re.search(r"(\d+)\s?(story|floor|levels?)", text.lower())
    if story_match:
        stories = int(story_match.group(1))

    return valuation, stories