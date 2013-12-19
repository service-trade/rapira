# -*- coding: utf-8 -*-
from sqlalchemy import (CHAR, Column, ForeignKey, Index, Integer, PrimaryKeyConstraint, String, Table, Text,)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (backref, relationship, scoped_session, sessionmaker,)
from sqlalchemy.exc import DataError
from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.security import (Allow, Everyone,)


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


##############################################################################
# Кореневой контейнер дерева ресурсов
class AppDataStore(dict):
    __parent__ = __name__ = None


##############################################################################
# Таблица сопоставления многие-ко-многим между ярлыками.
nn_tag2tag_table = Table(
    'nn_tag2tag',
    Base.metadata,

    Column('parent_id',
           Integer,
           ForeignKey('tag.id'), nullable=False),
    Column('child_id',
           Integer,
           ForeignKey('tag.id'), nullable=False),

    PrimaryKeyConstraint('parent_id', 'child_id'),
)


##############################################################################
# Модель для ярлыков
class Tag(Base):
    __tablename__ = 'tag'

    id       = Column(Integer, primary_key=True)
    name     = Column(String(255), unique=True)
    children = relationship('Tag',
                            secondary     = 'nn_tag2tag',
                            backref       = 'parents',
                            primaryjoin   = id==nn_tag2tag_table.c.parent_id,
                            secondaryjoin = id==nn_tag2tag_table.c.child_id,)


##############################################################################
# Контейнер для тэгов.
class TagContainer(object):
    __parent__ = None
    __name__ = u"каталог-ярлыков"
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, parent):
        self.__parent__ = parent

    def __getitem__(self, key):
        try:
            key = int(key)
        except ValueError:
            raise KeyError

        entity = DBSession.query(Tag).filter_by(id=key).first()
        if entity is None: raise KeyError

        entity.__name__ = entity.id
        entity.__parent__ = self

        return entity

    def __setitem__(self, key, value):
        DBSession.add(value)


##############################################################################
# Модель вики-страницы
class WikiPage(Base):
    __tablename__ = 'wiki_page'

    id   = Column(Integer,     primary_key=True)
    name = Column(String(255), unique=True)
    data = Column(Text)


##############################################################################
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


##############################################################################
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


##############################################################################
# Модель для заказчика-физлица.
class ClientPerson(Client):
    passport = Column(String(255))

    __mapper_args__ = {'polymorphic_identity': 'PRSN'}


##############################################################################
# Таблица сопоставления многие-ко-многим между фирмами и точками фирм.
nn_client_firm2facility_table = Table(
    'nn_client_firm2facility',
    Base.metadata,

    Column('client_firm_id',
           Integer,
           ForeignKey('client.id'), nullable=False),
    Column('client_firm_facility_id',
           Integer,
           ForeignKey('client_firm_facility.id'), nullable=False),
    PrimaryKeyConstraint('client_firm_id', 'client_firm_facility_id'),
)

##############################################################################
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


######################№#######################################################
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


##############################################################################
# Модель для точки (объекта) фирмы-заказчика.
class ClientFirmFacility(Base):
    __tablename__ = 'client_firm_facility'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    address = Column(String(255))


#######################№№#####################################################
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

    tags_section = TagContainer(app_root)
    app_root[tags_section.__name__] = tags_section

    wiki_section = WikiContainer(app_root)
    app_root[wiki_section.__name__] = wiki_section

    client_section = ClientContainer(app_root)
    app_root[client_section.__name__] = client_section

    facility_section = ClientFirmFacilityContainer(app_root)
    app_root[facility_section.__name__] = facility_section

    import transaction
    transaction.commit()

    return app_root
