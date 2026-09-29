# EQ Hearing Training
An quiz application for randomised EQ hearing training.

## Stacks
- Python
- FastAPI
- SQLAlchemy
- Docker
- JWT


## To run (Backend)
```bash
git clone git@github.com:David0023/EQ_Hearing_Training.git
cd EQ_Hearing_Training
docker compose up --build
```

- To reset DB and run
```bash
git clone git@github.com:David0023/EQ_Hearing_Training.git
cd EQ_Hearing_Training
docker compose down -v && docker compose up --build
```

## DB Tables
- TODO: Add a diagram
### User
- User registration requires email, username and password.
- Currently supported login method: Email & Login

### Training Session
- Defines Training Quesiton type and rule.

### Training Question
- Child of training session. Actual EQ Quiz Question and Answer.
## Backend structure

```text
backend/
├── main.py                # App startup and router composition
├── api/v1/router.py       # Versioned API composition
├── core/config.py         # Application settings
├── db/                    # Engine, sessions, base classes, model registration
├── auth/                  # Registration, login, tokens, current-user dependency
├── user/                  # User model, schemas, repository, account routes
├── training/
│   ├── dependencies.py    # Session ownership checks and locked session lookup
│   ├── enums.py           # Training-specific shared types
│   ├── domain/            # Pure question generation and training rules
│   ├── info/              # Frequency/gain option routes and schemas
│   ├── session/           # Session router, service, model, schema, repository
│   └── question/          # Question router, service, model, schema, repository
└── tests/                 # API and persistence regression tests
```

Routers handle HTTP input/output, services coordinate feature operations, and
repositories access the database. Training domain code does not depend on FastAPI
or SQLAlchemy. Register new ORM models in `db/models.py` so initialization does not
rely on router imports. Repository writes currently own commit/rollback; callers
must hold the session lock until a question is created or answered.

Existing public URLs are preserved: `/auth/*`, `/api/vi/training/*`, and
`/api/vi/info/*`. The existing `vi` prefix is intentional for compatibility.
Python imports use `backend/` as the application root, matching the Docker working
directory. For local execution from the repository root:

```bash
uvicorn main:app --app-dir backend
```

Set `SECRET_KEY` and `DATABASE_URL` in the environment before starting the app.

## Backend tests

Run from the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
.venv/bin/python -m pytest -q
```

Tests start the app against a temporary SQLite database with foreign keys enabled.
They cover authentication, session/question workflows, ownership checks, response
serialization, deletion cascades, and rollback. Email deliverability checks are
stubbed to avoid DNS dependency. PostgreSQL row-lock concurrency requires a separate
PostgreSQL integration environment; SQLite tests do not validate that behavior.
