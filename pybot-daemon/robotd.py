#!/usr/bin/env python

import sys, time
from daemon import Daemon
import robot
from config import path

class RobotDaemon(Daemon):
    def run(self):
        self.test_suit_path = path.test_suit
        self.logger.debug("run, path to the test suit: %s" % self.test_suit_path)
        while True:
            time.sleep(1)

if __name__ == "__main__":
    daemon = RobotDaemon(pidfile=path.pid_file, logfile=path.log_file, stdout=path.stdout, stderr=path.stderr)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
