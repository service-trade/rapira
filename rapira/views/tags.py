#-*- coding: utf-8 -*-
import colander
from deform import Form, Button
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from rapira.models import Tag

##############################################################################
# Вьюхи для тэгов

@view_config(context='rapira.models.TagContainer', permission='view')
def view_tags_list(context, request):
    return HTTPFound(location=request.resource_url(context, '1'))

@view_config(context='rapira.models.Tag',
             renderer='templates/rapira/tags/view.jinja2',
             permission='view')
def view_tag(context, request):
    tag = context.__parent__

    content = context.name
    edit_url = request.resource_url(context, 'edit_page')
    return dict(page = context, content = content, edit_url = edit_url,
                logged_in = authenticated_userid(request))
