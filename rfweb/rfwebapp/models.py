from django.db import models
from rfweb.settings import RESULTS_URL, RESULTS_PATH
import os

LOG_TYPE = (
    (0, 'Start suite'),
    (1, 'Start test'),
    (2, 'Start keyword'), 
    (3, 'End suite'),
    (4, 'End test'),
    (5, 'End keyword'),
    (6, 'Log message'),
    (7, 'Message'),
    (8, 'Close'),
)

_LOG_TYPE = {y: x for x, y in LOG_TYPE}
_LOG_TYPE.update({x: y for x, y in LOG_TYPE})

class BigIntegerField(models.IntegerField):
    empty_strings_allowed=False
    def get_internal_type(self):
        return "BigIntegerField"
    def db_type(self):
        return 'bigint' # Note this won't work with Oracle.

class Suite(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    path = models.CharField(max_length=80)
    doc = models.TextField(verbose_name='Documentation')
    version = models.CharField(max_length=20, default='<unknown>')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Variable(models.Model):
    id = models.AutoField(primary_key=True)
    suite = models.ForeignKey(Suite)
    name = models.CharField(max_length=80)
    value = models.TextField(verbose_name='Value')
    comment = models.CharField(max_length=250, verbose_name='Comment', null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Keyword(models.Model):
    id = models.AutoField(primary_key=True)
    suite = models.ForeignKey(Suite)
    name = models.CharField(max_length=80)
    doc = models.TextField(verbose_name='Documentation')
    args = models.CharField(max_length=200, verbose_name='Arguments',
            help_text='Use format: <em>arg1, arg2=default</em>')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Test(models.Model):
    id = models.AutoField(primary_key=True)
    suite = models.ForeignKey(Suite)
    name = models.CharField(max_length=80)
    doc = models.TextField(verbose_name='Documentation')
    tasks = models.ManyToManyField('Task', blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    suite = models.ForeignKey(Suite)
    tests = models.ManyToManyField(Test, through=Test.tasks.through, blank=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified = models.DateTimeField(auto_now_add=True, auto_now=True)
    comment = models.TextField(verbose_name='Comment')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Run(models.Model, object):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task)
    start = models.DateTimeField(auto_now_add=False, auto_now=False)
    finish = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    hwaddr = models.BigIntegerField(null=True) # NULL --- need to be started, Not NULL --- hwaddr
    ip = models.CharField(max_length=15, null=True)
    uid = models.CharField(max_length=50, null=True)
    status = models.NullBooleanField(null=True)
    viewed = models.NullBooleanField(default=False)
    rerun = models.NullBooleanField(default=False)

    def hwaddr_hex(self):
        return hex(self.hwaddr).replace('L','').replace('0x','')

    def _status_str(self):
        return str(self.status)
    sstatus = property(_status_str)

    def _get_results_name(self):
        return "%s_%s_%s" % (self.task.name, self.uid and self.uid or self.ip, self.id)
    results_name = property(_get_results_name)

    def _get_url_to_results(self):
        return "%s%s" % (RESULTS_URL, self.results_name)
    url_to_results = property(_get_url_to_results)

    def _get_path_to_results(self):
        return os.path.join(RESULTS_PATH, self.results_name)
    path_to_results = property(_get_path_to_results)

    def _path_exists(self):
        return os.path.exists(self.path_to_results)
    results_exist = property(_path_exists)

    def _report_exists(self):
        _path = os.path.join(os.path.join(RESULTS_PATH, self.results_name), 'report.html')
        return os.path.exists(_path)
    report_exists = property(_report_exists)

    def get_fields_names(self):
        # make a list of fields.
        return [field.verbose_name for field in Run._meta.fields]

    def get_fields(self):
        # make a list of fields/values.
        return [(field.verbose_name, field.value_to_string(self)) for field in Run._meta.fields]

    def get_fields_dict(self):
        # make a dict of fields/values.
        return {field.verbose_name: field.value_to_string(self) for field in Run._meta.fields}

    def get_values(self):
        # make a list of fields/values.
        return [field.value_to_string(self) for field in Run._meta.fields]

    def __str__(self):
        return "%s-%s: %s, %s" % (self.start, self.finish and self.finish or '', self.ip, self.status)

    def __unicode__(self):
        return self.__str__()

class Log(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.IntegerField(max_length=1, choices=LOG_TYPE)
    run = models.ForeignKey(Run)
    hwaddr = models.BigIntegerField(null=True)
    suite = models.CharField(max_length=100, null=True)
    keyword = models.CharField(max_length=100, null=True)
    test = models.CharField(max_length=100, null=True)
    time = models.DateTimeField(auto_now_add=True, auto_now=True)
    status = models.NullBooleanField(null=True)
    comment = models.CharField(max_length=250, null=True)

    def __str__(self):
        _res = ["%s:" % self.time, _LOG_TYPE[self.type]]
        try:
            for field in ('hwaddr', 'run', 'suite', 'keyword', 'test', 'status', 'comment'):
                if field == 'hwaddr':
                    _res.append(hex(getattr(self, field))[2:14])
                elif field == 'status':
                    if self.type in (_LOG_TYPE['End test'], _LOG_TYPE['End suite'], _LOG_TYPE['End keyword']):
                        _res.append(getattr(self, field) and 'PASS' or 'FAIL')
                    elif self.type in (_LOG_TYPE['Start test'], ):
                        _res.append(getattr(self, field) and 'Critical' or 'Non critical')
                else:
                    _res.append(getattr(self, field))
        except Exception, e:
            return 'No entries'
            #raise Exception('%s: %s' % (field, e))
        return ' '.join(map(unicode, filter(lambda x: x != None, _res)))

    def __unicode__(self):
        return self.__str__()

