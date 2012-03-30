#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.abspath(os.path.curdir) + "/pythondialog-2.7")
import helpers
import subprocess
import time
import dialog

colorize= { 
# black, red, green, yellow, blue, magenta, cyan white \Z0-\Z9
        'OK': "\Z2\ZbOK\Zn",
        'FAIL': "\Z1\ZbFAIL\Zn",
        'Error': "\Z1\ZbError\Zn",
        'ERROR': "\Z1\ZBERROR\Zn",
        'PASS': "\Z2\ZbPASS\Zn",
        }

class TestScheduler():
    '''
    Simple test scheduler with UI based on dialog/xdialog
    '''
    def __init__(self, logfile="scheduler.log", suit_path="quickstart"):
        self.logfile = open(logfile, 'w')
        self.suit_path = suit_path
        self.dlg = dialog.Dialog(dialog="dialog")
        self.flush_state()
        self.dlg.setBackgroundTitle(self.backtitle)
        self.display()

    def __str__(self):
        return str([(attr, getattr(self, attr)) for attr in self.__dict__])

    def flush_state(self):
        self.suit = None
        self.info = ""
        self.state = "restart"
        self.title = str(self.__class__).split('.')[1]
        self.backtitle = self.title

    def log(self, *args):
        self.logfile.write(str(time.ctime()) + ': ' + str(args) + '\n')

    def quit(self):
        self.info_update("----- Bye! -----", clear=True)
        self.log("quit", self)
        self.logfile.close()
        exit(0)

    def info_update(self, info, widget="infobox", clear=False):
        if clear:
            self.info = ""
        for token in colorize:
            info = info.replace(token, colorize[token])
        self.info += "\n" + info
        self.draw(self.state, widget)

    def draw(self, mode="", widget="infobox"):
        size = "%s %s" % (len(self.info.split('\n')) + 5, max(map(len, self.info.split('\n'))))
        subprocess.call("DIALOGRC=.dialogrc.%s dialog --keep-window --title \"%s\" --backtitle \"%s\" --colors --%s \"%s\" %s" % (mode, self.title, self.backtitle, widget, self.info, size), shell=True, stderr=self.logfile)

    def draw_menu(self):
        height = len(self.info[1]) + 7
        width = max(max(max(map(lambda x: len(x[1]), self.info[1])), len(self.info[0])), len(self.title)) + 5
        return self.dlg.menu(text=self.info[0], height=height, width=width, menu_height=7, choices=self.info[1])

    def display(self):
        while self.state != "exit":
            if self.state == "restart":
                self.do()
        self.quit()

    def do(self):
        htmls = [name for name in os.listdir(self.suit_path) if '.html' in name]
        self.info = ["Please, choose one of the test suits:", map(lambda x: (str(x[0]),str(x[1])), zip(range(1, len(htmls) + 1), htmls) )]
        try:
            chosen = int(self.draw_menu()[1]) - 1
        except Exception:
            self.state = "exit"
            return
        self.log("chosen item", chosen, self.log(htmls[chosen]))
        self.info_update("Welcome to test scheduler", clear=True)
        # reading test suite file
        self.suit = open("%s/%s" % ( self.suit_path, htmls[chosen]))
        if not self.suit:
            self.state = "alarm"
            self.title = colorize["Error"]
            self.info_update("[FAIL] Could not found any test suit")
            self.flush_state()
            return
        self.info_update("[OK] Found test suit %s" % self.suit.name)
        # checking pybot executable
        try:
            self.pybot = helpers._path_to_executable("pybot")
        except Exception:
            self.state = "alarm"
            self.title = colorize["Error"]
            self.info_update("[FAIL] Could not found pybot executable")
            self.flush_state()
            return
        self.info_update("[OK] Found pybot executable")
        self.log(self.info_update(info="\n\ZbRun available tests\Zn", widget="msgbox"))
        testrun = subprocess.Popen([self.pybot, self.suit.name], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.info_update("", clear=True)
        is_valid = False
        while testrun.poll() is None: #Check if child process has terminated
            line = testrun.stdout.readline()
            self.log(line)
            if bool(line):
                is_valid = True
            if not is_valid:
                self.title = colorize["Error"]
                self.info_update("[FAIL] %s is not a valid test suit file" % self.suit.name, widget="msgbox")
                self.flush_state()
                return
            if '|' in line or ',' in line:
                if 'FAIL' in line:
                    self.state = "alarm"
                self.info_update(line)
                #time.sleep(.8)
        self.info_update("", widget="msgbox")
        self.flush_state()

def main():
    if len(sys.argv) > 1:
        print sys.argv
        scheduler = TestScheduler(suit_path=sys.argv[1])

if __name__ == "__main__":
    main()
