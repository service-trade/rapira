from pyramid.config import Configurator

from .models import (
    DBSession,
    Base,
    resource_tree_factory,
    )

from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .security import groupfinder


def root_factory(request):
    return resource_tree_factory()

def configure_db_engine(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

def main(global_config, **settings):
    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    configure_db_engine(settings)

    config = Configurator(root_factory=root_factory, settings=settings)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.scan()

    #config.include('deform_jinja2')
    #config.include('deform_bootstrap_extra')

    return config.make_wsgi_app()
