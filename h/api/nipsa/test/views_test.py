import json
from mock import patch
from mock import Mock
from mock import MagicMock
from pyramid.testing import DummyRequest

from h.api.nipsa import views


@patch("h.api.nipsa.views.NipsaUser")
def test_user_index_with_no_users(NipsaUser):
    NipsaUser.all.return_value = []

    assert views.user_index(DummyRequest()) == []


@patch("h.api.nipsa.views.NipsaUser")
def test_user_index_with_one_user(NipsaUser):
    nipsa_user = Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.all.return_value = [nipsa_user]

    assert views.user_index(DummyRequest()) == ["test_id"]


@patch("h.api.nipsa.views.NipsaUser")
def test_user_index_with_multiple_users(NipsaUser):
    nipsa_user1 = Mock()
    nipsa_user1.user_id = "test_id1"
    nipsa_user2 = Mock()
    nipsa_user2.user_id = "test_id2"
    nipsa_user3 = Mock()
    nipsa_user3.user_id = "test_id3"
    NipsaUser.all.return_value = [nipsa_user1, nipsa_user2, nipsa_user3]

    assert views.user_index(DummyRequest()) == [
        "test_id1", "test_id2", "test_id3"]


@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_create_gets_id_from_matchdict(NipsaUser, _):
    request = MagicMock()
    request.matchdict.__getitem__.return_value = "test_id"

    views.user_create(request)

    request.matchdict.__getitem__.assert_called_once_with("user_id")


@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_create_gets_user_by_id(NipsaUser, _):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    views.user_create(request)

    NipsaUser.get_by_id.assert_called_once_with("test_id")


@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_create_does_not_add_when_user_already_exists(NipsaUser, Session):
    """
    user_create() should not call Session.add() if the user already exists.
    """
    nipsa_user = Mock()
    NipsaUser.get_by_id.return_value = nipsa_user
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    views.user_create(request)

    assert not Session.add.called


@patch("h.api.nipsa.views._publish")
@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_create_publishes_when_user_already_exists(
        NipsaUser, Session, _publish):
    """
    Even if the user is already NIPSA'd, user_create() should still publish a
    "nipsa" message to the queue.
    """
    nipsa_user = Mock()
    NipsaUser.get_by_id.return_value = nipsa_user
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    views.user_create(request)

    _publish.assert_called_once_with(
        request, json.dumps({"action": "nipsa", "user_id": "test_id"}))
    NipsaUser.get_by_id.assert_called_once_with("test_id")


@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_create_adds_user_if_user_does_not_exist(NipsaUser, Session):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    nipsa_user = Mock()
    NipsaUser.return_value = nipsa_user

    NipsaUser.get_by_id.return_value = None

    views.user_create(request)

    NipsaUser.assert_called_once_with("test_id")
    Session.add.assert_called_once_with(nipsa_user)


@patch("h.api.nipsa.views._publish")
@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_create_publishes_if_user_does_not_exist(
        NipsaUser, Session, _publish):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    nipsa_user = Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.return_value = nipsa_user

    NipsaUser.get_by_id.return_value = None

    views.user_create(request)

    _publish.assert_called_once_with(
        request, json.dumps({"action": "nipsa", "user_id": "test_id"}))


@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_delete_gets_id_from_matchdict(NipsaUser, _):
    request = MagicMock()
    request.matchdict.__getitem__.return_value = "test_id"

    views.user_delete(request)

    request.matchdict.__getitem__.assert_called_once_with("user_id")


@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_delete_gets_user_by_id(NipsaUser, _):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    views.user_delete(request)

    NipsaUser.get_by_id.assert_called_once_with("test_id")


@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_delete_does_not_delete_user_that_does_not_exist(
        NipsaUser, Session):
    """
    user_delete() should not call Session.delete() if the user isn't NIPSA'd.
    """
    NipsaUser.get_by_id.return_value = None
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    views.user_delete(request)

    assert not Session.delete.called


@patch("h.api.nipsa.views._publish")
@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_delete_publishes_when_user_does_not_exist(
        NipsaUser, Session, _publish):
    """
    Even if the user is not NIPSA'd, user_delete() should still publish an
    "unnipsa" message to the queue.
    """
    NipsaUser.get_by_id.return_value = None
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    views.user_delete(request)

    _publish.assert_called_once_with(
        request, json.dumps({"action": "unnipsa", "user_id": "test_id"}))


@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_delete_deletes_user(NipsaUser, Session):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    nipsa_user = Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.get_by_id.return_value = nipsa_user

    views.user_delete(request)

    Session.delete.assert_called_once_with(nipsa_user)


@patch("h.api.nipsa.views._publish")
@patch("h.api.nipsa.views.Session")
@patch("h.api.nipsa.views.NipsaUser")
def test_user_delete_publishes_if_user_exists(
        NipsaUser, Session, _publish):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    nipsa_user = Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.get_by_id.return_value = nipsa_user

    views.user_delete(request)

    _publish.assert_called_once_with(
        request, json.dumps({"action": "unnipsa", "user_id": "test_id"}))


@patch("h.api.nipsa.views.NipsaUser")
def test_user_read_gets_id_from_matchdict(_):
    request = MagicMock()

    views.user_read(request)

    request.matchdict.__getitem__.assert_called_once_with("user_id")


@patch("h.api.nipsa.views.NipsaUser")
def test_user_read_gets_user_by_id(NipsaUser):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    views.user_read(request)

    NipsaUser.get_by_id.assert_called_once_with("test_id")


@patch("h.api.nipsa.views.NipsaUser")
def test_user_read_returns_user_id_if_user_is_nipsad(NipsaUser):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    nipsa_user = Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.get_by_id.return_value = nipsa_user

    assert views.user_read(request) == "test_id"


@patch("h.api.nipsa.views.NipsaUser")
def test_user_read_returns_404_if_user_is_not_nipsad(NipsaUser):
    request = Mock()
    request.matchdict = {"user_id": "test_id"}

    NipsaUser.get_by_id.return_value = None

    assert views.user_read(request).status == 404
