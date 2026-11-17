# CareDesk — Hospital Management Demo

A small Flask app for keeping a basic patient directory and appointment schedule. The pages use plain HTML templates and CSS, and the records are stored in a local SQLite database.

## Run locally

Python 3.10 or newer is recommended.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The database is created at `instance/hospital.db` the first time the app starts. Sample doctors and departments are added automatically; patient data starts empty.

To use a different database file, set `DATABASE_PATH` before starting the app. A fresh random session key is generated on each run unless `SECRET_KEY` is set.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Jenkins

The `Jenkinsfile` installs the Python dependencies and runs the test suite. Configure a Jenkins agent with Python 3 and `pip`, create a Pipeline job pointing at this repository, and Jenkins will pick up the pipeline automatically. The pipeline uses `sh`, so the agent should be Linux-based.

## Scope and privacy

This is a learning/demo project. It has no staff authentication, role permissions, audit trail, CSRF protection, or production deployment hardening. Do not enter real patient or health information or use it for clinical operations.
