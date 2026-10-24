# EQ Hearing Training

EQ Hearing Training is a web app for practicing equalizer listening skills. Users configure a training session, answer generated EQ questions, and review their progress.

> **Project status:** The core account and training flows are implemented. The project is not deployed yet. Audio files are not uploaded to or served by the backend.

## What it does

- Register, log in, manage a profile, and upload a profile image
- Create and resume EQ training sessions
- Answer randomized `simple_blind` questions about target frequency and gain
- Review session questions, correctness, and progress summaries
- Retrieve available frequency groups and gain options

The backend currently supports one question type, `simple_blind`. Statistics and personalized EQ recommendations are planned, but are not implemented yet.

## Tech Stack

| Area | Technologies |
| --- | --- |
| Backend | Python 3.12+, FastAPI, Pydantic, SQLAlchemy 2 async |
| Database | PostgreSQL, Alembic |
| Authentication | JWT access tokens, rotating refresh tokens, Argon2 password hashing |
| Image handling | Pillow, local filesystem storage |
| Development and tests | Docker Compose, uv, pytest, HTTPX |

## Architecture

```mermaid
flowchart LR
    Client[Web client] --> API[FastAPI routers]
    API --> Services[Services]
    Services --> Repositories[Repositories]
    Repositories --> DB[(PostgreSQL)]
    Services --> Domain[Training domain and question strategies]
    API --> Images[Profile image storage]
```

The backend follows a Router → Service → Repository structure. Routers handle HTTP concerns, services coordinate feature flows and database transactions, and repositories handle persistence. Training rules and question generation are kept separate from FastAPI.

See [backend/README.md](backend/README.md) for the backend structure, API routes, setup instructions, data model, and detailed design decisions.

## Selected Design Decisions

### Keep related writes in one transaction

Repositories initially committed their own changes. Answering a question involves several writes, and committing after each repository call prevented the whole operation from rolling back if a later step failed. Transaction ownership now sits in the service layer, which commits or rolls back the complete feature flow.

### Isolate question-type behavior

Although `simple_blind` was the only implemented type, multiple types were planned. A strategy registry groups type-specific settings validation, question generation, and answer evaluation so the shared session and question flows do not accumulate type checks as new types are added.

### Separate shared question state from type-specific data

Question order and answer state are stored in a common table; each question type stores its own details in a separate table. This keeps the data model explicit and avoids centralizing type-specific JSON interpretation and branching in shared code.

### Store only refresh token hashes

Refresh tokens are delivered in HttpOnly cookies, and their SHA-256 hashes are stored in the database. Refresh rotates the token by revoking the old one and issuing a replacement. More detail is in [backend/README.md](backend/README.md#design-decisions).

## Run Locally

### Start with Docker Compose

From the repository root:

```bash
docker compose up --build
```

This starts PostgreSQL, applies database migrations, and starts the API at `http://localhost:8000`. The interactive API docs are at `http://localhost:8000/docs`.

### Run the backend directly

Start PostgreSQL, then from `backend/`:

```bash
uv sync --locked
export SECRET_KEY='replace-with-a-long-random-secret'
export DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@localhost:5432/DATABASE'
uv run alembic -c alembic.ini upgrade head
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## Tests

The Docker-based pytest suite currently passes. Run it from the repository root:

```bash
docker compose run --build --rm test
```

The suite uses an isolated PostgreSQL test database and covers authentication, account operations, training sessions and questions, ownership checks, deletion behavior, and transaction handling. See [backend/README.md#tests](backend/README.md#tests) for local test setup.

## Current Limitations

- Only the `simple_blind` training question type is implemented.
- Audio upload and playback are outside the backend's current scope.
- Today and weekly statistics routes are not implemented.
- Expired refresh token records are not removed by a scheduled job.
- Profile images use local storage. Cloud object storage is planned if usage grows.
- Personalized EQ recommendations based on device, preferences, and feedback are planned.
- The project has not been deployed.
