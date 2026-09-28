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