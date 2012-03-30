import re

from django.shortcuts import render_to_response, get_object_or_404

from rfweb.rfwebapp.models import Suit
from rfweb.rfwebapp import utils


def suit(request, suitname):
    suit = get_object_or_404(Suit, name=suitname)
    suitdoc = SuitDoc(suit)
    return render_to_response('suit.html', {'suit': suitdoc })

class _DocHelper:
    # This code is adapted from libdoc.py, see
    # http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool

    _name_regexp = re.compile("`(.+?)`")

    def _get_htmldoc(self):
        doc = utils.html_escape(self._doc, formatting=True)
        return self._name_regexp.sub(self._link_keywords, doc)

    def _link_keywords(self, res):
        name = res.group(1)
        keywords = self.keywords if isinstance(self, SuitDoc) else self._suit.keywords
        for kw in keywords:
            if utils.eq(name, kw.name):
                return '<a href="#%s" class="name">%s</a>' % (kw.name, name)
        if utils.eq_any(name, ['introduction', 'suit introduction']):
            return '<a href="#introduction" class="name">%s</a>' % name
        if utils.eq_any(name, ['importing', 'suit importing']):
            return '<a href="#importing" class="name">%s</a>' % name
        return '<span class="name">%s</span>' % name

    doc = property(_get_htmldoc)

class SuitDoc(_DocHelper):
    def __init__(self, suitdata):
        self.name = suitdata.name
        self.path = suitdata.path
        self._doc = suitdata.doc
        self.version = suitdata.version
        self.keywords = [ KeywordDoc(kwdata, self)
                          for kwdata in suitdata.keyword_set.all() ]
        self.tests = [ TestDoc(tcdata, self)
                          for tcdata in suitdata.test_set.all() ]
        '''
        self.tags = []
        for test in self.test:
            self.tags.extend([ TagDoc(tag, test, self) 
                                for tag in filter(lambda x: x.name == test.name, suitdata.tag_set.all()) ])
        assert self.tags[0]
        '''

class KeywordDoc(_DocHelper):
    def __init__(self, kwdata, suit):
        self.name = kwdata.name
        self.args = kwdata.args
        self._doc = kwdata.doc
        self.shortdoc = self._doc.split('\n')[0]
        self._suit = suit
 
class TestDoc(_DocHelper):
    def __init__(self, tcdata, suit):
        self.name = tcdata.name
        self._doc = tcdata.doc
        self.shortdoc = self._doc.split('\n')[0]
        self._suit = suit

'''
class TagDoc(_DocHelper):
    def __init__(self, tdata, test, suit):
        self.name = tdata.name
        self._test = test
        self._suit = suit
'''
