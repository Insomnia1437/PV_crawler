# -*- coding: utf-8 -*-
# @Time    : 2020-01-11
# @File    : procBootProcess
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp
import time

import psutil
from procBootLogger import Logger


class ProcessList(object):
    def __init__(self, pid, logpath):
        log_obj = Logger(logpath)
        self.logger = log_obj.logger
        if psutil.pid_exists(pid):
            self.ps = psutil.Process(pid)
        else:
            self.logger.error("%s pid does not exist")

    def get_name(self):
        if self.ps is not None:
            return self.ps.name()

    def get_boot_time(self):
        if self.ps is not None:
            epoch = self.ps.create_time()
            return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(epoch))

    def get_exe(self):
        if self.ps is not None:
            return self.ps.exe()

    def get_cwd(self):
        if self.ps is not None:
            return self.ps.cwd()

    def get_username(self):
        if self.ps is not None:
            return self.ps.username()

    def get_uid(self):
        if self.ps is not None:
            return self.ps.uids()[1]

    def get_gid(self):
        if self.ps is not None:
            return self.ps.gids()[1]


if __name__ == '__main__':
    ps = ProcessList(56076, 'test.log')
    print(ps.get_boot_time(), ps.get_name(), ps.get_exe(), ps.get_cwd())
    print(ps.get_username(), ps.get_gid())
