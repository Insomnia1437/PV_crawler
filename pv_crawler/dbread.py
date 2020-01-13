# -*- coding: utf-8 -*-
# @Time    : 2019-12-18
# @File    : dbread
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp

import subprocess
import shlex
PATH = "/cont/epics314/app/KEKB/EVT/MTS20190409/iocBoot/iocmyap/"
MSI_PATH = ""
# command_line = "/home/sdcswd/msi/msi -S substitute.substitutions"
command_line = "/usr/users/sdcswd/epics/base/base-3.15.6/bin/linux-x86_64/msi -S test.substitutions"
args = shlex.split(command_line)


class DBRead:
    """
    search the st.cmd or similar file for two functions:
    dbLoadRecords()
    dbLoadTemplate()
    expand macro to get real PV Name, record type etc.
    Using EPICS extensions: msi to expand.
    Command is like:
    ./msi -M "SYS=LIiEV,D=evg0,EVG=SKBEVG0" -o result.log ../workspace/SKBEVG-config.db
    ./msi -V -o outfile -I dir -M subs -S subfile template
    """

    def __init__(self, file=None, ):
        """
        Constructor.
        """
        self.file = file

    def read_records(self):
        # TODO
        pass

    def read_templates(self):
        # TODO
        pass


if __name__ == '__main__':
    # db_read = DBRead(PATH)
    # db_read.read_records()
    try:
        obj = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               cwd="/usr/users/sdcswd/python/pvcrawler/")
        stdout, stderr = obj.communicate()
        print(type(stdout), len(stdout))
    except subprocess.CalledProcessError as e:
        print(e.output)
        print(e.returncode)