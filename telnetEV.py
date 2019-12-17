# -*- coding: utf-8 -*-
# @Time    :
# @File    : telnetEV
# @Software:
# @Author  : Kudoh
# @Email   :

import time
import telnetlib


class Reset:
    def __init__(self):
        self.rtimeout = 1

    def open(self, host, port):
        tn = telnetlib.Telnet(host, port)
        time.sleep(1)
        tn.write("\n")
        if self.readmsg(tn, "->") == 0:
            tn.close()
            tn = None
        return tn

    def resetEVG(self, host, port, cardnumber):
        print("start resetEVG", host, port, cardnumber)
        tn = self.open(host, port)
        f = True
        if tn == None:
            f = False
        else:
            try:
                if f: tn.write("EG\n")
                if f and self.readmsg(tn, "]:") == 0: f = False
                if f: tn.write("%s\n" % (cardnumber))
                if f and self.readmsg(tn, "quit") == 0: f = False
                if f: tn.write("r\n")
                if f and self.readmsg(tn, "quit") == 0: f = False
                if f: tn.write("r\n")
                if f and self.readmsg(tn, "quit") == 0: f = False
                if f: tn.write("q\n")
                if f: self.readmsg(tn, "->")
                r = tn.read_eager()
                while r != "":
                    r = tn.read_eager()
                    tn.write("\r\n")
                time.sleep(1)
            except:
                print("error")
            tn.close()
        return f

    def resetEVR(self, host, port, cardnumber):
        print("start resetEVR", host, port, cardnumber)
        tn = self.open(host, port)
        f = True
        if tn == None:
            f = False
        else:
            try:
                if f: tn.write("ER\n")
                if f and self.readmsg(tn, "]:") == 0: f = False
                if f: tn.write("%s\n" % (cardnumber))
                if f and self.readmsg(tn, "quit") == 0: f = False
                if f: tn.write("r\n")
                if f and self.readmsg(tn, "quit") == 0: f = False
                if f: tn.write("r\n")
                if f and self.readmsg(tn, "quit") == 0: f = False
                if f: tn.write("q\n")
                if f: self.readmsg(tn, "->")
                r = tn.read_eager()
                while r != "":
                    r = tn.read_eager()
                    tn.write("\r\n")
                time.sleep(1)
            except:
                print("error")
            tn.close()
        return f

    def resetVME(self, host, port):
        print("start resetVME")
        tn = self.open(host, port)
        f = True
        if tn is None:
            f = False
        else:
            try:
                tn.write("reboot\n")
                r = tn.read_eager()
                while r != "":
                    r = tn.read_eager()
                    tn.write("\r\n")
                time.sleep(1)
                tn.close()
            except:
                tn.close()
                f = False
        return f

    def readmsg(self, tn, expected):
        msg = tn.read_until(expected, self.rtimeout)
        print(msg)
        return len(msg)
