"""View callables for the NIPSA API.

These view callables define a simple JSON API for managing a list of NIPSA'd
user IDs:

To get a list of all the NIPSA'd user IDs:

    GET /nipsa/user

To add user ID "acct:fred@hypothes.is" to the list:

    POST /nipsa/user/acct:fred@hypothes.is

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
from pyramid import view

from h.api.nipsa import models


@view.view_config(renderer='json', route_name='nipsa_user_index',
                  request_method='GET')
def user_index(_):
    """Return a list of all the NIPSA'd user IDs.

    :rtype: list of unicode strings

    """
    return models.user_index()


@view.view_config(renderer='json', route_name='nipsa_user',
                  request_method='PUT')
def user_create(request):
    """NIPSA a user.

    Add the given user's ID to the list of NIPSA'd user IDs.
    If the user is already NIPSA'd then nothing will happen.

    """
    user_id = request.matchdict["user_id"]
    models.user_create(user_id)

    if request.registry.feature("queue"):
        request.get_queue_writer().publish(
            "nipsa_user_requests",
            json.dumps({"action": "nipsa", "user_id": user_id}))
    return {"user_id": user_id}


@view.view_config(renderer='json', route_name='nipsa_user',
                  request_method='DELETE')
def user_delete(request):
    """Un-NIPSA a user.

    If the user isn't NIPSA'd then nothing will happen.

    """
    user_id = request.matchdict["user_id"]
    models.user_delete(user_id)

    if request.registry.feature("queue"):
        request.get_queue_writer().publish(
            "nipsa_user_requests",
            json.dumps({"action": "unnipsa", "user_id": user_id}))


@view.view_config(renderer='json', route_name='nipsa_user',
                  request_method='GET')
def user_read(request):
    """Return 200 OK if the given user is on the NIPSA list, 404 if not."""
    user_id = models.user_read(request.matchdict["user_id"])
    if user_id:
        return user_id
    else:
        request.response.status = 404
        request.response.content_type = "application/json"
        return request.response


def includeme(config):
    config.add_route('nipsa_user_index', '/nipsa/user')
    config.add_route('nipsa_user', '/nipsa/user/{user_id}')
    config.scan()
