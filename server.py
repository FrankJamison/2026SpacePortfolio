import re
import csv
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

@app.post("/submit_form")
def submit_form():
    try:
        data = request.form.to_dict()
        write_to_file(data)
        write_to_csv(data)
    except Exception as e:
        return (f"Did not save to database: {e}", 500)

    return redirect(url_for("page", page_name="thankyou"))