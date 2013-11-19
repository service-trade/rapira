# -*- coding: utf-8 -*-
from persistent import Persistent
from persistent.mapping import PersistentMapping


class WikiStore(PersistentMapping):
    __parent__ = __name__ = None


class WikiPage(Persistent):
    def __init__(self, data):
        self.data = data


def appmaker(zodb_root):
    if 'app_root' in zodb_root:
        zodb_root['wiki_root'] = zodb_root.pop('app_root')

    if not 'wiki_root' in zodb_root:
        app_root = WikiStore()
        frontpage = WikiPage(u'Это начальная страница.')
        app_root['FrontPage'] = frontpage
        frontpage.__name__ = 'FrontPage'
        frontpage.__parent__ = app_root
        zodb_root['wiki_root'] = app_root
        import transaction
        transaction.commit()

    return zodb_root['wiki_root']
