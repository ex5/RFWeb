from django.db import models

LOG_TYPE = (
    (0, 'Start'),
    (1, 'Finish'),
    (2, 'Status'),
    (3, 'Unknown'),
)

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
    suite = models.ForeignKey(Suite)
    name = models.CharField(max_length=80)
    comment = models.TextField(verbose_name='Comment')
    tests = models.ManyToManyField(Test, through=Test.tasks.through, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    modified = models.DateField(auto_now_add=True, auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Run(models.Model):
    task = models.ForeignKey(Task)
    start = models.DateField(auto_now_add=True, auto_now=False)
    finish = models.DateField(auto_now_add=False, auto_now=False)
    running = models.BooleanField() # NULL --- need to be started, True --- already running, False --- do nothing
    status = models.BooleanField()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Log(models.Model):
    type = models.IntegerField(max_length=1, choices=LOG_TYPE)
    host_id = models.IntegerField()
    task = models.ForeignKey(Task)
    keyword = models.ForeignKey(Keyword)
    test = models.ForeignKey(Test)
    time = models.DateField(auto_now_add=True, auto_now=False)
    status = models.BooleanField()
    comment = models.CharField(max_length=250)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

