-- PostgreSQL reference migration. The SQLAlchemy startup metadata creates the same schema for local development.
-- Run through Alembic or psql before production deployment; see README.
CREATE TABLE IF NOT EXISTS model_versions (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL, version VARCHAR(100) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
