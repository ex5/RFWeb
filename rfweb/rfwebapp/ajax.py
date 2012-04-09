from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from rfweb.rfwebapp.models import Suite, Test, Task
from django.utils import simplejson

@dajaxice_register
def get_test_list(request, suite_id):
    dajax = Dajax()
    tests = Test.objects.filter(suite_id__exact=(int(suite_id))).distinct()
    out = ""
    for test in tests:
        out += "<option value='%d'>%s" % (test.pk, test)
    dajax.assign('#tests', 'size', len(tests))
    dajax.assign('#tests', 'visibility', 'true')
    dajax.assign('#tests', 'innerHTML', out)
    return dajax.json()

@dajaxice_register
def preview_task(request, name, suite_id, test_ids, comment):
    if not suite_id:
        return
    dajax = Dajax()
    test_ids = filter(lambda x: bool(x) == True, test_ids.split(','))
    task = Task(suite=Suite.objects.get(id__exact=(int(suite_id))), name=name, comment=comment)
    task.save()
    task.tests.add(*Test.objects.filter(pk__in=test_ids))
    task.save()
    _xml = ""
    for test in test_ids:
        _xml += "<test name='%s' />\n" % test
    dajax.assign('#preview', 'rows', len(_xml.split('/')) + 1)
    dajax.assign('#preview', 'cols', max(map(len, _xml.split('/'))) + 1)
    dajax.assign('#preview', 'innerText', _xml)
    return dajax.json()

@dajaxice_register
def start_tasks(request, selected):
    dajax = Dajax()
    tasks = Task.objects.filter(pk__in=map(int, selected))
    out = "<root>"
    for task in tasks:
        out += '<robot suite="%s" output="%s">' % (task.suite.path, ".")
        for test in task.tests.select_related():
            out += "<test name='%s' />" % test.name
        out += "</robot>"
    out += "root"
    dajax.assign('#start', 'innerHTML', out)
    return dajax.json()

@dajaxice_register
def stop_tasks(request, selected):
    dajax = Dajax()
    return dajax.json()

@dajaxice_register
def delete_tasks(request, selected):
    dajax = Dajax()
    return dajax.json()

@dajaxice_register
def show_task_tests(request, task_id, test_ids):
    dajax = Dajax()
    tests = Test.objects.filter(pk__in=map(int, test_ids.replace('L', '').replace('[', '').replace(']', '').split(','))) # quite a temporary solution
    out = "<ul>"
    for test in tests:
        out += "<li>%s</li>" % test.name
    out += "</ul>"
    dajax.assign('#tests_%s' % task_id, 'innerHTML', out)
    return dajax.json()

