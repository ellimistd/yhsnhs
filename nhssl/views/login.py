from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import find_root
from pyramid.security import remember
from pyramid.security import forget
from pyramid.view import view_config
from pyramid.url import resource_url
from pyramid.renderers import get_renderer
from pyramid.security import authenticated_userid
import hashlib

@view_config(context='nhssl.resources.NHSSL', name='login',
             renderer='nhssl:templates/login.pt')
@view_config(context='pyramid.exceptions.Forbidden',
             renderer='nhssl:templates/login.pt')
def login(request):
    login_url = resource_url(request.context, request, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    oldpassword = ''
    main = get_renderer('../templates/master.pt').implementation()
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params["password"]
        oldpassword = password
        password = hashlib.sha1(password.encode('UTF-8')).digest()
        app = find_root(request.context)
        USERS = app["users"]
        if not USERS.get(login):
           return dict(message = "That username failed <br/> You either made a typo <br/> or must register",
                       url = request.application_url + '/login',
                       came_from = came_from,
                       login = login,
                       password = oldpassword,
                       name = 'Login',
                       main = main )
        elif USERS.get(login).password != password:
           return dict(message = "Password incorrect <br/> Either retry or contact <br/> administrators",
                       url = request.application_url + '/login',
                       came_from = came_from,
                       login = login,
                       password = oldpassword,
                       name = 'Login',
                       main = main )
        elif USERS.get(login).password == password:
            if not hasattr(USERS.get(login), 'deactivated'):
                USERS.get(login).deactivated = False
            if USERS.get(login).deactivated:
                return dict(message = "You've done something wrong <br/> and now this account has been <br/> deactivated",
                           url = request.application_url + '/login',
                           came_from = came_from,
                           login = login,
                           password = oldpassword,
                           name = 'Login',
                           main = main )
            else:
                headers = remember(request, login)
                return HTTPFound(location = came_from,
                                 headers = headers)
        message = 'Failed login'

    return dict(
        red = '',
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = oldpassword,
        name = 'Login',
        main = main )
    
@view_config(context='nhssl.resources.NHSSL', name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = resource_url(request.context, request),
                     headers = headers)
