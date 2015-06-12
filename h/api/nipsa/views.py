"""View callables for the NIPSA API.

These view callables define a simple JSON API for managing a list of NIPSA'd
user IDs:

To get a list of all the NIPSA'd user IDs:

    GET /nipsa/user

To add user ID "acct:fred@hypothes.is" to the list:

    PUT /nipsa/user/acct:fred@hypothes.is

To delete user ID "acct:fred@hypothes.is" from the list:

    DELETE /nipsa/user/acct:fred@hypothes.is

To ask whether user ID "acct:fred@hypothes.is" is on the list:

    GET /nipsa/user/acct:fred@hypothes.is

(returns 200 OK if the given user ID is on the list, 404 Not Found if not).

Note that these API endpoints would normally be deployed with an "/api/"
prefix, for for example <https://hypothes.is/api/nipsa/user> not
<https://hypothes.is/nipsa/user>.

"""
import json
import pyramid_basemodel
from pyramid import view

from h.api.nipsa.models import NipsaUser


@view.view_config(renderer='json', route_name='nipsa_user_index',
                  request_method='GET')
def user_index(_):
    """Return a list of all the NIPSA'd user IDs.

    :rtype: list of unicode strings

    """
    return [nipsa_user.user_id for nipsa_user in NipsaUser.all()]


@view.view_config(renderer='json', route_name='nipsa_user',
                  request_method='PUT')
def user_create(request):
    """NIPSA a user.

    Add the given user's ID to the list of NIPSA'd user IDs.
    If the user is already NIPSA'd then nothing will happen (but a "nipsa"
    message for the user will still be published to the queue).

    """
    user_id = request.matchdict["user_id"]

    nipsa_user = NipsaUser.get_by_id(user_id)
    if not nipsa_user:
        nipsa_user = NipsaUser(user_id)
        pyramid_basemodel.Session.add(nipsa_user)

    request.get_queue_writer().publish(
        "nipsa_user_requests",
        json.dumps({"action": "nipsa", "user_id": user_id}))


@view.view_config(renderer='json', route_name='nipsa_user',
                  request_method='DELETE')
def user_delete(request):
    """Un-NIPSA a user.

    If the user isn't NIPSA'd then nothing will happen (but an "unnipsa"
    message for the user will still be published to the queue).

    """
    user_id = request.matchdict["user_id"]

    nipsa_user = NipsaUser.get_by_id(user_id)
    if nipsa_user:
        pyramid_basemodel.Session.delete(nipsa_user)

    request.get_queue_writer().publish(
        "nipsa_user_requests",
        json.dumps({"action": "unnipsa", "user_id": user_id}))


@view.view_config(renderer='json', route_name='nipsa_user',
                  request_method='GET')
def user_read(request):
    """Return 200 OK if the given user is on the NIPSA list, 404 if not."""
    user_id = request.matchdict["user_id"]

    user_nipsa = NipsaUser.get_by_id(user_id)
    if user_nipsa:
        return user_nipsa.user_id
    else:
        request.response.status = 404
        request.response.content_type = "application/json"
        return request.response


def includeme(config):
    config.add_route('nipsa_user_index', '/nipsa/user')
    config.add_route('nipsa_user', '/nipsa/user/{user_id}')
    config.scan()
