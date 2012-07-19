from django import forms
from models import LOG_TYPE
from django.forms.util import ErrorList
import robot
import os
from rfweb.rfwebapp.models import Suite, Keyword, Test, Variable
 
class LogViewerForm(forms.Form):
    filter = forms.MultipleChoiceField(choices=LOG_TYPE, label="Show messages", required=True, initial=map(lambda x: x[0], LOG_TYPE))
    limit = forms.IntegerField(label=u'Limit', required=True, initial=20)
    host = forms.CharField(label=u'Host', max_length=15, required=False)
    task = forms.CharField(label=u'Task name', max_length=80, required=False)
    test = forms.CharField(label=u'Test name', max_length=80, required=False)
    suite = forms.CharField(label=u'Suite name', max_length=80, required=False)

class SuiteData(object):
    def __init__(self, _tmpfile):
        try:
            self.testdata = robot.parsing.TestData(source=os.path.abspath(_tmpfile))
            self.variables = self.testdata.variable_table.variables
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
            suitedata = SuiteData(_tmpfile)
            suite = None
            if Suite.objects.filter(name=suitedata.name):
                if not override:
                    raise Exception("Suite %s already exists." % suitedata.name)
                else:
                    suite = Suite.objects.get(name=suitedata.name)
            if not suite:
                suite = Suite(name=suitedata.name, doc=suitedata.doc, version=suitedata.version, path=_tmpfile)
            suite.doc = suitedata.doc
            suite.version = suitedata.version
            suite.path = _tmpfile
            suite.save()
            for kw in suitedata.keywords:
                keyword = None
                try:
                    keyword = Keyword.objects.get(suite=suite.id, name=kw.name)
                except Exception, e:
                    pass
                if not keyword:
                    suite.keyword_set.create(name=kw.name, doc=kw.doc.value, args=', '.join(map(str, kw.args.value)))
                else:
                    keyword.doc = kw.doc.value
                    keyword.args = ', '.join(map(str, kw.args.value))
                    keyword.save()
            for tc in suitedata.tests:
                test = None
                try:
                    test = Test.objects.get(suite=suite.id, name=tc.name)
                except Exception, e:
                    pass
                if not test:
                    suite.test_set.create(name=tc.name, doc=tc.doc.value)
                else:
                    test.doc = tc.doc.value
                    test.save()
            for vr in suitedata.variables:
                variable = None
                comment = len(vr.comment._comment) > 0 and vr.comment._comment[0] or None
                value = ', '.join(map(str, vr.value))
                try:
                    variable = Variable.objects.get(suite=suite.id, name=vr.name)
                except Exception, e:
                    pass
                if not variable:
                    suite.variable_set.create(name=vr.name, value=value, comment=comment)
                else:
                    variable.value = value
                    variable.comment = comment
                    variable.save()
        except Exception, err:
            self._errors['file'] = ErrorList([str(err)])
            return None
        return suite.name

