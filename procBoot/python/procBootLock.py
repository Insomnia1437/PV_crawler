# -*- coding: utf-8 -*-
# @Time    : 2020-01-11
# @File    : procBootLock
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp

"""
lock file format

{
    "pid": process id,
    "cmnd": command,
    "boot_time": process booted datetime(YYYY/MM/DD hh:mm:ss),
    "info": { # boot process any info

    }
    "filename": filename
}

"""
import glob
import json
import os
import time

from procBootLogger import Logger


class ProcBootLockFiles(object):
    def __init__(self, lock_path, logpath):
        self.lfs = {}
        self.lock_path = lock_path
        log_obj = Logger(logpath)
        self.log = log_obj.logger
        self._read_all_files()

    def _update_lock_data(self):
        self._read_all_files()

    def _read_all_files(self):
        self.lfs = {}
        files = glob.glob(os.path.join(self.lock_path, "*.lock"))
        self.log.debug("lock path:%s, lock files:%s" % (self.lock_path, files))
        for fd in files:
            try:
                l_data = self._read_lockfile(fd)
                pid = l_data['pid']
                self.lfs[pid] = l_data
            except KeyError:
                self.log.error("Error when read lock file %s" % fd)

    def _read_lockfile(self, lock_file):
        lock_data = {}
        if not os.path.exists(lock_file):
            self.log.error("lock file: %s does not exist, unable to read!" % lock_file)
        else:
            fd = open(lock_file, 'r')
            try:
                lock_data = json.load(fd)
            except json.JSONDecodeError:
                self.log.error("load lock file %s error" % lock_file, exc_infor=True)
            finally:
                fd.close()
        return lock_data

    def create_lockfile(self, pid, port, cmnd, **kwargs):
        if pid in self.get_PID_list():
            self.log.error("PID %s already exists" % pid)
            return
        now = time.localtime()
        fn = "%d_%s.lock" % (pid, time.strftime("%Y_%m_%d_%H_%M_%S", now))
        if not os.path.exists(self.lock_path):
            try:
                os.makedirs(self.lock_path)
            except FileExistsError:
                self.log.debug("create lock path: '%s' error" % self.lock_path)
        fn = os.path.join(self.lock_path, fn)
        lock_items = {'pid': pid, 'port': port, 'cmnd': cmnd, 'boot_time': time.strftime("%Y/%m/%d %H:%M:%S", now),
                      'filename': fn}
        if len(kwargs) > 0:
            lock_items['info'] = kwargs

        fd = open(fn, 'w')
        try:
            json.dump(lock_items, fd, indent=4, sort_keys=False)
            # self.lfs[pid] = lock_items
            self.log.info("Create lock file: PID %d, port: %d, cmnd: %s " % (pid, port, cmnd))
        except IOError:
            self.log.error("dump lock file %s error" % fn, exc_infor=True)
        finally:
            fd.close()
        self._update_lock_data()

    def remove_lockfile(self, pid):
        if pid in self.get_PID_list():
            filename = self.get_lockdata_from_PID(pid)["filename"]
            self.log.debug("remove lock file %s for pid %s", (filename, pid))
            if len(filename) == 0:
                self.log.error("PID %s : filename is None" % pid)
            if os.path.exists(filename):
                os.remove(filename)
                self.log.info("Remove lock file for PID %s" % pid)
            else:
                self.log.error("file %s does not exist" % filename)
        self._update_lock_data()

    def port_exist_in_lock(self, port):
        rtn = [False, ""]
        for lf in self.lfs.values():
            if int(lf["port"]) == int(port):
                self.log.debug("port: '%s' is already used" % port)
                rtn[0] = True
                rtn[1] = lf['cmnd']
                break
        return rtn

    def get_PID_from_port(self, port):
        for pid in self.get_PID_list():
            lockdata = self.get_lockdata_from_PID(pid)
            if int(lockdata['port']) == int(port):
                return int(pid)
        return False

    def get_PID_list(self):
        return self.lfs.keys()

    def get_lockdata_from_PID(self, pid):
        return self.lfs[pid]

    def get_all_lockdata(self):
        return self.lfs.values()

    def get_sections_list(self):
        rtn = []
        for l_data in self.get_all_lockdata():
            rtn.append(l_data['info']['section'])
        return rtn


if __name__ == '__main__':
    pblf = ProcBootLockFiles("lock/", "test.log")
    print(pblf.get_PID_list())
    # print(pblf.get_lock_info(12345))
    # print(pblf.get_lock_info(12345)["pid"])
    pblf.create_lockfile(1, port=333301, cmnd="some cmd", user="sdcswd", group="control")
    pblf.create_lockfile(2, port=333302, cmnd="another cmd", user="root", group="control")
    pblf.create_lockfile(3, port=333303, cmnd="ioc cmd", user="sdcswd", group="control")
    print(pblf.get_PID_list())
    # print(pblf.get_all_lockdata())
    print(pblf.port_exist_in_lock(333303))
    # time.sleep(5)
    # pblf.remove_lockfile(3)
    # print(pblf.check_lock(333303, "ass cmd"))
    print(pblf.get_PID_list())