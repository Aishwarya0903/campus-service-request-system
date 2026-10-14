# Database design

Core entities are `users`, `tickets`, `notifications`, `sla_rules`, `ticket_status_history`, and `model_versions`. Ticket foreign keys bind a student and optional assigned staff user. Authorization queries ensure students receive only their tickets and staff receive only their department. Email is unique and indexed; ticket status and notification user are indexed by their access patterns.
