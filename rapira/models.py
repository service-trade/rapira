# -*- coding: utf-8 -*-
from persistent import Persistent
from persistent.mapping import PersistentMapping


from pyramid.security import (Allow, Everyone,)

class WikiStore(PersistentMapping):
    __parent__ = __name__ = None
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]


class WikiPage(Persistent):
    def __init__(self, data):
        self.data = data


def appmaker(zodb_root):
#    if 'app_root' in zodb_root:
#        zodb_root['wiki_root'] = zodb_root.pop('app_root')

    if not 'wiki_root' in zodb_root:
        wiki_root = WikiStore()
        frontpage = WikiPage(u'Это начальная страница.')
        wiki_root['FrontPage'] = frontpage
        frontpage.__name__ = 'FrontPage'
        frontpage.__parent__ = wiki_root
        zodb_root['wiki_root'] = wiki_root
        import transaction
        transaction.commit()

    return zodb_root['wiki_root']
