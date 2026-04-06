# FastAPI Template Blueprint

This document is the complete build specification for recreating the `fastapi-template` repository from scratch in any location.

It is intentionally written so that a human or AI agent can use this file alone to regenerate the full repository without needing the original repo contents.

## Purpose

Create a production-oriented FastAPI backend template that preserves the architectural style used in `zml-api`:

- clear module boundaries
- SOLID-oriented service and repository abstractions
- dependency injection through FastAPI dependencies
- centralized configuration
- centralized exception handling
- structured logging with request correlation
- versioned API routing
- strong schema usage through Pydantic

The original `zml-api` used Firebase/Firestore/Realtime DB. This template replaces that persistence layer with:

- PostgreSQL via async SQLAlchemy
- Redis for cache/session-style fast access

All other design ideas remain broadly similar.

## High-Level Architectural Rules

Use this layering strictly:

1. `api`
   Exposes HTTP endpoints only.
   No business logic here.
   Endpoints should call service abstractions through dependency injection.

2. `schemas`
   Defines request and response contracts.
   Use Pydantic models.
   Keep transport contracts here, not in services or repositories.

3. `interfaces`
   Defines abstract contracts for services and repositories.
   Services depend on repository abstractions, not concrete implementations.

4. `services`
   Implements business logic.
   Services orchestrate repositories, security helpers, and cache logic.
   Services should not know about FastAPI request objects.

5. `repositories`
   Implements data access.
   Concrete repositories talk to PostgreSQL or Redis.
   Repositories should not contain HTTP concerns.

6. `db`
   Contains low-level database and cache client setup.
   Includes SQLAlchemy engine/session management and Redis client management.

7. `core`
   Contains cross-cutting concerns:
   - exceptions
   - logging
   - security helpers

8. `middleware`
   Contains request-scoped middleware like request id and trace id handling.

9. `main.py`
   Wires app startup, shutdown, middleware, router registration, and exception handling.

## Template Scope

The template should include three functional areas:

- health endpoints
- authentication endpoints
- user management endpoints

These are meant to demonstrate the architecture, not to be the only modules future teams use.

## Required Repository Layout

Create exactly this repository structure:

```text
fastapi-template/
├── .dockerignore
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── README.md
├── TEMPLATE_BLUEPRINT.md
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 20260330_0001_create_users_table.py
├── docker-compose.yml
├── pytest.ini
├── requirements-dev.txt
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── authentication.py
│   │           ├── health.py
│   │           └── users.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── init_db.py
│   │   ├── models.py
│   │   ├── redis.py
│   │   └── session.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── authentication.py
│   │   ├── users.py
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── authentication.py
│   │       ├── base.py
│   │       └── users.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── request_context.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_cache_repository.py
│   │   └── user_repository.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── authentication.py
│   │   ├── common.py
│   │   └── users.py
│   └── services/
│       ├── __init__.py
│       ├── authentication.py
│       └── users.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_authentication_service.py
    ├── test_health.py
    └── test_users_endpoints.py
```

## Technology Choices

Use these libraries:

- `fastapi==0.109.2`
- `uvicorn==0.27.1`
- `alembic==1.14.0`
- `sqlalchemy==2.0.36`
- `asyncpg==0.30.0`
- `redis==5.2.1`
- `pydantic==2.12.5`
- `pydantic-settings==2.13.1`
- `python-json-logger==2.0.7`
- `python-jose==3.3.0`
- `passlib[bcrypt]==1.7.4`
- `email-validator==2.3.0`
- `httpx==0.26.0`
- `pytest==9.0.2`
- `pytest-asyncio==1.3.0`
- `pytest-cov==7.0.0`

For development:

- `black==24.2.0`
- `flake8==7.0.0`
- `isort==5.13.2`
- `pre-commit==4.5.1`

## Root Files

### `README.md`

Purpose:

- brief project introduction
- explain that this template mirrors `zml-api` structure but uses PostgreSQL and Redis
- explain quick start
- list main modules
- include docker and testing instructions

### `.env.example`

Must include:

```env
ENVIRONMENT=local
DEBUG=true

APP_NAME=FastAPI Template
APP_VERSION=0.1.0
API_PREFIX=/api/v1
HOST=0.0.0.0
APP_PORT=8080

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/zml_template
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

REDIS_URL=redis://localhost:6379/0
REDIS_DEFAULT_TTL_SECONDS=300

JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://localhost:3000,http://localhost:8080

LOG_LEVEL=INFO
LOG_JSON_FORMAT=false
```

### `requirements.txt`

Must contain exactly the runtime dependencies listed earlier, including `alembic`.

### `requirements-dev.txt`

Should start with:

```text
-r requirements.txt
```

Then append dev-only tooling.

### `pytest.ini`

Use:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
asyncio_mode = auto
filterwarnings =
    ignore::DeprecationWarning
```

### `.gitignore`

Must ignore:

- Python caches
- virtual environments
- `.env`
- coverage artifacts
- IDE folders
- local logs
- `test.db`

### `.dockerignore`

Must ignore:

- `.git`
- `.env`
- IDE folders
- Python cache folders
- `tests/`
- `logs/`
- markdown docs
- dev config files

### `.pre-commit-config.yaml`

Include:

- `pre-commit-hooks`
- `black`
- `isort`
- `flake8`

Use the same general style as `zml-api`.

### `alembic.ini`

Must:

- set `script_location = %(here)s/alembic`
- set `prepend_sys_path = .`
- include a placeholder sync `sqlalchemy.url`
- include standard logger/handler configuration for Alembic

### `alembic/env.py`

Must:

- read settings from `app.config.settings.get_settings()`
- convert async URL to sync URL for Alembic
- import `Base.metadata`
- import ORM models so metadata is populated
- support both offline and online migration modes
- enable `compare_type=True`

### `alembic/script.py.mako`

Must provide the standard Alembic revision template.

### `alembic/versions/20260330_0001_create_users_table.py`

Must be the initial migration.

It should:

- create the `users` table
- create the unique index on `email`
- include a matching downgrade

### `docker-compose.yml`

Must define these services:

1. `api`
   - build current repo
   - use development target
   - load `.env`
   - expose `8080:8080`
   - depend on `postgres` and `redis`
   - mount current directory to `/app`

2. `postgres`
   - image: `postgres:16-alpine`
   - db: `zml_template`
   - user: `postgres`
   - password: `postgres`
   - expose `5432:5432`

3. `redis`
   - image: `redis:7-alpine`
   - expose `6379:6379`

### `Dockerfile`

Must be multi-stage:

1. `base`
   - `python:3.12-slim-bookworm`
   - install `build-essential`
   - define Python env vars
   - create non-root user `appuser`
   - create `/app/logs`

2. `dependencies`
   - copy `requirements.txt`
   - install runtime packages

3. `production`
   - copy app code
   - switch to `appuser`
   - run `uvicorn app.main:app`

4. `development`
   - install `requirements-dev.txt`
   - copy full repo
   - run uvicorn with `--reload`

## Migration Workflow

Alembic is the source of truth for schema changes.

Required commands:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

The application should not rely on `Base.metadata.create_all()` as the normal schema-management mechanism.

## App Configuration Layer

### `app/config/settings.py`

Must provide:

- `Environment` enum with:
  - `DEVELOPMENT`
  - `LOCAL`
  - `STAGING`
  - `PRODUCTION`

- `Settings` class using `BaseSettings`
- cached `get_settings()`
- base `.env` loading
- optional `.env.{environment}` loading

Required fields:

- `environment`
- `debug`
- `app_name`
- `app_version`
- `api_prefix`
- `host`
- `app_port`
- `database_url`
- `database_echo`
- `database_pool_size`
- `database_max_overflow`
- `redis_url`
- `redis_default_ttl_seconds`
- `jwt_secret_key`
- `jwt_algorithm`
- `jwt_access_token_expire_minutes`
- `cors_origins`
- `log_level`
- `log_json_format`

Required helper behavior:

- validate `api_prefix` starts with `/`
- validate `log_level`
- expose `cors_origins_list` property that parses comma-separated origins

## Core Layer

### `app/core/exceptions.py`

Implement:

- `APIException`
- `NotFoundError`
- `ValidationError`
- `UnauthorizedError`
- `ConflictError`
- `DatabaseError`
- `ExternalServiceError`

Also implement:

- `create_error_response(...)`
- `api_exception_handler(...)`
- `generic_exception_handler(...)`
- `register_exception_handlers(app)`

Behavior:

- API errors return:

```json
{
  "success": false,
  "error": {
    "status_code": 500,
    "code": "DATABASE_ERROR",
    "message": "Database operation failed",
    "path": "/api/v1/users"
  }
}
```

- attach `WWW-Authenticate: Bearer` for auth failures
- log 5xx as errors and 4xx as warnings

### `app/core/logging.py`

Must support:

- request-scoped request ids
- request-scoped trace ids
- optional user id
- JSON logs for production
- human-readable console logs for local/dev
- JSON file logging to `logs/app.log` in non-JSON mode

Required functions and objects:

- context vars:
  - `request_id_ctx`
  - `trace_id_ctx`
  - `user_id_ctx`
- `set_request_context(...)`
- `generate_request_id()`
- `ProductionJsonFormatter`
- `setup_logging(...)`
- `get_logger(name)`

JSON logs should include:

- timestamp
- level
- logger
- service
- version
- environment
- request_id if available
- trace_id if available
- user_id if available
- file
- line
- function
- exception details if present

### `app/core/security.py`

Implement:

- password hashing with `passlib`
- JWT encode/decode with `python-jose`

Required functions:

- `hash_password(password: str) -> str`
- `verify_password(plain_password: str, hashed_password: str) -> bool`
- `create_access_token(subject: str, additional_claims: dict | None = None) -> str`
- `decode_access_token(token: str) -> dict`

Behavior:

- read JWT settings from `Settings`
- put `sub` into the token
- include expiration
- raise `UnauthorizedError` on invalid/expired tokens

## Database Layer

### `app/db/base.py`

Define:

- SQLAlchemy declarative `Base`

### `app/db/models.py`

Define one ORM model:

#### `UserORM`

Table: `users`

Fields:

- `id: str`
  - primary key
  - UUID string default
- `email: str`
  - unique
  - indexed
  - not null
- `full_name: str`
  - not null
- `hashed_password: str`
  - not null
- `is_active: bool`
  - default true
- `created_at: datetime`
  - timezone-aware
  - server default `now()`
- `updated_at: datetime`
  - timezone-aware
  - server default `now()`
  - update on modification

### `app/db/session.py`

Must provide:

- async engine creation
- `SessionLocal`
- `get_db_session()`
- `check_database_connection()`
- `close_database_engine()`

Important behavior:

- use `create_async_engine`
- set `pool_pre_ping=True`
- if DB is not SQLite, include pool sizing from settings
- if DB is SQLite, avoid passing pool-specific args that break SQLite

### `app/db/redis.py`

Must provide:

- singleton `Redis` async client
- `get_redis_client()`
- `check_redis_connection()`
- `close_redis_client()`

Use:

- `Redis.from_url(..., decode_responses=True)`

### `app/db/init_db.py`

Purpose:

- import ORM models so metadata is registered
- avoid automatic schema creation at app startup

Required function:

- `init_db()`

Behavior:

- do not call `Base.metadata.create_all`
- act as a lightweight metadata-loading hook
- schema changes should be applied through Alembic

## Schema Layer

### `app/schemas/common.py`

Create:

- `BaseSchema`
  - `from_attributes=True`
  - `populate_by_name=True`
- `TimestampMixin`
- `SuccessResponse`
- `DataResponse[T]`
- `ListResponse[T]`
- `HealthStatus`

### `app/schemas/users.py`

Create:

#### `UserCreateRequest`

- `email: EmailStr`
- `full_name: str`, min 2, max 255
- `password: str`, min 8, max 128

#### `UserUpdateRequest`

- `full_name: Optional[str]`
- `is_active: Optional[bool]`

#### `UserResponse`

- `id: str`
- `email: EmailStr`
- `full_name: str`
- `is_active: bool`
- inherit timestamps via `TimestampMixin`

### `app/schemas/authentication.py`

Create:

#### `RegistrationRequest`

- `email`
- `full_name`
- `password`

#### `LoginRequest`

- `email`
- `password`

#### `AuthResponse`

- `access_token: str`
- `token_type: str = "bearer"`
- `user: UserResponse`

## Interface Layer

### `app/interfaces/authentication.py`

Define `IAuthenticationService` with:

- `register(request: RegistrationRequest) -> AuthResponse`
- `login(request: LoginRequest) -> AuthResponse`
- `get_me(user_id: str) -> UserResponse`

### `app/interfaces/users.py`

Define `IUsersService` with:

- `create_user(request: UserCreateRequest) -> UserResponse`
- `get_user(user_id: str) -> UserResponse`
- `list_users(limit: int = 100) -> list[UserResponse]`
- `update_user(user_id: str, request: UserUpdateRequest) -> UserResponse`

### `app/interfaces/repositories/base.py`

Define generic `IRepository[T]` with:

- `get_by_id(item_id: str) -> Optional[T]`
- `get_all(limit: int = 100) -> list[T]`
- `create(data: dict) -> T`
- `update(item_id: str, data: dict) -> T`
- `delete(item_id: str) -> None`
- `exists(item_id: str) -> bool`

### `app/interfaces/repositories/authentication.py`

Define `IAuthenticationRepository` with:

- `get_by_email(email: str) -> UserResponse | None`
- `create_credentials_user(email: str, full_name: str, hashed_password: str) -> UserResponse`

### `app/interfaces/repositories/users.py`

Define:

#### `IUserRepository`

Extends generic repository for `UserResponse` and adds:

- `get_by_email(email: str) -> Optional[UserResponse]`
- `get_hashed_password(user_id: str) -> Optional[str]`

#### `IUserCacheRepository`

For Redis:

- `get_user(user_id: str) -> Optional[UserResponse]`
- `set_user(user: UserResponse) -> None`
- `invalidate_user(user_id: str) -> None`

## Repository Layer

### `app/repositories/base.py`

Create generic `BaseRepository[OrmModelT, SchemaModelT]`.

Responsibilities:

- convert ORM model to Pydantic schema
- implement generic:
  - `get_by_id`
  - `get_by_id_or_raise`
  - `get_all`
  - `exists`
  - `delete`

Leave `create` and `update` as subclass responsibilities.

Requirements:

- use `AsyncSession`
- use `select(...)`
- raise `DatabaseError` for unexpected DB issues
- raise `NotFoundError` when needed

### `app/repositories/user_repository.py`

Implement `UserRepository`:

- inherit `BaseRepository[UserORM, UserResponse]`
- implement both `IUserRepository` and `IAuthenticationRepository`

Required methods:

- `get_by_email(email)`
- `get_hashed_password(user_id)`
- `create_credentials_user(...)`
- `create(data)`
- `update(item_id, data)`

Behavior:

- prevent duplicate email on create
- raise `ConflictError` if email already exists
- commit and refresh entity after writes
- rollback on DB failures
- update only editable fields:
  - `full_name`
  - `is_active`

### `app/repositories/user_cache_repository.py`

Implement `UserCacheRepository` using Redis.

Behavior:

- key format: `user:{user_id}`
- use JSON serialization
- TTL from `settings.redis_default_ttl_seconds`
- methods:
  - `get_user`
  - `set_user`
  - `invalidate_user`
- wrap Redis failures in `ExternalServiceError`

## Service Layer

### `app/services/authentication.py`

Implement `AuthenticationService`.

Constructor dependencies:

- `auth_repo: IAuthenticationRepository`
- `user_repo: IUserRepository`
- `cache_repo: IUserCacheRepository`

Methods:

#### `register`

Flow:

1. hash password
2. create user through auth repo
3. cache user in Redis
4. create JWT access token
5. return `AuthResponse`

#### `login`

Flow:

1. load user by email
2. if missing, raise `UnauthorizedError`
3. load stored hashed password
4. verify password
5. if invalid, raise `UnauthorizedError`
6. cache user in Redis
7. return signed JWT and user payload

#### `get_me`

Flow:

1. look in Redis cache
2. if cached, return cached value
3. otherwise load from DB
4. if missing, raise `UnauthorizedError`
5. cache and return

### `app/services/users.py`

Implement `UsersService`.

Constructor dependencies:

- `repo: IUserRepository`
- `cache_repo: IUserCacheRepository`

Methods:

#### `create_user`

- hash password
- write via repository
- cache result
- return user

#### `get_user`

- prefer Redis cache
- fallback to DB
- cache on miss

#### `list_users`

- direct DB call

#### `update_user`

- update DB
- invalidate Redis cache
- re-cache latest entity
- return updated user

## Middleware Layer

### `app/middleware/request_context.py`

Implement `RequestContextMiddleware`.

Behavior:

- read `X-Request-ID` header if provided, otherwise generate one
- read `X-Trace-ID` header if provided, otherwise generate one
- call `set_request_context(...)`
- add `X-Request-ID` to response headers

## API Dependency Layer

### `app/api/deps.py`

Must define:

- `bearer_scheme = HTTPBearer(auto_error=False)`
- `get_settings_dependency()`
- `get_db()`
- `get_user_repository(session)`
- `get_user_cache_repository()`
- `get_current_user_id(credentials)`

Also define these type aliases:

- `SettingsDep`
- `DbSession`
- `CurrentUserIdDep`

Behavior:

- `get_db()` should yield request-scoped async session
- `get_current_user_id()` should decode JWT bearer token and return `sub`
- if token missing, raise `UnauthorizedError`
- `DbSession` should be exposed as the injected async database session alias:

```python
DbSession = Annotated[AsyncSession, Depends(get_db)]
```

## API Routing Layer

### `app/api/v1/router.py`

Aggregate:

- `health.router`
- `authentication.router`
- `users.router`

## Endpoint Specifications

### `app/api/v1/endpoints/health.py`

Router:

- tag: `Health`

Endpoints:

#### `GET /health`

Response model: `HealthStatus`

Returns:

- `status="healthy"`
- app version
- environment

#### `GET /health/ready`

Returns:

- readiness for PostgreSQL
- readiness for Redis

Structure:

```json
{
  "status": "ready",
  "checks": {
    "postgres": "healthy",
    "redis": "healthy"
  }
}
```

### `app/api/v1/endpoints/authentication.py`

Router:

- prefix: `/authentication`
- tag: `Authentication`

Dependency constructor:

- `get_auth_service(session: DbSession) -> IAuthenticationService`

Wiring:

- `UserRepository(session)`
- `UserCacheRepository(get_redis_client())`
- pass same user repository as both auth repo and user repo

Endpoints:

#### `POST /authentication/register`

- request: `RegistrationRequest`
- response: `AuthResponse`
- status: `201`

#### `POST /authentication/login`

- request: `LoginRequest`
- response: `AuthResponse`
- status: `200`

#### `GET /authentication/me`

- require bearer token
- response is current user payload

### `app/api/v1/endpoints/users.py`

Router:

- prefix: `/users`
- tag: `Users`

Dependency constructor:

- `get_users_service(session: DbSession) -> IUsersService`

Endpoints:

#### `POST /users`

- request: `UserCreateRequest`
- response: `DataResponse[UserResponse]`
- status: `201`

#### `GET /users/{user_id}`

- response: `DataResponse[UserResponse]`
- status: `200`

#### `GET /users`

- query param: `limit`, default 100, range 1..500
- response: `ListResponse[UserResponse]`

#### `PATCH /users/{user_id}`

- request: `UserUpdateRequest`
- response: `DataResponse[UserResponse]`
- status: `200`

Important Python rule:

- in endpoint function signatures, dependency-injected parameters without defaults must appear before normal defaulted query parameters
- example:

```python
async def list_users(
    service: Annotated[IUsersService, Depends(get_users_service)],
    limit: int = Query(default=100, ge=1, le=500),
):
    ...
```

## App Entrypoint

### `app/main.py`

Must define:

- `lifespan(app)`
- `create_application()`
- `app = create_application()`

Startup behavior:

1. load settings
2. configure logging
3. log startup metadata
4. run `init_db()` as metadata-loading only
5. log that schema changes should be applied with Alembic

Shutdown behavior:

1. close Redis client
2. close SQLAlchemy engine

App setup must include:

- `RequestContextMiddleware`
- `CORSMiddleware`
- exception handler registration
- v1 router registration under `settings.api_prefix`
- root `/` endpoint outside versioned API

Root payload should include:

- app name
- version
- environment
- docs URL or "Disabled in production"

## Testing Requirements

### `tests/conftest.py`

Must:

- set env vars before importing app
- use SQLite test DB URL like `sqlite+aiosqlite:///./test.db`
- set test Redis URL
- set JWT secret
- patch `app.main.init_db` with `AsyncMock` to avoid startup DB creation during basic tests
- patch `app.main.init_db` with `AsyncMock` to avoid startup side effects during basic tests
- provide `app` fixture
- provide `client` fixture using `TestClient`

### `tests/test_health.py`

Implement:

- `test_health_check`
- `test_readiness_check`

Use `AsyncMock` to patch readiness dependency functions.

### `tests/test_authentication_service.py`

Use fake in-memory repositories and cache.

Must verify:

- register hashes password and returns token
- invalid login raises `UnauthorizedError`

### `tests/test_users_endpoints.py`

Use FastAPI dependency overrides for `get_users_service`.

Must verify:

- `POST /api/v1/users` returns `201`
- response contains created user email

## Behavioral Conventions

The recreated template must follow these conventions:

- use async database access
- keep route handlers thin
- put all business logic in services
- use repository abstractions for data access
- do not let services depend directly on FastAPI types
- centralize auth token decoding in dependencies/security helpers
- prefer Redis cache before DB on single-entity reads where relevant
- invalidate cache after updates
- use explicit response envelopes for user endpoints
- use a direct response model for auth token responses

## Style Rules

When generating the repository from this blueprint:

- prefer ASCII only
- use concise docstrings
- do not add unrelated modules
- do not add Firebase remnants
- do not add frontend code
- do not add background workers
- keep the template focused on API architecture only

## Minimal File-by-File Implementation Notes

Use these implementation summaries:

- `settings.py`
  Pydantic settings with env-file support and validators.

- `exceptions.py`
  Shared exception hierarchy and FastAPI handler registration.

- `logging.py`
  Request-aware structured logging using context variables.

- `security.py`
  Password hashing and JWT helpers.

- `models.py`
  SQLAlchemy ORM definitions, currently only `UserORM`.

- `session.py`
  Async engine/session creation and health helpers.

- `redis.py`
  Singleton async Redis client and ping helper.

- `init_db.py`
  Load ORM metadata only; real schema changes go through Alembic.

- `alembic.ini`
  Root Alembic configuration.

- `alembic/env.py`
  Binds Alembic to app settings and SQLAlchemy metadata.

- `alembic/versions/20260330_0001_create_users_table.py`
  Initial migration for the `users` table.

- `schemas/common.py`
  Generic response wrappers and health model.

- `schemas/users.py`
  User request and response schemas.

- `schemas/authentication.py`
  Registration, login, and auth response schemas.

- `interfaces/...`
  Abstract service and repository contracts.

- `repositories/base.py`
  Generic SQLAlchemy read/delete helpers.

- `repositories/user_repository.py`
  PostgreSQL implementation for user persistence.

- `repositories/user_cache_repository.py`
  Redis implementation for user caching.

- `services/authentication.py`
  Credential auth workflow.

- `services/users.py`
  User management workflow.

- `api/deps.py`
  DI wiring for settings, DB session, repositories, and current user id.

- `endpoints/health.py`
  Liveness and readiness routes.

- `endpoints/authentication.py`
  Register, login, current user routes.

- `endpoints/users.py`
  Create, get, list, update user routes.

- `main.py`
  App factory and lifecycle wiring.

## Build Instructions for Another Agent

If another AI agent is asked to create this template from this blueprint, it should do the following in order:

1. create the full directory tree
2. write root config files
3. write Alembic config and the initial migration
4. write configuration and core modules
5. write DB and ORM modules
6. write schemas
7. write interfaces
8. write repositories
9. write services
10. write middleware
11. write API dependencies and endpoints
12. write app entrypoint
13. write tests
14. run a syntax pass
15. run tests if dependencies are installed

## Acceptance Criteria

The repository is correct only if all of the following are true:

- it matches the structure defined in this document
- it uses PostgreSQL and Redis, not Firebase
- it includes Alembic and an initial migration for the `users` table
- it preserves the zml-style layering and DI approach
- `uvicorn app.main:app` can start the app when dependencies are installed
- `alembic upgrade head` can apply the initial schema
- `/api/v1/health` exists
- `/api/v1/health/ready` checks postgres and redis
- `/api/v1/authentication/register` exists
- `/api/v1/authentication/login` exists
- `/api/v1/authentication/me` exists
- `/api/v1/users` create/list exists
- `/api/v1/users/{user_id}` get/update exists
- logging, exception handling, and settings are centralized
- tests are present for health, auth service, and users endpoint

## Optional Future Extensions

These are not part of the required template but may be added later:

- Alembic migrations
- refresh tokens
- role-based authorization
- Redis-backed rate limiting
- pagination metadata beyond `limit`
- audit logging
- soft delete support
- additional domain modules using the same architectural pattern

This concludes the full blueprint.
