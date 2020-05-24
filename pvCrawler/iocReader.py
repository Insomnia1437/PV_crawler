# -*- coding: utf-8 -*-
# @Time    : 2020-05-14
# @File    : iocReader
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@gmail.com

# process the `procsrvtbl.tbl` file to get the iocs, `!` means comment
# ! PPORT : procServ port
# ! HOST  : hostname
# ! STCMD : st.cmd file name
# ! separator = ' '
# ! keyword   = "NAME HOST PPORT STCMD"
# ! format    = "%s %s %d %s"
import json
import os


class iocReader:
    def __init__(self, path):
        self.path = path
        self.ioc_list = []

    def read_ioc(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('!'):
                    continue
                if len(line) > 0:
                    try:
                        name, host, port, path = line.split()
                    except ValueError as e:
                        print(e, "in line: ", line)
                        continue
                    temp = {
                        'IOCNAME': name,
                        'IOCHOST': host,
                        'IOCPORT': port,
                        'IOCPATH': path
                    }
                    self.ioc_list.append(temp)
        return self.ioc_list

