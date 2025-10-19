from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_HOST_USER,
    MAIL_PASSWORD=settings.EMAIL_HOST_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_STARTTLS=settings.EMAIL_USE_TLS,
    MAIL_SSL_TLS=settings.EMAIL_USE_SSL,
    USE_CREDENTIALS=True,
)

fm = FastMail(conf)

async def send_email(recipient: str, subject: str, body: str, html: bool = False):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype="html" if html else "plain",  # OR "html"
    )
    await fm.send_message(message)

async def send_activation_email(email: str, token: str):
    """
    Отправка письма активации.
    """
    activation_link = f"{settings.FRONTEND_URL}/auth/activate/{token}"
    body = f"""
    <h3>Здравствуйте!</h3>
    <p>Пожалуйста, подтвердите свой аккаунт, перейдя по ссылке:</p>
    <p><a href="{activation_link}">{activation_link}</a></p>
    """
    await send_email(email, "Activate your account", body, html=True)


async def send_password_reset_email(email: str, token: str):
    """
    Отправка письма для сброса пароля.
    """
    reset_link = f"{settings.FRONTEND_URL}/password-reset/{token}"
    body = f"""
    <h3>Здравствуйте!</h3>
    <p>Чтобы сбросить пароль, перейдите по ссылке ниже:</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    """
    await send_email(email, "Password reset", body, html=True)
