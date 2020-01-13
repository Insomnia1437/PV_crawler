# -*- coding: utf-8 -*-
# @Time    : 2020-01-10
# @File    : procBootExec
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp

import subprocess
from procBootLogger import Logger


class ProcExec(object):
    def __init__(self, logpath):
        self.stat = None
        log_obj = Logger(logpath)
        self.logger = log_obj.logger

    def exec_process(self, cmnd):
        rtn = False
        try:
            self.stat = subprocess.Popen(cmnd.split(),
                                         shell=False,
                                         stdin=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         )
            rtn = True
        except subprocess.SubprocessError:
            self.stat = None
            self.logger.error("!!!!! Process Execute FAIL, %s!!!!!" % cmnd, exc_info=True)
        return rtn

    def kill(self):
        if self.stat is not None:
            self.logger.debug("try to kill subprocess")
            self.stat.kill()

    def term(self):
        if self.stat is not None:
            self.logger.debug("try to terminate subprocess")
            self.stat.terminate()

    def get_pid(self):
        rtn = -1
        if self.stat is not None:
            rtn = self.stat.pid
        return rtn

    def get_result(self):
        rtn = None
        try:
            if self.stat is not None:
                rtn = self.stat.communicate()
        except subprocess.SubprocessError:
            self.logger.error("get_result error", exc_info=True)
        return rtn

    def write_command(self, cmd):
        rtn = None
        try:
            if self.stat is not None:
                rtn = self.stat.communicate(cmd)
        except subprocess.SubprocessError:
            self.logger.error("write_command error", exc_info=True)
        return rtn
