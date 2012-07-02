from lxml.html import parse
import os
import tempfile

from django.shortcuts import render_to_response
from django import forms

from rfweb.rfwebapp.forms import UploadFileForm
from settings import SUITS_PATH 

def upload(request):
    suitname = None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            destination = os.path.join(SUITS_PATH, request.FILES['file'].name)
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

