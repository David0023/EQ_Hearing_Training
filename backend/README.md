# Backend

The backend provides the REST API for EQ Hearing Training. Users can create an account, manage their profile, and complete EQ listening exercises. A training session generates questions from its settings and stores answers and progress.

## Tech Stack

- Python 3.12+, FastAPI, and Pydantic
- SQLAlchemy 2 async ORM, PostgreSQL, and Alembic
- PyJWT for JWT handling and `pwdlib` for Argon2 password hashing
- Pillow for profile image validation and local file storage
- pytest and HTTPX

## Features

### Accounts and authentication

- Register, log in with email, view the current profile, and delete an account
- Upload or replace a profile image
- HS256-signed access tokens and refresh tokens in HttpOnly cookies
- Refresh token rotation: only a SHA-256 hash is stored in the database; each refresh revokes the old token and issues a new one
- Revoke the refresh token on logout

### Training

- Create, list, view, and delete training sessions
- Resume an unanswered question or generate the next question
- Submit answers, calculate correctness, and complete sessions
- View all questions and a progress summary for a session
- Retrieve available frequency groups and gain options

The only implemented question type is `simple_blind`. The backend validates the requested frequency and gain ranges, then randomly selects target values from the standard options within those ranges. Audio files are not uploaded to or served by the backend.

### Planned and incomplete features

- The today and weekly statistics routes exist, but their behavior has not been implemented.
- AI recommendations based on EQ preferences, playback devices, and user feedback are planned.
- Expired refresh tokens are rejected during authentication, but there is no scheduled job to remove expired records.

## Architecture and Request Flow

```text
backend/
├── main.py                   # FastAPI app, middleware, and router setup
├── api/v1/router.py          # /api/v1 router composition
├── auth/                     # Registration, login, tokens, and auth dependencies
├── user/                     # User API, service, repository, and model
├── storage/images/           # Image validation and local file operations
├── training/
│   ├── session/              # Session API, service, repository, and model
│   ├── question/             # Shared question API and lifecycle
│   │   └── types/            # Type-specific strategies and data models
│   ├── domain/               # Frequency/gain rules and question generation
│   └── info/                 # Training option endpoints
├── statistics/               # Statistics API (not implemented)
├── db/                       # Async SQLAlchemy setup and model registration
├── alembic/                  # Database migrations
└── tests/                    # API, service, and repository tests
```

Requests generally follow the Router → Service → Repository flow. Routers handle HTTP input and responses, services coordinate feature behavior and transactions, and repositories perform database queries and changes. Training rules and question generation live in `training/domain` and question-type strategies, independently of FastAPI.

Session-specific endpoints verify ownership. Question creation and answer submission lock the session row to prevent concurrent requests from overwriting the same progress state. Services own transaction commit and rollback. Repositories perform database operations without committing.

## Data Model

```mermaid
erDiagram
    USER ||--o{ TRAINING_SESSION : owns
    USER ||--o{ REFRESH_TOKEN : has
    TRAINING_SESSION ||--o{ TRAINING_QUESTION : contains
    TRAINING_QUESTION ||--o| SIMPLE_BLIND_QUESTION : details
```

- `users`: account information and profile image key
- `refresh_tokens`: token hash, expiration time, and revocation time
- `training_sessions`: owner, question count, status, timestamps, and session configuration including `question_plan`
- `training_questions`: question order, type, answer state, and correctness
- `simple_blind_questions`: target frequency/gain and the user's submitted values

Shared question state is stored separately from type-specific question data. Session settings are stored as a JSON column containing a `question_plan`; PostgreSQL uses JSONB for this column. Each question type stores its details in a type-specific table.

## Design Decisions

### Service-owned transactions

Repositories initially committed their own changes. Answering a question requires several repository operations, such as storing type-specific answer data, updating shared question state, and possibly completing the session. Committing after each repository call made the overall operation impossible to roll back as one unit if a later step failed. Transaction ownership was moved to the service layer so the full feature flow can commit or roll back together.

### Question-type strategies

`simple_blind` was the only question type when this structure was introduced, but multiple types were planned. As the API was made independent of specific question types, it became useful to group common type-specific behavior behind a strategy interface. The registry selects a strategy for settings validation, question generation, answer evaluation, and attaching type-specific data. This keeps the shared session and question flows readable as new types are added, without introducing strategies for types that do not exist yet.

### Separate tables for question types

The main concern was supporting additional question types without concentrating type checks and type-specific behavior in shared code. Storing all question data in JSON was considered, but would make shared code responsible for interpreting each type's payload. Separate detail tables make the model structure explicit. SQLAlchemy relationships connect the common question record to its type-specific details, while keeping each type's data in its own schema.

### Refresh token storage

Refresh tokens are generated as random values and only their SHA-256 hashes are stored in the database. The raw token is delivered in an HttpOnly cookie to reduce exposure to client-side scripts. During refresh, the old token is revoked and the new token is stored in one transaction. No additional policy for token reuse detection or revoking a token family has been implemented.

## API Overview

| Area | Endpoints | Description |
| --- | --- | --- |
| Authentication | `/auth/register`, `/auth/login` | Register and log in |
| Authentication | `/auth/refresh`, `/auth/logout` | Refresh the access token and log out |
| Users | `/api/v1/users/me` | View the current user or delete the account after password verification |
| Users | `/api/v1/users/profile/image` | Upload or replace the profile image |
| Training | `/api/v1/training/sessions` | Create a session or list recent sessions |
| Training | `/api/v1/training/sessions/{id}` | View or delete a session |
| Questions | `/api/v1/training/sessions/{id}/questions/resume` | Resume an unanswered question or generate one |
| Questions | `/api/v1/training/sessions/{id}/questions/{question_id}` | Submit an answer |
| Training info | `/api/v1/training/infos/frequency/groups` | List frequency groups |
| Training info | `/api/v1/training/infos/gain/options` | List gain options |

Interactive API documentation is available at `/docs` when the server is running.

## Run Locally

### Docker Compose

From the repository root:

```bash
docker compose up --build
```

The Compose setup starts PostgreSQL, applies Alembic migrations, and starts the API at `http://localhost:8000`.

### Local Python Environment

Start PostgreSQL, then install dependencies and configure the environment from `backend/`:

```bash
cd backend
uv sync --locked
export SECRET_KEY='replace-with-a-long-random-secret'
export DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@localhost:5432/DATABASE'
uv run alembic -c alembic.ini upgrade head
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Profile images are stored in `uploads/` by default. Set `LOCAL_UPLOAD_DIR` to change the location. For a public deployment, configure `COOKIE_SECURE` and `FRONTEND_ORIGINS` for the HTTPS domain. Local file storage is currently sufficient for the expected small user base; moving profile images to cloud storage is planned as usage grows.

## Tests

Run the Docker-based test suite from the repository root:

```bash
docker compose run --build --rm test
```

To run tests locally, install the development dependencies from `backend/` and set `TEST_DATABASE_URL` to a dedicated PostgreSQL database whose name includes `test`:

```bash
cd backend
uv sync --locked --group dev
TEST_DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@localhost:5432/eq_hearing_test' \
  uv run --locked --group dev python -m pytest -q
```

Tests use isolated PostgreSQL schemas and cover account/authentication flows, session and question workflows, ownership checks, deletion behavior, and transaction behavior. The Docker-based pytest suite is currently passing.

## Limitations and Next Steps

- Add scheduled cleanup for expired or revoked refresh token records.
- Implement today and weekly statistics.
- Build EQ recommendations using user preferences, playback devices, and feedback.
- Move profile image storage to a cloud object store as usage grows.
- Deploy the service and document its production environment and operating procedures. The project is not deployed yet.
