from django.db import models

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
    name = models.CharField(max_length=80)
    path = models.CharField(max_length=80)
    doc = models.TextField(verbose_name='Documentation')
    version = models.CharField(max_length=20, default='<unknown>')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Keyword(models.Model):
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
    suite = models.ForeignKey(Suite)
    name = models.CharField(max_length=80)
    doc = models.TextField(verbose_name='Documentation')
    tasks = models.ManyToManyField('Task', blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Task(models.Model):
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

class Run(models.Model):
    task = models.ForeignKey(Task)
    start = models.DateTimeField(auto_now_add=True, auto_now=False)
    finish = models.DateTimeField(null=True)
    host_id = models.BigIntegerField(null=True) # NULL --- need to be started, Not NULL --- host_id
    status = models.NullBooleanField(null=True)

    def __str__(self):
        return "%s,%s %s: %s %s" % (self.start, self.finish and self.finish or '', self.host_id and self.host_id or 'Any host', self.task, self.status != None and self.status or '')

    def __unicode__(self):
        return self.__str__()

class Log(models.Model):
    type = models.IntegerField(max_length=1, choices=LOG_TYPE)
    task = models.ForeignKey(Task)
    host_id = models.BigIntegerField(null=True)
    suite = models.CharField(max_length=100, null=True)
    keyword = models.CharField(max_length=100, null=True)
    test = models.CharField(max_length=100, null=True)
    time = models.DateTimeField(auto_now_add=True, auto_now=True)
    status = models.NullBooleanField(null=True)
    comment = models.CharField(max_length=250, null=True)

    def __str__(self):
        _res = ["%s:" % self.time, _LOG_TYPE[self.type]]
        for field in ('host_id', 'task', 'suite', 'keyword', 'test', 'status', 'comment'):
            if field == 'host_id':
                _res.append(hex(getattr(self, field))[2:14])
            elif field == 'status':
                if self.type in (_LOG_TYPE['End test'], _LOG_TYPE['End suite'], _LOG_TYPE['End keyword']):
                    _res.append(getattr(self, field) and 'PASS' or 'FAIL')
                elif self.type in (_LOG_TYPE['Start test'], ):
                    _res.append(getattr(self, field) and 'Critical' or 'Non critical')
            else:
                _res.append(getattr(self, field))
        return ' '.join(map(unicode, filter(lambda x: x != None, _res)))

    def __unicode__(self):
        return self.__str__()

