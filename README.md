# AI-Powered Campus Service Request System

A final-year capstone prototype that combines a React complaint portal, FastAPI REST API, PostgreSQL schema, NLP ticket classification, and SLA breach-risk prediction. It supports student, staff, and administrator workflows described in Review-1.

## What it does

- Students register, log in, submit a free-text request with location, upload a JPEG/PNG attachment, track their own tickets, and read notifications.
- The backend uses trained TF-IDF + Logistic Regression/Linear SVM candidate models to classify category and priority on ticket submission.
- Staff can only view their department, update lifecycle status, and record resolution notes.
- The Gradient Boosting SLA model scores open tickets using elapsed time, category, priority, created hour/day, and department workload. A scheduled production deployment can invoke `POST /sla/evaluate`; the Docker demo exposes this explicit trigger for transparent testing.
- Administrators manage SLA parameters and see database-derived totals, workloads, status/category/priority breakdowns, and high-risk tickets.

## Stack

React/Vite, FastAPI, SQLAlchemy, PostgreSQL, scikit-learn, pandas, NumPy, TF-IDF, Logistic Regression, Linear SVM, Gradient Boosting, Docker Compose.

## Quick start with Docker

1. Copy `.env.example` to `.env` and replace `JWT_SECRET`.
2. Run `docker compose up --build`.
3. Open `http://localhost:5173`; FastAPI Swagger is at `http://localhost:8000/docs`.

The container trains the reproducible synthetic models and seeds the database before the API starts. Docker uses PostgreSQL. The `postgres_data` volume retains local data; remove it only when you intentionally want a clean demo database.

## Non-Docker setup

Use Python 3.11+ and Node 20+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python ml/training/train_models.py
$env:DATABASE_URL='sqlite:///./campus.db' # local demonstration fallback; use PostgreSQL URL for the target deployment
$env:JWT_SECRET='generate-a-long-random-value'
cd backend
python -m app.seed
uvicorn app.main:app --reload
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

For PostgreSQL outside Docker, create a database and set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/campus_service`. The SQLAlchemy metadata bootstraps tables for development; `database/migrations/001_initial.sql` is the versioned schema reference to run through the deployment migration process.

## Demo accounts

All seed accounts use `CampusDemo2026!` and must be changed outside a demo environment.

| Role | Email |
|---|---|
| Student | student@campus.test |
| Electrical staff | electrical@campus.test |
| Plumbing staff | plumbing@campus.test |
| IT staff | it@campus.test |
| Hostel staff | hostel@campus.test |
| Admin | admin@campus.test |

## ML reproducibility and evaluation

`ml/training/train_models.py` generates `ml/data/synthetic_campus_tickets.csv`, trains the saved artifacts in `ml/models/`, and prints/writes actual held-out validation metrics to `ml/models/evaluation.json`. The data is synthetic campus-style data, not VIT data. It compares Logistic Regression and Linear SVM using accuracy and macro-F1 for each NLP task. The SLA model trains a Gradient Boosting classifier on a separately generated operational-history simulation. It reports its actual validation accuracy, macro-F1, and confusion matrix. Its output must not be interpreted as a real-world campus performance estimate.

## Testing and smoke test

After dependencies are installed, run `pytest backend/tests` and `npm run test` inside `frontend`. Manual smoke test: log in as student; create a request; confirm category/priority; log in as matching staff and update status; return as student to inspect notifications; log in as admin to invoke `/sla/evaluate` from Swagger and inspect `/analytics/overview`.

## ## Final Project Status

The AI-Powered Campus Service Request System has been implemented using React, FastAPI, PostgreSQL, SQLAlchemy, and machine learning models.

### Implemented Features
- Role-based authentication for students, staff, and administrators.
- Campus service request creation and department-based routing.
- Automated ticket classification and priority prediction.
- SLA-breach risk prediction using a trained machine learning model.
- Ticket status tracking, history, and internal notifications.
- PostgreSQL database integration.
- Model training and evaluation artifacts.
- Backend automated tests and frontend production build.

### Testing and Final Demonstration

The backend test suite completed successfully with 11 passing tests, and the frontend production build completed successfully. The application is being prepared for its final demonstration.

### Future Enhancements

Potential enhancements include evaluating the SLA model against real campus operational data, integrating an external email/SMS provider, expanding end-to-end test coverage, and improving accessibility and mobile responsiveness.
