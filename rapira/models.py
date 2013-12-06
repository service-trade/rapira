# -*- coding: utf-8 -*-
from sqlalchemy import (
    Table,
    Column,
    PrimaryKeyConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    CHAR,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

from pyramid.security import (Allow, Everyone,)


###############################################################################
# Кореневой контейнер дерева ресурсов
class AppDataStore(dict):
    __parent__ = __name__ = None


###############################################################################
# Модель вики-страницы
class WikiPage(Base):
    __tablename__ = 'wiki_page'

    id   = Column(Integer,     primary_key=True)
    name = Column(String(255), unique=True)
    data = Column(Text)


###############################################################################
# Контейнер для вики-страниц
class WikiContainer(object):
    __parent__ = None
    __name__ = "wiki"
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, parent):
        self.__parent__ = parent

    def __getitem__(self, pagename):
        page = DBSession.query(WikiPage).filter_by(name=pagename).first()
        if page is None:
            raise KeyError

        page.__name__   = page.name
        page.__parent__ = self

        return page

    def __setitem__(self, key, value):
        DBSession.add(value)


###############################################################################
# Базовая модель заказчика
class Client(Base):
    __tablename__ = 'client'

    discriminator = Column('type', CHAR(4))

    id            = Column(Integer,     primary_key=True)
    label_name    = Column(String(255), unique=True, nullable=False)
    legal_title   = Column(String(255), nullable=False)
    contacts      = Column(String(255))
    bank_accounts = Column(String(255))
    remarks       = Column(Text)

    __mapper_args__ = {'polymorphic_on': discriminator}


###############################################################################
# Модель для заказчика-физлица.
class ClientPerson(Client):
    passport = Column(String(255))

    __mapper_args__ = {'polymorphic_identity': 'PRSN'}


###############################################################################
# Таблица сопоставления многие-ко-многим между фирмами и точками фирм.
nn_client_firm2facility_table = Table(
    'nn_client_firm2facility',
    Base.metadata,

    Column('client_firm_id',
           Integer,
           ForeignKey('client.id')),
    Column('client_firm_facility_id',
           Integer,
           ForeignKey('client_firm_facility.id')),
    PrimaryKeyConstraint('client_firm_id', 'client_firm_facility_id'),
)

###############################################################################
# Модель для заказчика-ИП или юрлица.
class ClientFirm(Client):
    INN           = Column(Integer, unique=True)
    OGRN          = Column(Integer, unique=True)
    KPP           = Column(Integer, unique=True)
    legal_address = Column(String(255))
    facilities    = relationship('ClientFirmFacility',
                                 secondary='nn_client_firm2facility',
                                 backref="firms")

    __mapper_args__ = {'polymorphic_identity': 'FIRM'}


###############################################################################
# Контейнер для заказчиков.
class ClientContainer(object):
    __parent__ = None
    __name__ = "клиенты"
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, parent):
        self.__parent__ = parent

    def __getitem__(self, id):
        entity = DBSession.query(Client).filter_by(id=id).first()
        if entity is None:
            raise KeyError

        entity.__name__ = entity.id
        entity.__parent__ = self

        return entity

    def __setitem__(self, key, value):
        DBSession.add(value)


###############################################################################
# Модель для точки (объекта) фирмы-заказчика.
class ClientFirmFacility(Base):
    __tablename__ = 'client_firm_facility'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    address = Column(String(255))


#class nn_client_firm2facility(Base):
#    __tablename__ = 'nn_client_firm2facility'
#
#    id = Column(Integer, primary_key=True)
#    client_firm_id = Column(Integer, ForeignKey('client.id'))
#    client_firm_facility_id = Column(
#        Integer, ForeignKey('client_firm_facility.id')
#    )

###############################################################################
# Контейнер для точек фирм-заказчиков.
class ClientFirmFacilityContainer(object):
    __parent__ = None
    __name__ = "точки"
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, parent):
        self.__parent__ = parent

    def __getitem__(self, id):
        entity = DBSession.query(ClientFirmFacility).filter_by(id=id).first()
        if entity is None:
            raise KeyError

        entity.__name__ = entity.id
        entity.__parent__ = self

        return entity

    def __setitem__(self, key, value):
        DBSession.add(value)


def resource_tree_factory():
    app_root = AppDataStore()

    wiki_section = WikiContainer(app_root)
    app_root[wiki_section.__name__] = wiki_section

    client_section = ClientContainer(app_root)
    app_root[client_section.__name__] = client_section

    facility_section = ClientFirmFacilityContainer(app_root)
    app_root[facility_section.__name__] = facility_section

    import transaction
    transaction.commit()

    return app_root
