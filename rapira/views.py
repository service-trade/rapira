#-*- coding: utf-8 -*-
from docutils.core import publish_parts
import re
import colander
from deform import Form, Button

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from pyramid.view import (view_config, forbidden_view_config,)
from pyramid.security import (remember, forget, authenticated_userid,)

from .security import USERS
from .models import WikiPage


class LoginMappingSchema(colander.MappingSchema):
    login = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())


@view_config(context='.models.AppDataStore', name='login', renderer='templates/rapira/login.jinja2')
@forbidden_view_config(renderer='templates/rapira/login.jinja2')
def login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url: referrer = '/' # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)
    message = ''
    logindata = {'login': '', 'password': ''}
    login_form = Form(LoginMappingSchema(), buttons=(Button(name="form.submitted", title=u"Войти"),))
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
                login_form = login_form.render({'login': login,  'password': password}),
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

@view_config(context='.models.AppDataStore', name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.resource_url(request.context), headers = headers)

@view_config(context='.models.AppDataStore')
def view_index(context, request):
    return HTTPFound(location=request.resource_url(context, 'wiki'))

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(context='.models.WikiContainer')
def view_wiki(context, request):
    return HTTPFound(location=request.resource_url(context, 'frontpage'))

@view_config(context='.models.WikiPage', renderer='templates/rapira/view.jinja2', permission='view')
def view_wiki_page(context, request):
    wiki = context.__parent__

    def check(match):
        word = match.group(1)
        if word in wiki:
            page = wiki[word]
            view_url = request.resource_url(page)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = request.application_url + '/add_page/' + word 
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(context.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = request.resource_url(context, 'edit_page')
    return dict(page = context, content = content, edit_url = edit_url, logged_in = authenticated_userid(request))

@view_config(name='add_page', context='.models.WikiContainer', renderer='templates/edit.pt', permission='edit')
def add_page(context, request):
    pagename = request.subpath[0]
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = WikiPage(pagename, body)
        page.__name__ = pagename
        page.__parent__ = context
        context[pagename] = page
        return HTTPFound(location = request.resource_url(page))
    save_url = request.resource_url(context, 'add_page', pagename)
    page = WikiPage('', '')
    page.__name__ = pagename
    page.__parent__ = context
    return dict(page = page, save_url = save_url, logged_in = authenticated_userid(request))

@view_config(name='edit_page', context='.models.WikiPage',
             renderer='templates/edit.pt', permission='edit')
def edit_page(context, request):
    if 'form.submitted' in request.params:
        context.data = request.params['body']
        return HTTPFound(location = request.resource_url(context))

    return dict(page=context,
                save_url=request.resource_url(context, 'edit_page'),
                logged_in = authenticated_userid(request))