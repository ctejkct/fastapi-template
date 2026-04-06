# FastAPI Template

FastAPI template derived from the `zml-api` repository structure and layering principles, with Firebase/Firestore replaced by PostgreSQL and Redis.

## Architecture

- `api` for versioned route wiring and dependency injection
- `schemas` for request and response contracts
- `interfaces` for service and repository abstractions
- `services` for business logic
- `repositories` for persistence adapters
- `db` for PostgreSQL and Redis clients
- `core` for logging, security, and exception handling
- `middleware` for request-scoped context

## Stack

- FastAPI
- Alembic
- SQLAlchemy async + PostgreSQL
- Redis
- Pydantic Settings
- Pytest

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d postgres redis
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Environment

The template expects:

- `DATABASE_URL` for PostgreSQL
- `REDIS_URL` for Redis
- `JWT_SECRET_KEY` for bearer token signing

## Migrations

Apply the initial schema:

```bash
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

## Included Example Modules

- `authentication`: register, login, current user
- `users`: CRUD-style profile access with Redis-backed read-through cache
- `health`: liveness and readiness checks

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest
```
