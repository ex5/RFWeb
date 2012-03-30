import re
from subprocess import Popen, PIPE

HwAddr = lambda x: re.search(r".* ([0-9a-e:]*) .*", x)
substr = lambda subs, x: re.findall("^.*%s.*$" % subs, x, re.MULTILINE)
cores_count = lambda _tmp: max(map(int, re.findall("^core id.*: (\d*)$", _tmp, re.M))) + 1
cpus_count = lambda _tmp: max(map(int, re.findall("^physical id.*: (\d*)$", _tmp, re.M))) + 1

class BFT2Library:
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

    def add_hwaddr(self, hwaddr):
        if hwaddr in self._hwaddrs:
            return
        self._hwaddrs.add(hwaddr)
        _file = open(self._hwaddrs_file_path, 'a+')
        if not _file:
            return
        _file.write(hwaddr + '\n')
        _file.close()

    def get_hwaddrs(self):
        return self._hwaddrs

    hwaddrs = property(get_hwaddrs, add_hwaddr)

    def _is_hwaddr_taken(self, hwaddr):
        if hwaddr in self.hwaddrs:
            return True
        self.add_hwaddr(hwaddr)
        return False

    def _run_command(self, command):
        self._status = ''
        self._error = ''
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        self._status = process.stdout.read().strip()
        self._error = process.stderr.read().strip()

    def HwAddr(self):
        self._run_command("tail /sys/class/net/eth0/address")
        if self._error:
            return "ERROR: %s" % self._error
        if self._is_hwaddr_taken(self._status):
            return 'NOT UNIQUE'
        else:
            return 'UNIQUE'

    def network_device(self, name):
        self._run_command("ls /sys/class/net")
        if self._error:
            return "ERROR: %s" % self._error
        if not substr(name, self._status):
            return 'NOT FOUND'
        else:
            return 'EXISTS'

    def pci_device(self, devID):
        self._run_command("lspci -d %s -vvv" % devID)
        if self._error:
            return "ERROR: %s" % self._error
        return self._status
    
    def link_up(self, name):
        self._run_command("cat /sys/class/net/%s/operstate" % name)
        if self._error:
            return "ERROR: %s" % self._error
        return self._status

    def ping(self, host, count=100, flood=False, acceptable_loss=10):
        _cmd = "ping %s -c %s %s" % (flood and "-i 0" or '', count, host)
        _stdout_path = _cmd.replace(' ', '_') + ".out"
        _stdout = open(_stdout_path, 'w+')
        process = Popen(_cmd, shell=True, stdout=_stdout, stderr=PIPE)
        self._error = process.stderr.read().strip()
        if self._error:
            return "ERROR: %s" % self._error
        self._run_command("tail %s -n 2" % _stdout_path)
        _packet_loss = re.search('([\d]+)%', self._status).groups()[0]
        _stdout.close()
        return int(_packet_loss) <= int(acceptable_loss) and 'REPLIED' or 'FAILED'

    def UID(self):
        if self._error:
            return "ERROR: %s" % self._error
        return "1234567890"
    
    def serial_exists(self):
        self._run_command("dmesg | grep tty")
        if self._error:
            return "ERROR: %s" % self._error
        _tmp = re.search("(?P<tty>ttyS[01])", self._status).groups()
        if not _tmp:
            return None
        return _tmp[0]

    def serial_test(self, port_num=0, _test_string="hello serial port"):
        import serial
        try:
            _p = serial.Serial(int(port_num), timeout=5, writeTimeout=5, interCharTimeout=5, xonxoff=False, rtscts=False)
            _p.flowControl(False)
        except Exception:
            return "ERROR: cannot open port %s" % port_num
        if False in (_p.writable(), _p.readable()):
            _p.close()
            return "ERROR: cannot write to/read from port %s" % _p.port
        _p.write(_test_string)
        _tmp = _p.readall()
        _p.close()
        return _tmp

    def hyper_threading_check(self):
        #cat /proc/cpuinfo | grep "processor"
        self._run_command("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return max(map(int, re.findall("^processor.*: (\d*)$", self._status, re.M))) + 1 != cpus_count(self._status) * cores_count(self._status)

    def CPU_cores(self):
        #cat /proc/cpuinfo | grep "core id"
        self._run_command("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return cores_count(self._status)

    def CPUs(self):
        #cat /proc/cpuinfo | grep "physical id"
        self._run_command("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return cpus_count(self._status)
    
    def CPU_frequency(self, expect_freq=3093.061):
        #cat /proc/cpuinfo | grep "cpu MHz"
        self._run_command("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        _tmp = re.findall("^cpu MHz.*: (\d*\.\d*)$", self._status, re.M)
        if any(map(lambda x: x != expect_freq, _tmp)):
            return 'Unexpected CPU MHz %s' % _tmp
        return 'PASS'
    
    def total_memory(self):
        #cat /proc/meminfo | grep "MemTotal:"
        self._run_command("cat /proc/meminfo")
        if self._error:
            return "ERROR: %s" % self._error
        _tmp = re.findall("^MemTotal:.* (\d*) kB$", self._status, re.M)
        if not _tmp:
            return "ERROR: cannot stat memory"
        return _tmp[0]
    

