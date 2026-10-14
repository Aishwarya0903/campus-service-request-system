# Requirement traceability

| Requirement | Source | Implemented location | Status | How to test |
|---|---|---|---|---|
| Student registration/login and RBAC | Review-1 §8, use case | `backend/app/main.py` auth | Implemented | Swagger `/auth/*`, `/users/me` |
| Complaint, free text, location, photo | Review-1 §8 | ticket endpoints and `frontend/src/main.jsx` | Implemented | Submit then `POST /tickets/{id}/attachment` |
| Automatic category/priority | Review-1 §§5,7 | `ml/training/train_models.py`, `classify` | Implemented after training | Submit a WiFi complaint |
| Staff department tickets/status/notes | Review-1 §8 | ticket query/patch authorization | Implemented | Sign in as IT staff |
| Continuous SLA risk and escalation | Review-1 §§5,7,8 | `sla_score`, `reevaluate` | Implemented; deployment scheduler remains | Admin invokes `/sla/evaluate` |
| Notifications | Review-1 §8, use case | `Notification`, `/notifications` | Implemented internally | Change a ticket status |
| Analytics and workload | Review-1 §8 | `/analytics/overview` | Implemented | Admin Swagger/API |
| Configurable SLA rules | Review-1 §8 | `/sla/rules` | Implemented | Admin GET/PUT |
| PostgreSQL and model version schema | Review-1 §7, architecture | models, Compose, migration | Implemented | Docker start |
| Independent retraining/evaluation | Review-1 §7 | `ml/training/train_models.py` | Implemented | Run script and inspect JSON |
| Responsive interface | Review-1 §8 | `frontend/src/styles.css` | Implemented | Resize browser |
