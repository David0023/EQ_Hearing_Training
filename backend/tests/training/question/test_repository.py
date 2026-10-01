import pytest

from db import database
from tests.training.helpers import BASE, create_session

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize('count', [1, 10])
async def test_question_deletion_preserves_other_rows(client, headers, count):
    from training.question import repository as question_repository
    from training.question.model import TrainingQuestion

    first = await create_session(client, headers)
    second = await create_session(client, headers)
    keep = (await client.post(f'{BASE}/sessions/{first}/questions', headers=headers)).json()['question']['id']
    target = (await client.post(f'{BASE}/sessions/{second}/questions', headers=headers)).json()['question']['id']
    async with database.SessionLocal() as db:
        deleted = await question_repository.delete_these(
            db, TrainingQuestion.id == target, count=count, flush=True,
        )
        assert deleted == 1
        assert [q.id for q in await question_repository.get_all(db)] == [keep]
        await db.rollback()
    async with database.SessionLocal() as db:
        assert [q.id for q in await question_repository.get_all(db)] == [keep, target]
        await question_repository.delete_these(db, TrainingQuestion.id == target, count=count)
        await db.commit()
    async with database.SessionLocal() as db:
        assert [q.id for q in await question_repository.get_all(db)] == [keep]
