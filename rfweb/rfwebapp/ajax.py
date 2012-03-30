from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from rfweb.rfwebapp.models import Suit, Test, Task
from django.utils import simplejson

@dajaxice_register
def get_test_list(request, suit_id):
    dajax = Dajax()
    tests = Test.objects.filter(suit_id__exact=(int(suit_id))).distinct()
    out = ""
    for test in tests:
        out += "<option value='%s'>%s" % (test, test)
    dajax.assign('#tests', 'size', len(tests))
    dajax.assign('#tests', 'visibility', 'true')
    dajax.assign('#tests', 'innerHTML', out)
    return dajax.json()

@dajaxice_register
def preview_task(request, name, suit_id, tests, comment):
    if not suit_id:
        return
    dajax = Dajax()
    tests = filter(lambda x: bool(x) == True, tests.split(','))
    task = Task(suit=Suit.objects.get(id__exact=(int(suit_id))), name=name, comment=comment)
    task.save()
    task.tests.add(*Test.objects.filter(name__in=tests))
    task.save()
    _xml = ""
    for test in tests:
        _xml += "<test name='%s' />\n" % test
    dajax.assign('#preview', 'rows', len(tests))
    dajax.assign('#preview', 'cols', max(map(len, tests)))
    dajax.assign('#preview', 'innerText', _xml)
    return dajax.json()

