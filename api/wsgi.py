"""WSGI entrypoint used by gunicorn (`gunicorn wsgi:app`) and `flask run`."""
import os

from app import create_app

app = create_app(os.environ.get("HBL_ENV", "production"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=False)
