"""Gunicorn configuration.

Defaults to binding on port 30001.
Override by setting the PORT environment variable.

Run:
    gunicorn -c gunicorn.conf.py wsgi:app
"""

import os

bind = f"0.0.0.0:{os.getenv('PORT', '30001')}"

# Keep defaults for workers/threads so hosting can size appropriately.
