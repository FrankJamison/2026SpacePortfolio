# 2026 Python Portfolio (Flask)

Hi — I’m Frank Jamison. This repo is my personal portfolio site built with Python + Flask.

It’s intentionally simple and fast: a small Flask server renders HTML templates, serves a compiled front-end bundle, and includes a working contact form that writes messages to a lightweight “database” file for easy review.

- Live site: https://2026pythonportfolio.fcjamison.com/
- Local dev: http://127.0.0.1:5000/

---

## Who this is for

**Recruiters / hiring managers**
- This site is my “front door” for work: clean navigation, focused content sections, and a working contact form.
- The code is readable and intentionally small so you can quickly see my approach to shipping.

**Developers**
- The back-end is a minimal Flask app with safe routing and a tiny persistence layer.
- The front-end is a compiled static bundle (CSS + JS) plus Jinja templates.

---

## What the site includes

### Pages
The app renders a small set of pages from the `templates/` folder:

- **Home** (`/`): hero landing page with a typed headline animation.
- **Works** (`/works`): carousel layout to showcase projects.
- **Work detail** (`/work`): single project detail layout.
- **About** (`/about`): about-me section + portrait.
- **Contact** (`/contact`): contact form.
- **Thank you** (`/thankyou`): shown after form submission.
- **Components** (`/components`): style/component reference page (useful when tweaking UI).

### Contact form (end-to-end)
The contact form posts to `/submit_form`.

- Accepts: `email`, `subject`, `message`
- Writes the data to **two formats** for convenience:
  - `database.txt` (CSV rows, “log style”)
  - `database.csv` (CSV with consistent quoting)
- Redirects to `thankyou` after success

**Data is written to the Flask instance folder** so runtime data stays separate from source code:

- `var/server-instance/database.txt`
- `var/server-instance/database.csv`

---

## Tech stack

### Back-end
- **Python 3.14** (local venv metadata in `pyvenv.cfg`)
- **Flask 3.x**
- **Gunicorn** for production serving (see `wsgi.py`)

### Front-end
- Pre-built static assets:
  - `static/main.css` (compiled CSS)
  - `static/main.js` (compiled JS)
- The CSS bundle includes **Bootstrap 3.3.7** and project-specific theme styles.
- The JS bundle includes Bootstrap’s JS plugins and site-specific behaviors.

### Tooling
- VS Code tasks in `.vscode/tasks.json`:
  - Run dev server
  - Open local site
  - Open production site

---

## Architecture (how it works)

### Request → response flow
1. A request comes in (example: `GET /about`).
2. Flask routes it to the `page()` handler.
3. `page()` renders `templates/about.html` via Jinja.
4. The HTML references the compiled static CSS/JS via `url_for('static', ...)`.

### Routing strategy
I designed routing so pages are easy to add while still being safe:

- `GET /` renders `index.html`.
- `GET /<page_name>` attempts to render `<page_name>.html`.
- A strict allowlist regex ensures the dynamic path segment is “filename-safe”:
  - allowed: letters, digits, `_`, `-`
  - blocked: slashes, dots, and traversal patterns

If a template doesn’t exist, the server returns a 404.

---

## Back-end details (developer notes)

### Key files
- `server.py`
  - Defines the Flask app
  - Implements page routing
  - Handles contact form submission
  - Writes contact submissions into the instance data directory
- `dev_server.py`
  - Runs the app locally with `debug=True` on `127.0.0.1:5000`
- `wsgi.py`
  - Production entrypoint for Gunicorn (`gunicorn wsgi:app`)

### Data persistence
This project deliberately uses a simple persistence approach:

- **Why**: for a portfolio contact form, file-based storage is easy to deploy, easy to inspect, and doesn’t require provisioning a database.
- **Where**: the Flask instance folder (`var/server-instance/`) keeps data separate from tracked source.

### Error handling
- If a submission write fails, `/submit_form` returns a 500 with a message.
- Otherwise, it redirects to the thank-you page.

### Contact form email delivery (SMTP)
The contact form can also send you an email notification via SMTP (in addition to saving to the instance files).

Configure these environment variables on your host:

- `CONTACT_SMTP_HOST` (default: `mail.fcjamison.com`)
- `CONTACT_SMTP_PORT` (default: `587`)
- `CONTACT_SMTP_USER` (required)
- `CONTACT_SMTP_PASSWORD` (required)
- `CONTACT_MAIL_FROM` (default: `CONTACT_SMTP_USER`)
- `CONTACT_MAIL_TO` (default: `CONTACT_SMTP_USER`)
- `CONTACT_SMTP_USE_STARTTLS` (default: `true`)

Notes:
- The outgoing message uses `CONTACT_MAIL_FROM` as the sender and sets `Reply-To` to the visitor’s typed email.
- This avoids spoofing issues on servers that reject arbitrary `From` addresses.

---

## Front-end & design notes

### Visual style
- Minimal, high-contrast layout with a strong black/white theme and a “border frame” effect.
- Large hero typography on the landing page to immediately communicate role/identity.

### Layout system
- Bootstrap grid + utility patterns.
- Reusable card containers for content blocks and work previews.

### Interaction design
- Landing page typed animation (rotating intro lines).
- Works carousel for browsing project tiles.
- Hover effect on work thumbnails (grayscale → full color).

### Accessibility considerations
- Semantic HTML structure and headings.
- Basic mobile support via responsive meta tag + Bootstrap.

(If you’d like, I can take the next step and add: better alt text, keyboard focus styling checks, and form error messaging.)

---

## How to run locally (Windows)

### Option A: Use the included VS Code tasks
- Run **“Run Dev Server”**
- Then run **“Open in Browser”**

### Option B: Run from a terminal
If you are using the repo’s virtual environment:

1. Activate the venv:
   - `Scripts\\activate.bat`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start the dev server:
   - `python dev_server.py`
4. Open:
   - http://127.0.0.1:5000/

---

## Production deployment

This project is set up for a standard WSGI deployment.

- Entrypoint: `wsgi:app`
- Example:
  - `gunicorn wsgi:app`

Notes:
- The app writes contact submissions to the instance directory at runtime.
- Ensure the deployment environment has write permission for `var/server-instance/`.

---

## Repository map

- `templates/` — Jinja HTML pages
- `static/` — compiled front-end assets and images
- `server.py` — Flask application
- `dev_server.py` — local runner
- `wsgi.py` — production WSGI entrypoint
- `requirements.txt` — Python dependencies
- `var/server-instance/` — runtime data (contact form submissions)
- `.vscode/` — editor tasks and interpreter settings

---

## Credits

This project uses a prebuilt theme/template as a starting point and I customized it for my portfolio.

- Template attribution appears in the HTML metadata (Orson.io “Mashup Template”).
- Image attribution references Unsplash.

---

## Roadmap (next upgrades I’d ship)

If I were extending this beyond a portfolio, here’s what I’d add next:

- CSRF protection and stronger server-side validation for the contact form
- Spam protection (honeypot field + rate limiting)
- Replace file storage with SQLite (still simple, but more robust)
- Add a real projects data model and render “Works” from structured data
- Improve accessibility (alt text, keyboard-first UX, reduced-motion mode)

---

## Contact

If you want to talk about this project or a role, the contact form on the site is the fastest way to reach me.
