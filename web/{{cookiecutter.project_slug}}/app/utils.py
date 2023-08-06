import emails

from app.config import settings


def send_email(**kwargs):
    m = emails.Message(
        mail_from=(settings.emails_from_name, settings.emails_from_email), **kwargs
    )

    return m.send(
        smtp={
            "tls": settings.smtp_tls,
            "host": settings.smtp_host,
            "port": settings.smtp_port,
            "user": settings.smtp_user,
            "password": settings.smtp_password,
        }
    )
