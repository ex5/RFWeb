class Path():
    def __init__(self):
        self.test_suit = '.'
        self.pid_file = '/tmp/robotd.pid'
        self.log_file = '/tmp/robotd.log'
        self.stderr = '/tmp/robotd.log'
        self.stdout = '/tmp/robotd.log'
        self.testlist = '/home/public/clone/pybot-daemon/example.xml'
        self.start_flag = '/tmp/.start_test'

path = Path()

