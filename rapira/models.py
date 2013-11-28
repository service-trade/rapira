# -*- coding: utf-8 -*-
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

from pyramid.security import (Allow, Everyone,)


class AppDataStore(dict):
    __parent__ = __name__ = None


class WikiPage(Base):
    __tablename__ = 'wiki_page'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    data = Column(Text)

    def __init__(self, name, data):
        self.name = name
        self.__name__ = name
        self.data = data


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

        page.__name__ = page.name
        page.__parent__ = self

        return page

    def __setitem__(self, key, value):
        DBSession.add(value)


class LegalEntity(Base):
    __tablename__ = 'legal_entity'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    legal_title = Column(Text)
    inn = Column(Integer, unique=True)
    ogrn = Column(Integer, unique=True)

    def __init__(self, title, inn, ogrn):
        self.title = title
        self.inn = inn
        self.ogrn = ogrn

class LegalEntitiesContainer(object):
    __parent__ = None
    __name__ = "юрлица"
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, parent):
        self.__parent__ = parent

    def __getitem__(self, id):
        entity = DBSession.query(LegalEntity).filter_by(id=id).first()
        if entity is None:
            raise KeyError

        entity.__name__ = entity.id
        entity.__parent__ = self

        return entity

    def __setitem__(self, key, value):
        DBSession.add(value)



#class EquipmentContainer(object):
#    __parent__ = None
#    __name__ = u'оборудование'
#
#    def __init__(self, parent):
#        self.__parent__ = parent
#
#
#class EquipmentType(Persistent):
#    def __init__(self, name, parent):
#        self.name = name
#        self.__name__ = name
#        self.__parent__ = parent
#
#class EquipmentItem(Persistent):
#    def __init__(self, serial_number, equipment_type, parent):
#        self.__name__ = self.serial_number = serial_number
#        self.type = equipment_type
#        self.__parent__ = parent

def resource_tree_factory():
    app_root = AppDataStore()

    wiki_section = WikiContainer(app_root)
    app_root[wiki_section.__name__] = wiki_section

    equipment_section = EquipmentContainer(app_root)
    app_root[equipment_section.__name__] = equipment_section

    import transaction
    transaction.commit()

    return app_root
