#!/usr/bin/env python

import sys
import os
import subprocess
import time
import dialog
import robot

colorize= { 
# black, red, green, yellow, blue, magenta, cyan white \Z0-\Z9
        'OK': "\Z2\ZbOK\Zn",
        'FAIL': "\Z1\ZbFAIL\Zn",
        'Error': "\Z1\ZbError\Zn",
        'ERROR': "\Z1\ZBERROR\Zn",
        'PASS': "\Z2\ZbPASS\Zn",
        }

def _run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {'stdout': process.stdout.read().strip(),
            'stderr': process.stderr.read().strip()
           }

def _find_usb_drive():
    _out  = _run_command('ls /dev/disk/by-id| grep "usb.*part1"')
    if _out['stderr']:
        return "ERROR: %s" % _out['stderr']
    return _out['stdout']

class TestScheduler():
    '''
    Simple test scheduler with UI based on dialog/xdialog
    '''
    def __init__(self, logfile="dscheduler.log", suit_path="quickstart"):
        self.logfile = open(logfile, 'w')
        sys.stderr = self.logfile
        self.suit_path = suit_path
        self.dlg = dialog.Dialog(dialog="dialog")
        self.flush_state()
        self.chosen_tags = []
        self.dlg.setBackgroundTitle(self.backtitle)
        self.display()

    def get_info_height(self):
        return len(self.text.split('\n')) + 5
    height = property(get_info_height)

    def get_info_width(self):
        return max(map(len, self.text.split('\n'))) + 5
    width = property(get_info_width)

    def __str__(self):
        return str([(attr, getattr(self, attr)) for attr in self.__dict__])

    def _reports_to_usb_drive(self, devID):
        _mount_path = "/mnt/%s" % devID + str(time.time())
        _device = "/dev/disk/by-id/%s" % devID
        os.mkdir(_mount_path)
        _out = _run_command("mount %s %s" % (_device, _mount_path))
        self.text_update(str(_out))
        self.dlg.infobox(self.text, self.height, self.width)
        if _out['stderr']:
            return "ERROR: %s" % _out['stderr']
        _dest_path = _mount_path + "/bft2report_%s" % time.strftime("%Y_%m_%d-%H-%M-%s")
        os.mkdir(_dest_path)
        _out = _run_command("cp *.html %(path)s; cp *.xml %(path)s; cp *.log %(path)s" % {'path':_dest_path})
        _out = _run_command("umount %s" % _mount_path)
        os.rmdir(_mount_path)
        if _out['stderr']:
            return "ERROR: %s" % _out['stderr']

    def flush_state(self):
        self.suit = None
        self.text = ""
        self.state = "restart"
        self.title = str(self.__class__).split('.')[1]
        self.backtitle = self.title
        self.dlg.DIALOGRC = ''

    def log(self, *args):
        self.logfile.write(str(time.ctime()) + ': ' + str(args) + '\n')

    def quit(self):
        self.text_update(" Bye! ", clear=True)
        self.log("quit", self)
        self.logfile.close()
        exit(0)

    def text_update(self, info, widget="infobox", clear=False):
        if clear:
            self.text = ""
        for token in colorize:
            info = info.replace(token, colorize[token])
        self.text += "\n" + info
        if self.state != "restart":
            self.dlg.DIALOGRC = os.path.abspath(".dialogrc.%s" % self.state)

    def draw_menu(self):
        height = len(self.text[1]) + 7
        width = max(max(max(map(lambda x: len(x[1]), self.text[1])), len(self.text[0])), len(self.title)) + 5
        return self.dlg.menu(text=self.text[0], height=height, width=width, menu_height=7, choices=self.text[1])

    def display(self):
        while self.state != "exit":
            if self.state == "restart":
                self.do()
        self.dlg.msgbox(self.text, self.height, self.width, "Bye!")
        self.quit()

    def load_test_suit(self):
        if os.path.isdir(self.suit_path):
            return #TODO
        if not os.path.isfile(self.suit_path):
            self.text_update("[FAIL] Could not load test suit")
            return
        # reading test suite file
        try:
            self.suit = robot.parsing.TestData(source=self.suit_path)
            self.tags = set([])
            self.log(self.tags)
            for testcase in self.suit.testcase_table:
                if testcase.tags.value.__class__ == list:
                    self.tags.update(map(str,testcase.tags.value))
                else:
                    self.tags.add(str(testcase.tags.value))
        except Exception, e:
            self.log(e)
            self.title = colorize["Error"]
            self.text_update("[FAIL] %s is not a valid test suit file" % self.suit_path, widget="msgbox")
            return
        self.text_update("[OK] Test suit %s" % self.suit)

    def check_pybot(self):
        # checking pybot executable
        try:
            self.pybot = dialog._path_to_executable("pybot")
        except Exception:
            self.title = colorize["Error"]
            self.text_update("[FAIL] Could not found pybot executable")
            return
        self.text_update("[OK] pybot executable")

    def do(self):
        self.check_pybot()
        self.load_test_suit()
        if not self.suit or not self.pybot:
            self.state = "exit"
            return
        #keywords = map(lambda x: (str(x.name), "", 1), self.suit.keywords)
        #self.log(self.suit, keywords)
        if self.tags:
            self.chosen_tags = self.dlg.checklist(text="Please, choose tests:", choices=[(str(x[1]), str(x[0]), 'off') for x in zip(range(len(self.tags) + 1), self.tags)])[1]
            self.log(self.chosen_tags)
            self.text_update("[OK] Tags to run: %s" % self.chosen_tags)
        exit = self.dlg.yesno(self.text + "\nProceed?\n", len(self.text.split('\n')) + 5, max(map(len, self.text.split('\n'))) + 5, "Run", "Exit")
        if exit:
            self.state = "exit"
            return
        self.log(' '.join(map(str, self.chosen_tags)))
        _cmd = self.chosen_tags and [self.pybot, "--include", ' '.join(map(str, self.chosen_tags)), self.suit_path] or [self.pybot, self.suit_path]
        testrun = subprocess.Popen(_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.text_update("", clear=True)
        while testrun.poll() is None:
            line = testrun.stdout.readline()
            if '|' in line or ',' in line:
                if 'FAIL' in line:
                    self.state = "alarm"
                self.text_update(line)
                self.dlg.infobox(self.text, self.height, self.width)
        exit = self.dlg.yesno(self.text, self.height + 20, self.width + 20, "Run again", "Write to USB and exit")
        if exit:
            self.state = "exit"
            _usb = _find_usb_drive()
            self.log(_usb)
            _attemts = 3
            while not _usb and _attemts:
                self.log("Waiting")
                time.sleep(5)
                _attemts -= 1
                self.dlg.msgbox("Please, insert USB-drive\nPress OK when finished")
                _usb = _find_usb_drive()
            self.log(_usb)
            if not _usb:
                self.dlg.msgbox("Cannot write reports")
            else:
                self.dlg.infobox("Writing reports to USB-drive..")
                self._reports_to_usb_drive(_usb)
        else:
            self.flush_state()

def main():
    if len(sys.argv) > 1:
        print sys.argv
        scheduler = TestScheduler(suit_path=sys.argv[1])

if __name__ == "__main__":
    main()
