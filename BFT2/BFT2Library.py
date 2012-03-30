import re
from subprocess import Popen, PIPE
import sys

HwAddr = lambda x: re.search(r".* ([0-9a-e:]*) .*", x)
substr = lambda subs, x: re.findall("^.*%s.*$" % subs, x, re.MULTILINE)

class BFT2Library:
    ROBOT_SYSLOG_FILE = 'robot.log'
    SUIT_STATUS = "test suite status set be script"
    #ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    def __init__(self):
        self._hwaddrs_file_path = 'hwaddrs.log'
        self._hwaddrs = set()
        try:
            _file = open(self._hwaddrs_file_path, 'r')
            if _file:
                self._hwaddrs = set(_file.read().split('\n'))
                _file.close()
        except Exception:
            pass
        self._error = ''
        self._status = ''
        self._pci = \
'''
8086:0100
8086:0101
8086:1c3a
8086:1c2d
8086:1c20
8086:1c10
8086:244e
8086:1c18
8086:1c26
8086:1c5c
8086:1c00
8086:1c22
8086:1c08
1002:68e1
1002:aa68
1283:8893
10ec:8168'''.split('\n')

    def set_another_hwaddr(self, hwaddr):
        if hwaddr in self._hwaddrs:
            return
        self._hwaddrs.add(hwaddr)
        _file = open(self._hwaddrs_file_path, 'a+')
        if not _file:
            return
        _file.write(hwaddr + '\n')
        _file.close()

    def get_another_hwaddr(self):
        return self._hwaddrs

    hwaddrs = property(get_another_hwaddr, set_another_hwaddr)

    def _is_hwaddr_taken(self, hwaddr):
        if hwaddr in self.hwaddrs:
            return True
        self.set_another_hwaddr(hwaddr)
        return False

    def status_should_be(self, expected_status):
        if expected_status != self._status:
            raise AssertionError("Expected status to be '%s' but was '%s'"
                                  % (expected_status, self._status))

    def status_should_not_be(self, expected_status):
        if self._status == expected_status:
            raise AssertionError("Status should not be '%s'" % self._status)
    
    def any_errors(self):
        if self._error:
            raise AssertionError("ERROR: %s" % self._error)

    def _run_command(self, command):
        self._status = ''
        self._error = ''
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        self._status = process.stdout.read().strip()
        self._error = process.stderr.read().strip()

    def HwAddr(self):
        self._run_command("tail /sys/class/net/eth0/address")
        if self._is_hwaddr_taken(self._status):
            self._status = 'NOT UNIQUE'
        else:
            self._status = 'UNIQUE'

    def network_device(self, name):
        self._run_command("ls /sys/class/net")
        if not substr(name, self._status):
            return 'NOT FOUND'
        else:
            return 'EXISTS'

    def pci_device(self, devID):
        self._run_command("lspci -d %s -vvv" % devID)
        return self._status
    
    def link_up(self, name):
        self._run_command("cat /sys/class/net/%s/operstate" % name)
        return self._status

    def ping(self, ip, count=100, flood=False):
        print "ping %s -c %s %s" % (flood and "-i 0" or '', count, ip)
        self._run_command("ping %s -c %s %s" % (flood and "-i 0" or '', count, ip))
        print self._status

    def serial(self):
        return "1234567890"

