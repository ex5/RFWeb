import os

class Path():
    def __init__(self):
        self.source_dir = os.path.abspath(os.path.dirname(__file__))
        self.test_suit = '.'
        self.pid_file = '/tmp/robotd.pid'
        self.logs = '/tmp'
        self.stderr = '/tmp/robotd.log'
        self.stdout = '/tmp/robotd.log'
        self.testlist = os.path.join(self.source_dir, 'example.xml')
        self.listener_path = self.source_dir
        self.listener = 'listener.Listener'

    def __str__(self):
        return '\n'.join(map(lambda x: "%s: %s" % (x, getattr(self, x)), self.__dict__))

path = Path()

