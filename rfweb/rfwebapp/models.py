from django.db import models

class Suit(models.Model):
    name = models.CharField(max_length=80)
    path = models.CharField(max_length=80)
    doc = models.TextField(verbose_name='Documentation')
    version = models.CharField(max_length=20, default='<unknown>')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Keyword(models.Model):
    suit = models.ForeignKey(Suit)
    name = models.CharField(max_length=80)
    doc = models.TextField(verbose_name='Documentation')
    args = models.CharField(max_length=200, verbose_name='Arguments',
            help_text='Use format: <em>arg1, arg2=default</em>')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Test(models.Model):
    suit = models.ForeignKey(Suit)
    name = models.CharField(max_length=80)
    doc = models.TextField(verbose_name='Documentation')
    tasks = models.ManyToManyField('Task', blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Task(models.Model):
    suit = models.ForeignKey(Suit)
    name = models.CharField(max_length=80)
    comment = models.TextField(verbose_name='Comment')
    tests = models.ManyToManyField(Test, through=Test.tasks.through, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    modified = models.DateField(auto_now_add=True, auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

'''
class Tag(models.Model):
    test = models.ForeignKey(Test)
    suit = models.ForeignKey(Suit)
    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name
'''

