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
`/api/vi/infos/*`. The existing `vi` prefix is intentional for compatibility.
Python imports use `backend/` as the application root, matching the Docker working
directory. For local execution from the repository root:

```bash
uvicorn main:app --app-dir backend
```

Set `SECRET_KEY` and `DATABASE_URL` in the environment before starting the app.

## Backend tests

### Docker

Run from the repository root. This builds a test image and starts an isolated
PostgreSQL test database; Python, pytest, and PostgreSQL do not need to be installed
on the host:

```bash
docker compose run --build --rm test
```

The test services use the `test` profile, so the regular `docker compose up`
application stack is unaffected. The test database is separate from the app's
`db` service and is not published to the host.

### Local Python

If you prefer to run pytest outside Docker, use a dedicated PostgreSQL test DB:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
createdb eq_hearing_test
TEST_DATABASE_URL='postgresql+asyncpg://postgres:postgres@localhost:5432/eq_hearing_test' \
  .venv/bin/python -m pytest -q
```

The test suite requires `TEST_DATABASE_URL` to point to a dedicated PostgreSQL
database whose name includes `test`; SQLite is not supported. Each test gets a
unique schema that is dropped after the test, so the test role must be allowed to
create and drop schemas. Tests cover authentication, session/question workflows,
ownership checks, response serialization, deletion cascades, rollback, and
PostgreSQL row-lock concurrency. Email deliverability checks are stubbed to avoid
DNS dependency.
