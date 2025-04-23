import requests

def send_email(to_email, subject, text, mailgun_api_key, domain):
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", mailgun_api_key),
        data={"from": f"Hot Project Detector <mailgun@{domain}>",
              "to": [to_email],
              "subject": subject,
              "text": text}
    )