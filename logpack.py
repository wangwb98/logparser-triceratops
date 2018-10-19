# -*- coding: utf-8 -*-
"""This module is a class to represent a set of logs"""

import os, re
from enum import Enum

Logtype = Enum("Logtype", ("kernel","event","system","main", "all", "unknown"))
Logatomtype = Enum("Logatomtype", ("boot","reboot"))

KERNEL_REGEX = '(\d+-\d+ \d+:\d+:\d+\.\d+)\s+<(\d+)>\s+\[\s*(\d+\.\d+)\]\s+c(\d+)\s+(\d+)\s+\(([^)]*)\)\s+(.*)'
MAIN_REGEX = '(\d+-\d+ \d+:\d+:\d+\.\d+)\s+(\d+)\s+(\d+)\s+(\w)\s+(.*)'

class LogPack ():
    """
    LogPack is a collection of running logs.
    Usually it has the log of a continuous running period (a few minutes, a few days) on one
    device.
    """
    def __init__(self):
        self.log_full = []
        self.log_atomized = []
    def __str__(self):
        printed = '<' + str(self.log_full)[1:-1] + '>'
        return pritnted

    def _is_logcat_file(self, filename):
        if filename[:4] in ("main", "even", "syst"):
            return True

# logcat log sample as below:
#    10-16 18:00:07.255   276   276 W auditd  : type=2000 audit(0.0:1): initialized
# kernel log sample as below:
#    10-17 09:35:08.477 <3> [54391.705222] c0 21280 (system_server) Value of AWUCRS register: 0x90000000
    def _log_line_translate(self, filename, log_line):
        if self._is_logcat_file(filename):
            # date_time, pid, tid, msg_type, msg
            p = re.compile(MAIN_REGEX).search(log_line)
            if (p != None):
                return p.groups()
        if filename.startswith("kernel"):
            p = re.compile(KERNEL_REGEX).search(log_line)
            if (p != None):
                return p.groups()
    
    """
    Add log folder contents into LogPack object.
    update .log_full and .log_atomized
    """
    def add(self, folder_name):
        rootdir = folder_name
        for root, dirs, files in os.walk(rootdir):
            for filename in files:
                # skip the files we cannot handler right now
                if self._filename_filter(filename) == False:
                    continue
                with open(os.path.join(root, filename),
                                 encoding='utf-8', errors="ignore",
                          newline="\n") as f:
                    # must add "errors" since some log file has non-UTF8
                    # content
                    # must use "\n" newline otherwise there will be more lines
                    # judged as wrong contents by regex pattern
                    l = f.readline()
                    while l != "":
                        #t, lt, pid, msg = self._log_line_translate(filename, l)
                        try:
                            if self._is_logcat_file(filename):
                                t, pid, tid, msg_type, msg = self._log_line_translate(filename, l)
                            elif filename.startswith("kernel"):
                                t, kloglvl, kt, cpu_id, pid, pid_name, msg = self._log_line_translate(filename, l)
                                tid="??"
                                msg_type = "??"

#    10-17 09:35:08.477 <3> [54391.705222] c0 21280 (system_server) Value of AWUCRS register: 0x90000000

                            self.log_full.append({"time":t,
                                    "logtype":self._filename2log_type(filename),
                                                 "pid":pid,
                                                 "tid":tid,
                                                  "msg_type":msg_type,
                                                 "msg":msg})
                        except TypeError:
                            # this line doesn't have the expected format
                            # simply ignore this line
                            print ("error line: %s" % l)
                            pass
                        l = f.readline()
        #self.log_atomized.append({"time":"111", "logatomtype":
                                 #Logatomtype.boot, "param":"xxx"})
        pass
    def getlog(self, logtype = Logtype.all, sorttype = "time"):
        return sorted(self.log_full, key=lambda log_line: log_line["time"] )

    def _filename2log_type(self, filename):
        if filename.startswith("main"):
            return Logtype.main
        elif filename.startswith("system"):
            return Logtype.system
        elif filename.startswith("event"):
            return Logtype.event
        elif filename.startswith("kernel"):
            return Logtype.kernel
        else:
            return Logtype.unknown

    def _filename_filter(self, filename):
        if self._is_logcat_file(filename):
            return True
        elif filename.startswith("kernel"):
            return True else: return False

def test():
    log = LogPack()
    log.add("/tmp/test")
    for i in log.getlog():
        print ("%s %s %s %s" %(i["time"], i["logtype"], i["pid"], i["msg"]))

if __name__ == "__main__":
    test()
