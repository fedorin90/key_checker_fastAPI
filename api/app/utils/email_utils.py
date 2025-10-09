import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_activation_email(email: str, token: str):
    activation_link = f"{settings.FRONTEND_URL}/auth/activate/{token}"
    msg = MIMEText(f"Hello! Please confirm your account: {activation_link}", "plain", "utf-8")
    msg["Subject"] = "Activate your account"
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = email

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
