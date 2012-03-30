import re
from subprocess import Popen, PIPE
import helpers

HwAddr = lambda x: re.search(r".* ([0-9a-e:]*) .*", x)
substr = lambda subs, x: re.findall("^.*%s.*$" % subs, x, re.MULTILINE)
cores_count = lambda _tmp: max(map(int, re.findall("^core id.*: (\d*)$", _tmp, re.M))) + 1
cpus_count = lambda _tmp: max(map(int, re.findall("^physical id.*: (\d*)$", _tmp, re.M))) + 1

class BFT2Library(helpers.CmdRunner):
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

    def HwAddr(self):
        self.run("tail /sys/class/net/eth0/address")
        if self._error:
            return "ERROR: %s" % self._error
        if self._is_hwaddr_taken(self._output):
            return 'NOT UNIQUE'
        else:
            return 'UNIQUE'

    def network_device(self, name):
        self.run("ls /sys/class/net")
        if self._error:
            return "ERROR: %s" % self._error
        if not substr(name, self._output):
            return 'NOT FOUND'
        else:
            return 'EXISTS'

    def pci_device(self, devID):
        self.run("lspci -d %s -vvv" % devID)
        if self._error:
            return "ERROR: %s" % self._error
        return self._output
    
    def link_up(self, name):
        self.run("cat /sys/class/net/%s/operstate" % name)
        if self._error:
            return "ERROR: %s" % self._error
        return self._output

    def ping(self, host, count=100, flood=False, acceptable_loss=10):
        _cmd = "ping %s -c %s %s" % (flood and "-i 0" or '', count, host)
        _stdout_path = _cmd.replace(' ', '_') + ".out"
        _stdout = open(_stdout_path, 'w+')
        process = Popen(_cmd, shell=True, stdout=_stdout, stderr=PIPE)
        self._error = process.stderr.read().strip()
        if self._error:
            return "ERROR: %s" % self._error
        self.run("tail %s -n 2" % _stdout_path)
        _packet_loss = re.search('([\d]+)%', self._output).groups()[0]
        _stdout.close()
        return int(_packet_loss) <= int(acceptable_loss) and 'REPLIED' or 'FAILED'

    def UID(self):
        if self._error:
            return "ERROR: %s" % self._error
        return "1234567890"
    
    def serial_exists(self):
        self.run("dmesg | grep tty")
        if self._error:
            return "ERROR: %s" % self._error
        return ["/dev/%s" % x for x in set(re.findall("(tty[USB\d]{2,5})", self._output,  re.M))]

    def serial_test(self, device='/dev/ttyS0', _test_string="hello serial port"):
        import serial
        try:
            _p = serial.Serial(device, baudrate=115200, timeout=5, writeTimeout=5, interCharTimeout=5, xonxoff=False, rtscts=False)
            _p.flowControl(False)
        except Exception:
            return "ERROR: cannot open port %s" % device
        if False in (_p.writable(), _p.readable()):
            _p.close()
            return "ERROR: cannot write to/read from port %s" % _p.port
        _p.write(_test_string)
        _tmp = _p.readall()
        _p.close()
        return _tmp

    def hyper_threading_check(self):
        #cat /proc/cpuinfo | grep "processor"
        self.run("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return max(map(int, re.findall("^processor.*: (\d*)$", self._output, re.M))) + 1 != cpus_count(self._output) * cores_count(self._output)

    def CPU_cores(self):
        #cat /proc/cpuinfo | grep "core id"
        self.run("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return cores_count(self._output)

    def CPUs(self):
        #cat /proc/cpuinfo | grep "physical id"
        self.run("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return cpus_count(self._output)
    
    def CPU_frequency(self, expect_freq=3093.061):
        #cat /proc/cpuinfo | grep "cpu MHz"
        self.run("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        _tmp = re.findall("^cpu MHz.*: (\d*\.\d*)$", self._output, re.M)
        if any(map(lambda x: x != expect_freq, _tmp)):
            return 'Unexpected CPU MHz %s' % _tmp
        return 'PASS'
    
    def total_memory(self):
        #cat /proc/meminfo | grep "MemTotal:"
        self.run("cat /proc/meminfo")
        if self._error:
            return "ERROR: %s" % self._error
        _tmp = re.findall("^MemTotal:.* (\d*) kB$", self._output, re.M)
        if not _tmp:
            return "ERROR: cannot stat memory"
        return _tmp[0]
    

