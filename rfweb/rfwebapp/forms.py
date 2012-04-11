from django import forms
from models import LOG_TYPE
from django.forms.util import ErrorList
import robot
import os
from rfweb.rfwebapp.models import Suite
 
class LogViewerForm(forms.Form):
    filter = forms.MultipleChoiceField(choices=LOG_TYPE, label="Show messages", required=True, initial=map(lambda x: x[0], LOG_TYPE))
    limit = forms.IntegerField(label=u'Limit', required=True, initial=20)

class SuiteData(object):
    def __init__(self, _tmpfile):
        try:
            self.testdata = robot.parsing.TestData(source=os.path.abspath(_tmpfile))
            self.name = self.testdata.name
            self.path = _tmpfile
            self.version = '1.0'
            self.doc = ''
        except Exception, e:
            if _tmpfile.split('.')[-1] in ('py',):
                raise Exception('Saving %s as a Python-library.' % _tmpfile)
            raise Exception('Given file does not contain valid XML: %s.' % e)
        self.keywords = self.testdata.keywords
        self.tests = []
        if self.testdata.has_tests():
            self.tests = self.testdata.testcase_table.tests

class UploadFileForm(forms.Form):
    file = forms.FileField()
    file.widget.attrs['size'] = 40
    override = forms.BooleanField(required=False)

    def parse_kw_spec(self, _tmpfile, override):
        try:
            suitdata = SuiteData(_tmpfile)
            if Suite.objects.filter(name=suitdata.name):
                if not override:
                    raise Exception("Suite %s already exists." % suitdata.name)
                else:
                    Suite.objects.filter(name=suitdata.name).delete()
            suit = Suite(name=suitdata.name, doc=suitdata.doc, version=suitdata.version, path=_tmpfile)
            suit.save()
            for kw in suitdata.keywords:
                suit.keyword_set.create(name=kw.name, doc=kw.doc.value, args=' | '.join(map(str, kw.args.value)))
            for tc in suitdata.tests:
                suit.test_set.create(name=tc.name, doc=tc.doc.value)
        except Exception, err:
            self._errors['file'] = ErrorList([str(err)])
            return None
        return suit.name

