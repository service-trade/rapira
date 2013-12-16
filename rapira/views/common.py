#-*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

##############################################################################
# Вьюха заглавной страницы

@view_config(context='rapira.models.AppDataStore')
def view_index(context, request):
    return HTTPFound(location=request.resource_url(context, 'wiki'))
