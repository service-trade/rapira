#-*- coding: utf-8 -*-
import colander
from deform import Form, Button
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from rapira.models import (DBSession, Tag,)

##############################################################################
# Вьюхи для тэгов

@view_config(context='rapira.models.TagContainer', permission='view')
def view_tags(context, request):
    return HTTPFound(location=request.resource_url(context, '1'))

@view_config(context='rapira.models.Tag',
             renderer='templates/rapira/tags/view.jinja2',
             permission='view')
def view_tag(context, request):
    tag = context.__parent__

    content = context.name
    edit_url = request.resource_url(context, 'edit')
    return dict(
        tag       = context,
        edit_url  = edit_url,
        logged_in = authenticated_userid(request)
    )

@view_config(name='add',
             context='rapira.models.TagContainer',
             renderer='templates/rapira/tags/edit.jinja2',
             permission='edit')
def add_tag_page(context, request):
    if 'form.submitted' in request.params:
        tagname = request.params['tagname']
        tag = Tag(name=tagname)
        tag.__parent__ = context
        context[tagname] = tag
        DBSession.query(Tag).first()
        tag.__name__ = tag.id
        return HTTPFound(request.resource_url(tag))
    save_url = request.resource_url(context, 'add')
    tag = Tag(name='')
    tag.__name__ = None
    tag.__parent__ = context
    return dict(
        tag       = tag,
        save_url  = save_url,
        logged_in = authenticated_userid(request)
    )

@view_config(name='edit',
             context='rapira.models.Tag',
             renderer='templates/rapira/tags/edit.jinja2',
             permission='edit')
def edit_tag_page(context, request):
    if 'form.submitted' in request.params:
        tag = context
        tag.name = request.params['tagname']
        return HTTPFound(location = request.resource_url(tag))

    return dict(
        tag       = context,
        save_url  = request.resource_url(context, 'edit'),
        logged_in = authenticated_userid(request)
    )