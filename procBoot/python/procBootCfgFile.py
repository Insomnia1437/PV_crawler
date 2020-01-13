# -*- coding: utf-8 -*-
# @Time    : 2020-01-09
# @File    : procBootCfgFile.py
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp

import configparser
import os
import platform

_PROCSERV_SEC = 'procServ'
_PROCBOOT_SEC = 'procBoot'
_DEFAULT_SEC = 'default'


class CfgFile(object):
    __shared_state = {}

    def __init__(self, filename):
        self.__dict__ = self.__shared_state
        if len(self.__dict__) == 0:
            self.cfg = configparser.ConfigParser()
            self.cfg.read(filename)
            self.default_section = self.get_default_section()

    def _convlogmacro(self, basestr, **kwargs):
        rtn = basestr
        for key, val in kwargs.items():
            mkey = '$' + key
            if mkey in basestr:
                rtn = rtn.replace(mkey, val)
        return rtn

    def convlog(self, basestr):
        host_str = platform.uname()[1].split('.')[0]
        return self._convlogmacro(basestr, host=host_str)

    def convlogsection(self, basestr, sectionstr):
        host_str = platform.uname()[1].split('.')[0]
        return self._convlogmacro(basestr, host=host_str, section=sectionstr)

    def _get_value(self, seckey, key, default=""):
        rtn = None
        try:
            if self.cfg.has_option(seckey, key):
                rtn = self.cfg.get(seckey, key)
            elif default != "":
                rtn = default
        except configparser.Error as e:
            print("!!!FATAL: configparser error: %s \n please check your config file.", e.message)
            exit(-1)
        return rtn

    def get_procserv_section(self):
        seckey = _PROCSERV_SEC
        return {'procserv': self._get_value(seckey, 'procserv'),
                'lockpath': self.convlogsection(self.cfg.get(seckey, 'lockpath'), seckey),
                }

    def get_procserv_lockpath(self):
        return self.get_procserv_section()["lockpath"]

    def get_procserv_procserv(self):
        return self.get_procserv_section()["procserv"]

    def get_procboot_section(self):
        seckey = _PROCBOOT_SEC
        return {'logpath': self.convlogsection(self._get_value(seckey, 'logpath'), seckey),
                'log': self.convlogsection(self._get_value(seckey, 'log'), seckey)
                }

    def get_procboot_logfile(self):
        return os.path.join(self.get_procboot_section()['logpath'], self.get_procboot_section()['log'])

    def get_default_section(self):
        seckey = _DEFAULT_SEC
        return {'startcmnd': self._get_value(seckey, 'startcmnd'),
                'endline': self._get_value(seckey, 'endline'),
                'restartwait': self._get_value(seckey, 'restartwait'),
                'user': self._get_value(seckey, 'user'),
                'logpath': self._get_value(seckey, 'logpath'),
                'log': self._get_value(seckey, 'log'),
                'desc': self._get_value(seckey, 'desc'),
                'group': self._get_value(seckey, 'group'),
                }

    def get_one_prog_section(self, seckey):
        return {'cmnd': self.convlogsection(self.cfg.get(seckey, 'cmnd'), seckey),
                'path': self.convlogsection(self.cfg.get(seckey, 'path'), seckey),
                'port': self._get_value(seckey, 'port'),
                'startcmnd': self._get_value(seckey, 'startcmnd', self.get_default_section()['startcmnd']),
                'endline': self._get_value(seckey, 'endline', self.default_section['endline']),
                'restartwait': self._get_value(seckey, 'restartwait', self.default_section['restartwait']),
                'user': self._get_value(seckey, 'user', self.default_section['user']),
                'logpath': self.convlogsection(self._get_value(seckey, 'logpath', self.default_section['logpath']),
                                               seckey),
                'log': self.convlogsection(self._get_value(seckey, 'log', self.default_section['log']), seckey),
                'desc': self.convlogsection(self._get_value(seckey, 'desc', self.default_section['desc']), seckey),
                'group': self._get_value(seckey, 'group', self.default_section['group']),
                }

    def get_prog_sections(self, section="", user=""):
        seclists = self.cfg.sections()
        seclists.remove(_PROCBOOT_SEC)
        seclists.remove(_DEFAULT_SEC)
        seclists.remove(_PROCSERV_SEC)
        if user != "":
            sss = []
            for s in seclists:
                sec = self.get_one_prog_section(s)
                if sec['user'] == user:
                    sss.append(s)
            if len(sss) == 0:
                print("No such user in config file")
                return sss
            seclists = sss

        if section != "":
            sss = []
            for sec in section:
                if sec in seclists:
                    sss.append(sec)
                else:
                    print("WARNING: No such section in config file: %s, will be omitted" % sec)
            if len(sss) == 0:
                print("Error: No section specified")
                return sss
            seclists = sss

        return seclists

    def search_prog_by_port(self, port, user=None):
        """
        search configure file whether @port exist
        :param port: procServ port for telnet
        :param user: user
        :return: section name or None
        """
        rtn = None
        seclists = self.get_prog_sections(user=user)
        for sec in seclists:
            tmpport = self._get_value(sec, 'port')
            if int(tmpport) == port:
                rtn = sec
                break
        return rtn

    def _check_procserv_section(self):
        rtn = []
        error_prefix = "[procServ ERROR]:"
        section = self.get_procserv_section()
        if section is not None:
            procserv_file = section['procserv']
            lockpath = section['lockpath']
            # check procserv
            if not os.path.exists(procserv_file):
                rtn.append("%s procserv does not exist\n%s" % (error_prefix, procserv_file))
            elif not os.path.isfile(procserv_file):
                rtn.append("%s procserv is not a file or link\n%s" % (error_prefix, procserv_file))
            elif not os.access(procserv_file, os.X_OK):
                rtn.append("%s procserv file cannot be executed\n%s" % (error_prefix, procserv_file))

            # check lockpath
            if not os.path.exists(lockpath):
                rtn.append("%s lockpath does not exist\n%s" % (error_prefix, lockpath))
            elif not os.path.isdir(lockpath):
                rtn.append("%s lockpath is not a directory\n%s" % (error_prefix, lockpath))
            elif not os.access(lockpath, os.W_OK):
                rtn.append("%s lockpath cannot be wrote\n%s" % (error_prefix, lockpath))

        return rtn

    def _check_procboot_section(self):
        rtn = []
        error_prefix = "[procBoot ERROR]:"
        section = self.get_procboot_section()
        if section is not None:
            logpath = section['logpath']
            # check lockpath
            if not os.path.exists(logpath):
                rtn.append("%s logpath does not exist\n%s" % (error_prefix, logpath))
            elif not os.path.isdir(logpath):
                rtn.append("%s logpath is not a directory\n%s" % (error_prefix, logpath))
            elif not os.access(logpath, os.W_OK):
                rtn.append("%s logpath cannot be wrote\n%s" % (error_prefix, logpath))

        return rtn

    def _check_prog_section(self):
        rtn = []
        error_prefix = "[prog ERROR]:"
        sections = self.get_prog_sections()
        if len(sections) == 0:
            rtn.append("%s no section" % error_prefix)
        else:
            for sec in sections:
                section = self.get_one_prog_section(sec)
                cmnd = section['cmnd']
                path = section['path']
                user = section['user']
                port = section['port']
                logpath = section['logpath']
                # path
                if not os.path.exists(path):
                    rtn.append("[%s]:path is not exist \n%s" % (sec, path))
                elif not os.path.isdir(path):
                    rtn.append("[%s]:path is not directory \n%s" % (sec, path))
                elif not os.access(path, os.W_OK):
                    rtn.append("[%s] path cannot be wrote \n%s" % (sec, path))

                # cmnd
                if os.path.exists(path):
                    abs_cmnd = os.path.join(path, cmnd)
                    cmd_sep = cmnd.split(' ')
                    if len(cmd_sep) > 1:
                        # Not EPICS IOC command
                        abs_cmnd = cmd_sep[0]
                    if not os.path.exists(abs_cmnd):
                        rtn.append("[%s]:cmnd file not exist \n%s" % (sec, abs_cmnd))
                    elif not os.access(abs_cmnd, os.X_OK):
                        rtn.append("[%s]:cmnd cannot be executed \n%s" % (sec, abs_cmnd))

                # user
                try:
                    # print user
                    sys = platform.platform().split("-")[0]
                    if sys == "Linux" or sys == "Darwin" or sys == "macOS":
                        import pwd
                        pwd.getpwnam(user)
                    else:
                        print("FATAL ERROR: sorry, %s system is not supported yet." % sys)
                        exit(-1)
                except (KeyError, TypeError):
                    rtn.append("[%s]:user %s not found" % (sec, user))

                # port
                try:
                    port_num = int(port)
                    if (port_num < 1024) or (port_num > 65536):
                        rtn.append("[%s]:port %d should between 1024~65536" % (sec, port_num))
                except (ValueError, SyntaxError):
                    rtn.append("[%s]:port %s is not integer" % (sec, port))

                # log path
                if not os.path.exists(logpath):
                    rtn.append("[%s]:logpath directory not exist \n%s" % (sec, logpath))
                elif not os.path.isdir(logpath):
                    rtn.append("[%s]:logpath is not directory \n%s" % (sec, logpath))
                elif not os.access(logpath, os.W_OK):
                    rtn.append("[%s]:logpath cannot be wrote \n%s" % (sec, logpath))

        return rtn

    def _check_section_overlap(self):
        rtn = []
        sections = self.get_prog_sections()
        cmd_set = set()
        port_set = set()
        log_set = set()
        for sec in sections:
            section = self.get_one_prog_section(sec)
            cmnd = section['cmnd']
            path = section['path']
            port = section['port']
            logpath = section['logpath']
            log = section['log']
            abs_cmnd = os.path.join(path, cmnd)
            abs_log = os.path.join(logpath, log)
            if abs_cmnd in cmd_set:
                rtn.append("[%s]:cmnd overlap \n%s" % (sec, abs_cmnd))
            else:
                cmd_set.add(abs_cmnd)

            if port in port_set:
                rtn.append("[%s]:port overlap \n%s" % (sec, port))
            else:
                port_set.add(port)

            if abs_log in log_set:
                rtn.append("[%s]:port overlap \n%s" % (sec, abs_log))
            else:
                log_set.add(abs_log)

        return rtn

    def check_cfg(self):
        rtn = []
        rtn.extend(self._check_procboot_section())
        rtn.extend(self._check_procserv_section())
        rtn.extend(self._check_prog_section())
        rtn.extend(self._check_section_overlap())
        return rtn

    def is_ok_cfg(self):
        res = self.check_cfg()
        if len(res) >= 1:
            for i in map(lambda x: x + "\n", res):
                print(i)
            # exit(-1)
        else:
            return True


if __name__ == '__main__':
    cfg1 = CfgFile(r"/Users/sdcswd/workspace/python/PV_crawler/procBoot/config/boot_test.config")
    # print()
    # map(cfg1._get_value, (seckey, 'cmnd'))
    cfg1.is_ok_cfg()
    print(cfg1.get_prog_sections())
    # a = cfg1.check_cfg()
    # if len(a) > 0:
    #     # print(a)
    #     for i in map(lambda x: x + "\n", a):
    #         print(i)
    #     exit(-1)
