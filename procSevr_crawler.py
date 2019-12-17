# -*- coding: utf-8 -*-
# @Time    : 2019-12-16
# @File    : procSevr_crawler
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp

import telnetlib
import time

# HOST = "172.19.74.2"
HOST = "localhost"
# user = input("Enter your remote account: ")
PORT = "30001"

tn = telnetlib.Telnet(HOST, port=PORT)

# tn.write(b"pwd\n")
time.sleep(1)
tn.write(b"dbl\n")
time.sleep(5)

r = tn.read_until(b'epics>', 10).decode('ascii')
print(r)

tn.close()

