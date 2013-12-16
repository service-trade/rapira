#-*- coding: utf-8 -*-
import colander
from deform import Form, Button

from pyramid.httpexceptions import HTTPFound
from pyramid.view import (view_config, forbidden_view_config,)
from pyramid.security import (remember, forget, authenticated_userid,)

from rapira.security import USERS

##############################################################################
# Вьюхи для логина и выхода из системы

class LoginMappingSchema(colander.MappingSchema):
    login = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())


@view_config(context='rapira.models.AppDataStore',
             name='login',
             renderer='templates/rapira/common/login.jinja2')
@forbidden_view_config(renderer='templates/rapira/common/login.jinja2')
def login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url: referrer = '/' # never use the login
                                              # form itself as came_from

    came_from = request.params.get('came_from', referrer)
    message = ''
    logindata = {'login': '', 'password': ''}
    login_form = Form(LoginMappingSchema(),
                      buttons=(
                          Button(name="form.submitted", title=u"Войти"),
                      ))

    add_req = login_form.get_widget_requirements()

    if 'form.submitted' in request.params:
        try:
            logindata = login_form.validate(request.POST.items())
        except ValidationFalure, e:
            message = u'Введены некорректные данные!'
            return dict(
                message = message,
                url = request.application_url + '/login',
                came_from = came_from,
                login_form = login_form.render({'login': login,
                                                'password': password}),
                add_req = add_req,
                )
        if USERS.get(logindata['login']) == logindata['password']:
            headers = remember(request, logindata['login'])
            return HTTPFound(location = came_from,
                             headers = headers)

        message = u'Неверное имя пользователя или пароль!'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login_form = login_form.render(logindata),
        add_req = add_req,
        )

@view_config(context='rapira.models.AppDataStore', name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.resource_url(request.context),
                     headers = headers)