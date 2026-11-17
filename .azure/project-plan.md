# Project Plan

**Status**: Planning
**Created**: 2026-11-17
**Mode**: NEW

---

## 1. Project Overview

**Goal**: Build a modest hospital-management web application for tracking patients, doctors, departments, appointments, and visit records. The project is designed so that every module is independently testable.

**App Type**: Full-stack SSR

**API Login**: No

**Mode**: NEW

**Deployment Plan**: No deployment plan found

---

## 2. Backend - Flask

| Component | Technology |
|-----------|-----------|
| **Language** | Python |
| **Runtime** | CPython |
| **Framework** | Flask |
| **Package Manager** | pip |
| **Test Runner** | pytest |
| **Mocking Library** | unittest.mock |
| **Test Command** | python -m pytest |
| **Orchestration** | docker-compose |

> **Language vs Runtime**: `Language` is the source language the user picked in this service's `language` question. `Runtime` is the execution runtime — default `Node` for TypeScript/JavaScript, `CPython` for Python, `.NET` for C#. Only deviate from the default (e.g. `Bun`, `Deno`, `PyPy`) when the user explicitly asks. **Package Manager and Test Runner are language-dependent** — match them to this service's Language (e.g. C# → `dotnet (NuGet)` + `xUnit`/`NUnit`/`MSTest`). The `Orchestration` row is recorded for the scaffold step but hidden in the plan UI — always keep it set to `docker-compose`.

> Tooling alternatives in the template are examples, not an allowlist. Preserve the user's confirmed package manager and test runner, and derive a matching test command rather than replacing their selection with a default.

> **Runtime names only:** write just the runtime name in the Runtime row; keep host/programming-model details and explicit version constraints outside this row; detected tool versions belong in Prerequisites.

> **API framework selection:** copy the service's framework answer into the Framework row and section title. Azure Functions is the only suggested API framework for every language; the plan view also provides a custom field. Preserve explicit custom frameworks, including during language edits, and keep their best-effort warning separate from language support. Do not emit a limited-support warning for Python on Azure Functions.

---

## 3. Services Required

| Azure Service | Role in App | Environment Variable | Default Value (Local) | Classification |
|---------------|------------|---------------------|----------------------|----------------|
| PostgreSQL | Primary relational data store for patients, doctors, departments, appointments, and visit records | DATABASE_URL | postgresql://postgres:postgres@localhost:5432/hospitaldb | Essential |

---

## 4. Prerequisites

Identify the required tools, then inventory them by following the prerequisites guidance. The plan webview shows the Run group always and the Debug group only when the user turns on the Autopilot toggle, so both groups are listed below.

### Run

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| Python | hospital-management | ✅ | 3.14 |
| pip | hospital-management | ✅ | 26.1.1 |
| pytest | hospital-management | ❓ | Not detected in PATH |

### Debug

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| Docker | hospital-management | ✅ | detected |
| Docker Compose | hospital-management | ✅ | detected |
| VS Code Python extension (`ms-python.python`) | hospital-management | ❓ | Not confirmed |

---

## 5. Project Structure

```text
hospital-management/
├─ app/
│  ├─ __init__.py
│  ├─ models.py
│  ├─ routes.py
│  ├─ forms.py
│  ├─ services/
│  │  ├─ patient_service.py
│  │  ├─ appointment_service.py
│  │  └─ audit_service.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ dashboard.html
│  │  ├─ patients.html
│  │  ├─ appointments.html
│  │  └─ staff_login.html
│  └─ static/
│     ├─ css/
│     │  └─ site.css
│     └─ js/
│        └─ app.js
├─ tests/
│  ├─ test_patients.py
│  ├─ test_doctors.py
│  ├─ test_appointments.py
│  └─ test_views.py
├─ .env.example
├─ requirements.txt
├─ Jenkinsfile
├─ pytest.ini
├─ run.py
└─ README.md
```

---

## 6. Route Definitions

| # | Method | Path | Description | Request Body | Response Body | Status Codes |
|---|--------|------|-------------|-------------|--------------|-------------|
| 1 | GET | `/api/health` | Health check for the application and persistence layer | — | `{ status, services }` | 200, 503 |
| 2 | GET | `/api/patients` | List patient records with basic filtering | — | `{ patients: [...] }` | 200 |
| 3 | POST | `/api/patients` | Create a new patient record | `{ name, age, gender, blood_group, department_id }` | `{ patient }` | 201, 400 |
| 4 | GET | `/api/doctors` | List provider records | — | `{ doctors: [...] }` | 200 |
| 5 | GET | `/api/appointments` | List scheduled appointments | — | `{ appointments: [...] }` | 200 |
| 6 | POST | `/api/appointments` | Create or reschedule an appointment | `{ patient_id, doctor_id, appointment_date, notes }` | `{ appointment }` | 201, 400 |
| 7 | GET | `/api/departments` | List departments and staffing overview | — | `{ departments: [...] }` | 200 |

---

## 7. Next Steps

1. Run **azure-project-scaffold** to execute this plan
2. Run **azure-project-integrate** to wire the frontend to live data, smoke-test the backend, and create the migrations
3. Run **azure-debug-plan** → **azure-debug-generate** for Docker emulators and VS Code debugging
4. Run the **azure-deploy** agent when ready; it uses **azure-app-onboard** for architecture, cost estimation, IaC generation, provisioning, and health verification
