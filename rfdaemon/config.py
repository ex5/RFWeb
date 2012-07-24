import os

class Dj():
    def __init__(self):
        self.app_name = 'rfweb'
        self.app_dir = '/opt/ta/'
        self.settings = '%s.settings' % self.app_name

django = Dj()

class Path():
    def __init__(self):
        self.source_dir = os.path.abspath(os.path.dirname(__file__))
        self.pid_file = os.path.join(self.source_dir, 'robotd_%s_%s.pid')
        self.stdout = "/var/log/messages"
        self.stderr = self.stdout
        self.testlist = os.path.join(self.source_dir, 'example.xml')
        self.listener_path = self.source_dir
        self.listener = 'listener.Listener'
        self.output = os.path.join(django.app_dir, '%s/media/results' % django.app_name)
        self.suits_path = os.path.join(django.app_dir, '%s/media/suits' % django.app_name)
        self.pybot = '/opt/python2.7/bin/pybot'

    def __str__(self):
        return '\n'.join(map(lambda x: "%s: %s" % (x, getattr(self, x)), self.__dict__))

path = Path()

