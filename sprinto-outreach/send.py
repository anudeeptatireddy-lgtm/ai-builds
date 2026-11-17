import smtplib
from email.message import EmailMessage
from pathlib import Path
import os
import config


def send(domain, subject, body):
    if config.OFFLINE:
        Path("outbox").mkdir(exist_ok=True)
        Path(f"outbox/{domain}.txt").write_text(f"To: {config.TO_ADDRESS}\nSubject: {subject}\n\n{body}\n")
        return "written to outbox/"
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not password:
        raise RuntimeError("GMAIL_APP_PASSWORD is not set")
    msg = EmailMessage()
    msg["To"], msg["From"], msg["Subject"] = config.TO_ADDRESS, config.TO_ADDRESS, subject
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(config.TO_ADDRESS, password)
        s.send_message(msg)
    return "sent"
