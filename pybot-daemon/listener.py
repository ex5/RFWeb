"""
Listener implementation example. 
Instead of doing nothing listener can, for example, report test status somewhere (e.g., to remote DB).
It also can write custom log file.
"""

import os
import sys
import tempfile

class Listener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, filename='listener.log'):
        outpath = os.path.join(tempfile.gettempdir(), filename)
        self.outfile = open(outpath, 'w')

    def start_suite(self, *args):
        _str = '[%s]: %s \n' % (__file__, (str(args)))
        self.outfile.write(_str)

    def start_test(self, *args):
        _str = '[%s]: %s \n' % (__file__, (str(args)))
        self.outfile.write(_str)

    def end_test(self, *args):
        _str = '[%s]: %s \n' % (__file__, (str(args)))
        self.outfile.write(_str)

    def end_suite(self, *args):
        _str = '[%s]: %s \n' % (__file__, (str(args)))
        self.outfile.write(_str)

    def start_keyword(self, *args):
        _str = '[%s]: %s \n' % (__file__, (str(args)))
        self.outfile.write(_str)

    def end_keyword(self, *args):
        _str = '[%s]: %s \n' % (__file__, (str(args)))
        self.outfile.write(_str)

    def close(self):
        _str = '[%s]: closing\n' % __file__
        self.outfile.write(_str)
        self.outfile.close()

