import pytest
from sqlalchemy.exc import IntegrityError

from auth.service import is_email_unique_violation


def integrity_error(original):
    return IntegrityError('INSERT INTO users ...', {}, original)


@pytest.mark.parametrize('constraint_name', [None, 'uq_users_email'])
def test_email_unique_violation_uses_postgres_constraint_name(constraint_name):
    class PostgresUniqueViolation(Exception):
        sqlstate = '23505'

    original = PostgresUniqueViolation(
        'duplicate key value violates unique constraint "uq_users_email"'
    )
    if constraint_name is not None:
        original.constraint_name = constraint_name

    assert is_email_unique_violation(integrity_error(original)) is True


def test_other_postgres_unique_constraint_is_not_an_email_duplicate():
    class PostgresUniqueViolation(Exception):
        constraint_name = 'uq_users_username'

    error = integrity_error(
        PostgresUniqueViolation('duplicate key violates unique constraint "uq_users_username"')
    )

    assert is_email_unique_violation(error) is False