from jinja2 import Environment, PackageLoader, select_autoescape

from app import utils
from app.config import settings

from .celery import app

env = Environment(autoescape=select_autoescape(), loader=PackageLoader("app"))


@app.task
def send_new_account_email(to: str, username: str, password: str) -> None:
    template = env.get_template("new_account.html")

    utils.send_email(
        mail_to=to,
        subject=f"{settings.project_name} - New account for user {username}",
        html=template.render(
            link=settings.server_host,
            project_name=settings.project_name,
            username=username,
            password=password,
        ),
    )


@app.task
def send_reset_password_email(to: str, username: str, token: str) -> None:
    template = env.get_template("reset_password.html")

    utils.send_email(
        mail_to=to,
        subject=f"{settings.project_name} - Password recovery for user {username}",
        html=template.render(
            link=f"{settings.server_host}/reset-password?token={token}",
            project_name=settings.project_name,
            username=username,
            valid_hours=settings.email_reset_token_expire_hours,
        ),
    )
