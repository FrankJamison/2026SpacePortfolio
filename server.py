import re
import csv
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from flask import Flask, current_app, redirect, render_template, request, url_for
from jinja2 import TemplateNotFound

_INSTANCE_PATH = (Path(__file__).resolve().parent / "var" / "server-instance").resolve()
app = Flask(__name__, instance_path=str(_INSTANCE_PATH), instance_relative_config=True)

_SAFE_PAGE_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")


@app.get("/", defaults={"page_name": "index"})
@app.get("/<string:page_name>")
def page(page_name: str):
    if not _SAFE_PAGE_NAME.match(page_name):
        return ("Not Found", 404)

    try:
        return render_template(f"{page_name}.html")
    except TemplateNotFound:
        return ("Not Found", 404)

def write_to_file(data):
    Path(current_app.instance_path).mkdir(parents=True, exist_ok=True)
    db_path = Path(current_app.instance_path) / "database.txt"

    email = data.get("email", "")
    subject = data.get("subject", "")
    message = data.get("message", "")

    with db_path.open(mode="a", newline="", encoding="utf-8") as database1:
        writer = csv.writer(database1)
        writer.writerow([email, subject, message])

def write_to_csv(data):
    Path(current_app.instance_path).mkdir(parents=True, exist_ok=True)
    db_path = Path(current_app.instance_path) / "database.csv"

    email = data.get("email", "")
    subject = data.get("subject", "")
    message = data.get("message", "")

    with db_path.open(mode="a", newline="", encoding="utf-8") as database:
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email, subject, message])


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def send_contact_email(data):
    """Send a contact-form submission via SMTP.

    Configuration (environment variables):
    - CONTACT_SMTP_HOST (default: mail.fcjamison.com)
    - CONTACT_SMTP_PORT (default: 587)
    - CONTACT_SMTP_USER (required)
    - CONTACT_SMTP_PASSWORD (required)
    - CONTACT_MAIL_FROM (default: CONTACT_SMTP_USER)
    - CONTACT_MAIL_TO (default: CONTACT_SMTP_USER)
    - CONTACT_SMTP_USE_STARTTLS (default: true)
    """

    smtp_host = os.getenv("CONTACT_SMTP_HOST", "mail.fcjamison.com")
    smtp_port = int(os.getenv("CONTACT_SMTP_PORT", "587"))
    smtp_user = os.getenv("CONTACT_SMTP_USER")
    smtp_password = os.getenv("CONTACT_SMTP_PASSWORD")
    mail_from = os.getenv("CONTACT_MAIL_FROM") or smtp_user
    mail_to = os.getenv("CONTACT_MAIL_TO") or smtp_user
    use_starttls = _env_bool("CONTACT_SMTP_USE_STARTTLS", True)
    email_required = _env_bool("CONTACT_EMAIL_REQUIRED", False)

    if not smtp_user or not smtp_password:
        if email_required:
            raise RuntimeError(
                "SMTP not configured. Set CONTACT_SMTP_USER and CONTACT_SMTP_PASSWORD environment variables."
            )
        return False
    if not mail_from or not mail_to:
        if email_required:
            raise RuntimeError(
                "Email not configured. Set CONTACT_MAIL_FROM and CONTACT_MAIL_TO (or CONTACT_SMTP_USER)."
            )
        return False

    sender_email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "").strip() or "(no subject)"
    message = (data.get("message") or "").strip()

    remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    user_agent = request.headers.get("User-Agent", "")

    email_message = EmailMessage()
    email_message["From"] = mail_from
    email_message["To"] = mail_to
    email_message["Subject"] = f"Portfolio contact: {subject}"
    if sender_email:
        email_message["Reply-To"] = sender_email

    email_message.set_content(
        "\n".join(
            [
                "New contact form submission:",
                "",
                f"From (typed): {sender_email}",
                f"Subject: {subject}",
                "",
                "Message:",
                message,
                "",
                "---", 
                f"IP: {remote_addr}",
                f"User-Agent: {user_agent}",
            ]
        )
    )

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        server.ehlo()
        if use_starttls:
            server.starttls(context=context)
            server.ehlo()
        server.login(smtp_user, smtp_password)
        server.send_message(email_message)

    return True

@app.post("/submit_form")
def submit_form():
    data = request.form.to_dict()

    try:
        write_to_file(data)
        write_to_csv(data)
    except Exception as e:
        return (f"Did not save to database: {e}", 500)

    try:
        send_contact_email(data)
    except Exception:
        current_app.logger.exception("Contact email send failed")

    return redirect(url_for("page", page_name="thankyou"))