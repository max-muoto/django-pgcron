from __future__ import annotations

from unittest import mock

import pytest
from django.db import connection

import pgcron
from pgcron.tests.models import NameTestModel


def test_statement() -> None:
    """Test that a standard statement class works."""
    cursor = mock.Mock()
    statement = pgcron.SQLExpression("SELECT 1")
    assert statement.as_escaped_sql(cursor, "default") == "$$SELECT 1$$"
    assert statement.as_sql(cursor, "default") == "SELECT 1"


@pytest.mark.django_db
def test_delete() -> None:
    """Test that a delete class works."""
    delete = pgcron.Delete(NameTestModel.objects.all().filter(name="test"))
    with connection.cursor() as cursor:
        assert (
            delete.as_escaped_sql(cursor, "default")
            == '$$DELETE FROM "name_model" WHERE "name_model"."name" = \'test\'$$'
        )
        assert (
            delete.as_sql(cursor, "default")
            == 'DELETE FROM "name_model" WHERE "name_model"."name" = \'test\''
        )


@pytest.mark.django_db
def test_update() -> None:
    """Test that an update class works."""

    update = pgcron.Update(NameTestModel.objects.all().filter(name="test"), name="test2")
    with connection.cursor() as cursor:
        assert update.as_escaped_sql(cursor, "default") == (
            '$$UPDATE "name_model" SET "name" = \'test2\' ' 'WHERE "name_model"."name" = \'test\'$$'
        )
        assert update.as_sql(cursor, "default") == (
            'UPDATE "name_model" SET "name" = \'test2\' ' 'WHERE "name_model"."name" = \'test\''
        )
