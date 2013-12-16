#-*- coding: utf-8 -*-
from docutils.core import publish_parts
import re
import colander
from deform import Form, Button

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from rapira.models import WikiPage

##############################################################################
# Вьюхи для wiki

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(context='rapira.models.WikiContainer')
def view_wiki(context, request):
    return HTTPFound(location=request.resource_url(context, 'frontpage'))

@view_config(context='rapira.models.WikiPage',
             renderer='templates/rapira/wiki/view.jinja2',
             permission='view')
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
    return dict(page = context, content = content, edit_url = edit_url,
                logged_in = authenticated_userid(request))

@view_config(name='add_page',
             context='rapira.models.WikiContainer',
             renderer='templates/rapira/wiki/edit.jinja2',
             permission='edit')
def add_page(context, request):
    pagename = request.subpath[0]
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = WikiPage(name=pagename, data=body)
        page.__name__ = pagename
        page.__parent__ = context
        context[pagename] = page
        return HTTPFound(location = request.resource_url(page))
    save_url = request.resource_url(context, 'add_page', pagename)
    page = WikiPage(name='', data='')
    page.__name__ = pagename
    page.__parent__ = context
    return dict(page = page, save_url = save_url,
                logged_in = authenticated_userid(request))

@view_config(name='edit_page',
             context='rapira.models.WikiPage',
             renderer='templates/rapira/wiki/edit.jinja2',
             permission='edit')
def edit_page(context, request):
    if 'form.submitted' in request.params:
        context.data = request.params['body']
        return HTTPFound(location = request.resource_url(context))

    return dict(page=context,
                save_url=request.resource_url(context, 'edit_page'),
                logged_in = authenticated_userid(request))