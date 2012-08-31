from django.shortcuts import render_to_response
from django import forms
from django.db.models import Q

from rfwebapp.models import Keyword

def search(request):
    search_performed = False
    kws = []
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            term = form.cleaned_data['search_term']
            filter = Q(name__icontains=term)
            if form.cleaned_data['include_doc']:
                filter = filter | Q(doc__icontains=term)
            kws = Keyword.objects.filter(filter) 
            search_performed = True
    else:
        form = SearchForm()
    return render_to_response('search.html', {'form': form, 'kws': kws,
                                              'search_performed': search_performed})

class SearchForm(forms.Form):
    search_term = forms.CharField() 
    include_doc = forms.BooleanField(required=False)

