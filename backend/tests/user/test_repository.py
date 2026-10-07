import pytest
from sqlalchemy.exc import IntegrityError

from user import repository as user_repository

pytestmark = pytest.mark.anyio


async def test_user_creation_repository(headers, db_session):
    # DB Constraint will raise Integrity Error for duplicate email.
    with pytest.raises(IntegrityError):
        await user_repository.create(
            db_session, 'tester@example.com', 'duplicate', 'hash', flush=True
        )

    await db_session.rollback()
    created = await user_repository.create(
        db_session, 'fresh@example.com', 'fresh', 'hash', flush=True
    )
    await db_session.commit()
    assert created.id is not None


async def test_user_lookup_returns_none_for_missing_email(headers, db_session):
    from user.model import User

    user = await user_repository.get_one(db_session, User.email == 'missing@example.com')
    assert user is None


async def test_user_update_only_accepts_account_fields(headers, db_session):
    from user.model import User

    user = await user_repository.get_one(db_session, User.email == 'tester@example.com')
    updated = await user_repository.update(
        db_session, user, flush=True, username='renamed', email='renamed@example.com'
    )
    assert updated.username == 'renamed'
    assert updated.email == 'renamed@example.com'

    with pytest.raises(ValueError, match='Cannot update fields: id'):
        await user_repository.update(db_session, user, id=999)


async def test_delete_missing_user_is_a_noop(headers, db_session):
    assert await user_repository.delete_this(db_session, None, flush=True) is False
