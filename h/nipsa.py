from pyramid import view
from pyramid import httpexceptions


@view.view_config(route_name='nipsa_user', request_method='GET',
                  renderer='h:templates/nipsa_user.html')
def user_index(request):
    return {"user_ids": request.api_client.get("/nipsa/user")}


@view.view_config(route_name='nipsa_user', request_method='POST',
                  renderer='h:templates/nipsa_user.html')
def user_create(request):
    user_id = request.params["add"]
    request.api_client.put(u"/nipsa/user/" + user_id)
    return user_index(request)


@view.view_config(route_name='nipsa_user_delete', request_method='POST',
                  renderer='h:templates/nipsa_user.html')
def user_delete(request):
    user_id = request.params["remove"]
    request.api_client.delete(u"/nipsa/user/" + user_id)
    return httpexceptions.HTTPSeeOther(
        location=request.route_url("nipsa_user"))


def includeme(config):
    config.add_route('nipsa_user', '/nipsa/user')
    config.add_route('nipsa_user_delete', '/nipsa/user/delete')
    config.scan(__name__)
