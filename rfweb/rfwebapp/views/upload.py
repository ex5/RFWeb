from lxml.html import parse
import os
import robot
import tempfile

from django.shortcuts import render_to_response
from django import forms
from django.forms.util import ErrorList

from rfweb.rfwebapp.models import Suit
from settings import MEDIA_ROOT

def upload(request):
    suitname = None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            destination = os.path.join(MEDIA_ROOT, request.FILES['file'].name)
            handle_uploaded_file(request.FILES['file'], destination)
            suitname = form.parse_kw_spec(destination, form.cleaned_data['override'])
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form, 'suitname': suitname})

def handle_uploaded_file(f, destination):
    destination = open(destination, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

class UploadFileForm(forms.Form):
    file = forms.FileField()
    file.widget.attrs['size'] = 40
    override = forms.BooleanField(required=False)

    def parse_kw_spec(self, _tmpfile, override):
        try:
            suitdata = SuitData(_tmpfile)
            if Suit.objects.filter(name=suitdata.name):
                if not override:
                    raise Exception("Suit %s already exists." % suitdata.name)
                else:
                    Suit.objects.filter(name=suitdata.name).delete()
            suit = Suit(name=suitdata.name, doc=suitdata.doc, version=suitdata.version)
            suit.save()
            for kw in suitdata.keywords:
                suit.keyword_set.create(name=kw.name, doc=kw.doc.value, args=' | '.join(map(str, kw.args.value)))
            for tc in suitdata.tests:
                suit.test_set.create(name=tc.name, doc=tc.doc.value)
                '''
                for tag in tc.tags.as_list()[1:]:
                    suit.tag_set.create(name=tag, test=tc)
                '''
        except Exception, err:
            self._errors['file'] = ErrorList([str(err)])
            return None
        return suit.name

class SuitData(object):
    def __init__(self, _tmpfile):
        try:
            self.testdata = robot.parsing.TestData(source=os.path.abspath(_tmpfile))
            self.name = self.testdata.name
            self.path = _tmpfile
            self.version = '1.0'
            self.doc = ''
        except Exception:
            raise Exception('Given file contains invalid XML.')
        self.keywords = self.testdata.keywords
        self.tests = []
        if self.testdata.has_tests():
            self.tests = self.testdata.testcase_table.tests

