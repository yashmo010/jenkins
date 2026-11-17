import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for


DEPARTMENTS = ("Cardiology", "General Medicine", "Pediatrics", "Orthopedics")
DOCTORS = (
    ("Dr. Maya Patel", "Cardiology"),
    ("Dr. James Wilson", "General Medicine"),
    ("Dr. Amina Yusuf", "Pediatrics"),
    ("Dr. Leo Chen", "Orthopedics"),
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get(
            "DATABASE_PATH",
            str(Path(app.instance_path) / "hospital.db"),
        ),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    @app.template_filter("datetime")
    def format_datetime(value):
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return f"{parsed.strftime('%b')} {parsed.day}, {parsed.year} · {parsed.strftime('%I:%M %p')}"

    @app.context_processor
    def inject_now_label():
        today = datetime.now()
        return {"now_label": f"{today.strftime('%A, %B')} {today.day}"}

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department_id INTEGER NOT NULL REFERENCES departments(id)
            );
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK (age BETWEEN 0 AND 120),
                phone TEXT NOT NULL DEFAULT '',
                department_id INTEGER REFERENCES departments(id),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY,
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                doctor_id INTEGER NOT NULL REFERENCES doctors(id),
                appointment_at TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Scheduled'
            );
            """
        )
        for department in DEPARTMENTS:
            db.execute(
                "INSERT OR IGNORE INTO departments (name) VALUES (?)",
                (department,),
            )
        department_ids = {
            row["name"]: row["id"]
            for row in db.execute("SELECT id, name FROM departments")
        }
        for name, department in DOCTORS:
            exists = db.execute(
                "SELECT 1 FROM doctors WHERE name = ?", (name,)
            ).fetchone()
            if not exists:
                db.execute(
                    "INSERT INTO doctors (name, department_id) VALUES (?, ?)",
                    (name, department_ids[department]),
                )
        db.commit()

    with app.app_context():
        init_db()

    @app.get("/")
    def dashboard():
        db = get_db()
        counts = {
            "patients": db.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
            "doctors": db.execute("SELECT COUNT(*) FROM doctors").fetchone()[0],
            "appointments": db.execute(
                "SELECT COUNT(*) FROM appointments WHERE date(appointment_at) = date('now')"
            ).fetchone()[0],
        }
        upcoming = db.execute(
            """
            SELECT a.appointment_at, a.status, p.name AS patient, d.name AS doctor
            FROM appointments a
            JOIN patients p ON p.id = a.patient_id
            JOIN doctors d ON d.id = a.doctor_id
            WHERE datetime(a.appointment_at) >= datetime('now')
            ORDER BY a.appointment_at
            LIMIT 5
            """
        ).fetchall()
        return render_template("dashboard.html", counts=counts, upcoming=upcoming)

    @app.get("/patients")
    def patients():
        db = get_db()
        search = request.args.get("q", "").strip()
        rows = db.execute(
            """
            SELECT p.id, p.name, p.age, p.phone, d.name AS department
            FROM patients p
            LEFT JOIN departments d ON d.id = p.department_id
            WHERE p.name LIKE ?
            ORDER BY p.name COLLATE NOCASE
            """,
            (f"%{search}%",),
        ).fetchall()
        departments = db.execute(
            "SELECT id, name FROM departments ORDER BY name"
        ).fetchall()
        return render_template(
            "patients.html", patients=rows, departments=departments, search=search
        )

    @app.post("/patients")
    def add_patient():
        name = request.form.get("name", "").strip()
        age_value = request.form.get("age", "").strip()
        phone = request.form.get("phone", "").strip()
        department_value = request.form.get("department_id", "").strip()
        try:
            age = int(age_value)
            department_id = int(department_value) if department_value else None
            if not name or len(name) > 100 or not 0 <= age <= 120 or len(phone) > 30:
                raise ValueError
            if department_id is not None:
                exists = get_db().execute(
                    "SELECT 1 FROM departments WHERE id = ?", (department_id,)
                ).fetchone()
                if not exists:
                    raise ValueError
        except ValueError:
            flash("Enter a name and a valid age and department.", "error")
            return redirect(url_for("patients"))

        db = get_db()
        db.execute(
            """
            INSERT INTO patients (name, age, phone, department_id)
            VALUES (?, ?, ?, ?)
            """,
            (name, age, phone, department_id),
        )
        db.commit()
        flash("Patient added.", "success")
        return redirect(url_for("patients"))

    @app.get("/appointments")
    def appointments():
        db = get_db()
        rows = db.execute(
            """
            SELECT a.appointment_at, a.reason, a.status,
                   p.name AS patient, d.name AS doctor
            FROM appointments a
            JOIN patients p ON p.id = a.patient_id
            JOIN doctors d ON d.id = a.doctor_id
            ORDER BY a.appointment_at DESC
            """
        ).fetchall()
        patients_list = db.execute(
            "SELECT id, name FROM patients ORDER BY name COLLATE NOCASE"
        ).fetchall()
        doctors_list = db.execute(
            """
            SELECT doctors.id, doctors.name, departments.name AS department
            FROM doctors JOIN departments ON departments.id = doctors.department_id
            ORDER BY doctors.name
            """
        ).fetchall()
        return render_template(
            "appointments.html",
            appointments=rows,
            patients=patients_list,
            doctors=doctors_list,
        )

    @app.post("/appointments")
    def add_appointment():
        try:
            patient_id = int(request.form.get("patient_id", ""))
            doctor_id = int(request.form.get("doctor_id", ""))
            appointment_at = datetime.strptime(
                request.form.get("appointment_at", ""), "%Y-%m-%dT%H:%M"
            ).strftime("%Y-%m-%d %H:%M:%S")
            reason = request.form.get("reason", "").strip()
            if len(reason) > 200:
                raise ValueError
        except ValueError:
            flash("Choose a patient, doctor, date and time, and a short note.", "error")
            return redirect(url_for("appointments"))

        db = get_db()
        valid_patient = db.execute(
            "SELECT 1 FROM patients WHERE id = ?", (patient_id,)
        ).fetchone()
        valid_doctor = db.execute(
            "SELECT 1 FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone()
        if not valid_patient or not valid_doctor:
            flash("Choose a patient and doctor from the list.", "error")
            return redirect(url_for("appointments"))

        db.execute(
            """
            INSERT INTO appointments (patient_id, doctor_id, appointment_at, reason)
            VALUES (?, ?, ?, ?)
            """,
            (patient_id, doctor_id, appointment_at, reason),
        )
        db.commit()
        flash("Appointment scheduled.", "success")
        return redirect(url_for("appointments"))

    return app


if __name__ == "__main__":
    create_app().run(debug=os.environ.get("FLASK_DEBUG") == "1")
