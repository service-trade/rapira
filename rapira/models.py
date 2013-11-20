# -*- coding: utf-8 -*-
from persistent import Persistent
from persistent.mapping import PersistentMapping


from pyramid.security import (Allow, Everyone,)


class AppDataStore(PersistentMapping):
    __parent__ = __name__ = None


class WikiContainer(dict):
    __parent__ = None
    __name__ = "wiki"
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, parent):
        self.__parent__ = parent


class WikiPage(Persistent):
    def __init__(self, data):
        self.data = data


class EquipmentContainer(dict):
    __parent__ = None
    __name__ = u'оборудование'

    def __init__(self, parent):
        self.__parent__ = parent


class EquipmentType(Persistent):
    def __init__(self, name, parent):
        self.name = name
        self.__name__ = name
        self.__parent__ = parent

class EquipmentItem(Persistent):
    def __init__(self, serial_number, equipment_type, parent):
        self.__name__ = self.serial_number = serial_number
        self.type = equipment_type
        self.__parent__ = parent

def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = AppDataStore()

        wiki_root = WikiContainer(app_root)
        frontpage = WikiPage(u'Это начальная страница.')
        wiki_root['frontpage'] = frontpage
        frontpage.__name__ = 'frontpage'
        frontpage.__parent__ = wiki_root
        app_root[wiki_root.__name__] = wiki_root

        eqiupment_root = EquipmentContainer(app_root)
        eq_type = EquipmentType(u'весы', eqiupment_root)
        eqiupment_root[eq_type.__name__] = eq_type
        item = EquipmentItem('12345', eq_type, eqiupment_root)
        eqiupment_root[item.__name__] = item
        app_root[eqiupment_root.__name__] = eqiupment_root

        zodb_root['app_root'] = app_root

        import transaction
        transaction.commit()

    return zodb_root['app_root']
