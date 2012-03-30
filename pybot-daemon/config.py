class Path():
    def __init__(self):
        self.test_suit = '.'
        self.pid_file = '/tmp/robotd.pid'
        self.logs = '/tmp'
        self.stderr = None
        self.stdout = None
        self.testlist = '/home/public/clone/pybot-daemon/example.xml'
        self.start_flag = '/tmp/.start_test'

path = Path()

