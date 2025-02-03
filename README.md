# harborline-freight

Monorepo for **Harborline Book** — the new booking platform replacing the PHP billing app.

Right now this is just the Flask API skeleton:

```bash
cd api
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
flask --app wsgi run --debug
curl localhost:5000/healthz
```

More soon. — Dana
