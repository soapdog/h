from pytest import raises
from pytest import mark
from sqlalchemy.exc import IntegrityError

from h.api.nipsa.models import NipsaUser


@mark.usefixtures("db_session")
def test_init():
    nipsa_user = NipsaUser("test_id")
    assert nipsa_user.user_id == "test_id"


def test_get_by_id_with_matching_user(db_session):
    nipsa_user = NipsaUser("test_id")
    db_session.add(nipsa_user)

    assert NipsaUser.get_by_id("test_id") == nipsa_user


@mark.usefixtures("db_session")
def test_get_by_id_not_found():
    assert NipsaUser.get_by_id("does not exist") is None


@mark.usefixtures("db_session")
def test_all_with_no_rows():
    assert NipsaUser.all() == []


def test_all_with_one_row(db_session):
    nipsa_user = NipsaUser("test_id")
    db_session.add(nipsa_user)

    assert NipsaUser.all() == [nipsa_user]


def test_all_with_multiple_rows(db_session):
    nipsa_user1 = NipsaUser("test_id1")
    db_session.add(nipsa_user1)
    nipsa_user2 = NipsaUser("test_id2")
    db_session.add(nipsa_user2)
    nipsa_user3 = NipsaUser("test_id3")
    db_session.add(nipsa_user3)

    assert NipsaUser.all() == [nipsa_user1, nipsa_user2, nipsa_user3]


def test_two_rows_with_same_id(db_session):
    db_session.add(NipsaUser("test_id"))
    with raises(IntegrityError):
        db_session.add(NipsaUser("test_id"))
        db_session.flush()


def test_null_id(db_session):
    with raises(IntegrityError):
        db_session.add(NipsaUser(None))
        db_session.flush()
