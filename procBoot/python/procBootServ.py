# -*- coding: utf-8 -*-
# @Time    : 2020-01-12
# @File    : procBootServ
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp
import json
import os
import signal
import socket
import telnetlib
import time

from procBootCfgFile import CfgFile
from procBootExec import ProcExec
from procBootLock import ProcBootLockFiles
from procBootLogger import Logger


# from procBootProcess import ProcessList


class ProcBoot(object):
    def __init__(self, configfile):
        self.cfg = CfgFile(configfile)
        if self.cfg.is_ok_cfg():
            # procboot section
            self.pb_logfile = self.cfg.get_procboot_logfile()

            # procserv section
            self.ps_procserv = self.cfg.get_procserv_procserv()
            self.ps_lockpath = self.cfg.get_procserv_lockpath()

            # default section
            self.default_sec = self.cfg.get_default_section()

            log_obj = Logger(self.pb_logfile)
            self.logger = log_obj.logger

            self.pe = ProcExec(self.pb_logfile)
            self.pblfs = ProcBootLockFiles(self.ps_lockpath, self.pb_logfile)

    def __get_boot_cmd(self, sections):
        return '%s -c %s -L %s %s %s' % (self.ps_procserv, sections['path'],
                                         os.path.join(sections['logpath'], sections['log']), sections['port'],
                                         sections['cmnd'])

    @staticmethod
    def __get_abs_cmd(sec):
        return os.path.join(sec['path'], sec['cmnd'])

    def __get_sections(self, section="", user=""):
        all_sections = self.cfg.get_prog_sections(section=section, user=user)
        if len(all_sections) == 0:
            print("No section specified...check sections:%s and user:%s" % (section, user))
            self.logger.warn("No section specified...check sections:%s and user:%s" % (section, user))
            return 0
        return all_sections

    def procboot_start(self, section="", user=""):
        all_sections = self.__get_sections(section, user)
        for sec_name in all_sections:
            result = ""
            sections = self.cfg.get_one_prog_section(sec_name)
            port_num = int(sections['port'])
            abs_cmd = self.__get_abs_cmd(sections)
            boot_cmd = self.__get_boot_cmd(sections)

            # check whether port exist in the lock
            exist, cmnd = self.pblfs.port_exist_in_lock(port_num)
            if exist:
                print("section: %s, port: '%d' Already used!!!"
                      % (sec_name, port_num))
                self.logger.info("section: %s, cmd: '%s' port: '%d' has already used, please check the logger file"
                                 % (sec_name, cmnd, port_num))
                continue

            if self.pe.exec_process(boot_cmd):
                result = self.pe.get_result()
                if len(result) == 0:
                    self.logger.error("subprocess communicate method error", exc_info=True)
            else:
                self.logger.error("create subprocess error", exc_info=True)
            """
            Correct return value:
            (b'/Users/sdcswd/epics/R3.14.12.8/extensions/bin/darwin-x86/procServ:
             spawning daemon process: 45203\n')
             
            Return value when error happens:
            (b'Caught an exception creating the initial control telnet port: 
            Bad file descriptor\n
            /Users/sdcswd/epics/R3.14.12.8/extensions/bin/darwin-x86/procServ: 
            Exiting with error code: 48\n')
            """
            result = str(result[1], encoding="utf-8")
            if len(result.split(':')) > 3:
                print(result)
                self.logger.error("create procServ error: %s" % result)
            else:
                temp = result.split(':')
                prompt = temp[1].strip()
                pid = int(temp[2].strip())
                if prompt == "spawning daemon process":
                    self.pblfs.create_lockfile(pid, port_num, boot_cmd, user=user,
                                               path=sections['path'], logpath=sections['logpath'],
                                               group=sections['group'],
                                               desc=sections['desc'], section=sec_name)
                print("run %s at port %d, pid is %d" % (sec_name, port_num, pid))

    def procboot_stop(self, section="", user=""):
        all_sections = self.__get_sections(section, user)
        for sec_name in all_sections:
            sections = self.cfg.get_one_prog_section(sec_name)
            port_num = int(sections['port'])
            abs_cmd = self.__get_abs_cmd(sections)
            boot_cmd = self.__get_boot_cmd(sections)

            # check lock
            exist, cmnd = self.pblfs.port_exist_in_lock(port_num)
            if not exist:
                print("section: %s, port: '%d' is not used"
                      % (sec_name, port_num))
                self.logger.info("section: %s, port: '%d' is not used, please check the logger file"
                                 % (sec_name, port_num))
                continue
            if cmnd != boot_cmd:
                print("FATAL Error: cmnd in lock file is '%s', but cmnd in config file is '%s'"
                      % (cmnd, boot_cmd))
                self.logger.error("cmnd in lock file is '%s', but cmnd in config file is '%s'"
                                  % (cmnd, boot_cmd))
                continue
            pid = self.pblfs.get_PID_from_port(port_num)
            if pid:
                try:
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                    self.pblfs.remove_lockfile(pid)
                except OSError:
                    self.logger.error("Try to kill pid: %d" % pid, exc_infor=True)
            print("kill %s at port %d, pid is %d" % (sec_name, port_num, pid))

    def procboot_restart(self, section="", user=""):
        startcmnd = self.cfg.get_default_section()['startcmnd']
        endline = self.cfg.get_default_section()['endline']
        restartwait = self.cfg.get_default_section()['restartwait']
        all_sections = self.__get_sections(section, user)
        for sec_name in all_sections:
            sections = self.cfg.get_one_prog_section(sec_name)
            port_num = int(sections['port'])
            boot_cmd = self.__get_boot_cmd(sections)

            # check lock
            exist, cmnd = self.pblfs.port_exist_in_lock(port_num)
            if not exist:
                print("section: %s, port: '%d' is not used"
                      % (sec_name, port_num))
                self.logger.info("section: %s, port: '%d' is not used, please check the logger file"
                                 % (sec_name, port_num))
                continue
            if cmnd != boot_cmd:
                print("Error: cmnd in lock file is '%s', but cmnd in config file is '%s'"
                      % (cmnd, boot_cmd))
                self.logger.error("Error: cmnd in lock file is '%s', but cmnd in config file is '%s'"
                                  % (cmnd, boot_cmd))
                continue
            tn = None
            try:
                tn = telnetlib.Telnet('localhost', port_num, 5)
                """
                '\x03': [CTRL+C] (^C) restart IOC
                '\x14': [CTRL+T] (^T) Toggled auto restart mode to [OFF, ONESHOT, ON]
                '\x18': [CTRL+X] (^X) restart IOC
                'dbl\n': show all PV
                """
                tn.write('\x03'.encode("ascii"))

                if int(restartwait) > 0:
                    time.sleep(float(restartwait))
                if startcmnd == '\n':
                    tn.write('\n'.encode("ascii"))
                else:
                    # TODO restart other procserv program
                    pass
                # if endline is not None:
                #     while True:
                #         line = tn.read_until('\n', 1)
                #         if line.endswith('\n'):
                #             line = line.rstrip()[:-1]
                #         if endline in line:
                #             break
                self.logger.info("restart section %s, port is %d" % (sec_name, port_num))
                time.sleep(0.1)
            except socket.timeout:
                self.logger.error("telnet timeout")
            finally:
                if tn is not None:
                    tn.close()

    def procboot_print_status(self, section="", user=""):
        all_sections = self.__get_sections(section, user)
        running_sec = self.pblfs.get_sections_list()
        print("%s%s%s%s" %
              ('{:20}'.format("prog"), '{:20}'.format("status"), '{:20}'.format("user"), '{:20}'.format("port")))
        if len(all_sections) == 0:
            print("%s%s%s%s" %
                  ('{:20}'.format("-"), '{:20}'.format("-"), '{:20}'.format("-"), '{:20}'.format("-")))
        for sec_name in all_sections:
            sections = self.cfg.get_one_prog_section(sec_name)
            prog = sec_name
            status = "stopped"
            if sec_name in running_sec:
                status = "running"
            user = sections['user']
            port = sections['port']
            print("%s%s%s%s" %
                  ('{:20}'.format(prog), '{:20}'.format(status), '{:20}'.format(user), '{:20}'.format(port)))

    def proboot_print_detail(self, section="", user=""):
        all_sections = self.__get_sections(section, user)
        running_sec = self.pblfs.get_sections_list()
        dic = {}
        for sec_name in all_sections:
            sections = self.cfg.get_one_prog_section(sec_name)
            if sec_name in running_sec:
                dic = self.pblfs.get_lockdata_from_secname(sec_name)
                dic["status"] = "running"
            else:
                dic["user"] = sections['user']
                dic["port"] = sections['port']
                dic["desc"] = sections['desc']
                dic["group"] = sections['group']
                dic["status"] = "stopped"
            print(json.dumps(dic, indent=4))

