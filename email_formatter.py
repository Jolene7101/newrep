def format_email_body(user_name, projects):
    if not projects:
        return f"Hi {user_name},\n\nNo matching projects were found for your filters today.\n\nBest,\nHot Project Detector"

    body = f"Hi {user_name},\n\nHere are your matched leads for today:\n"
    for p in projects:
        title = p.get("title", "Untitled")
        source = p.get("source", "Unknown")
        body += f"\n• {title} ({source})"
    body += "\n\nBest,\nHot Project Detector"
    return body