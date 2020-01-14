# -*- coding: utf-8 -*-
# @Time    : 2020-01-12
# @File    : procBoot
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp
import optparse
import os
from procBootServ import ProcBoot

if __name__ == "__main__":
    parser = optparse.OptionParser(
        usage="%prog.py [start|stop|restart|status|detail] [options] configFile")
    parser.add_option(
        "-n", "--name",
        action="store",
        type="string",
        default="",
        dest="section",
        help="process(section) names(any sections join \',\', NO SPACE!!!)"
    )
    # parser.add_option(
    #     "-f", "--format",
    #     action="store",
    #     dest="format",
    #     choices=['print', 'xml', 'json'],
    #     default='print',
    #     help="status output format"
    # )
    parser.add_option(
        "-u", "--user",
        action="store",
        type="string",
        default="",
        dest="user",
        help="For [status|detail] mode: if specified, show only this user's program status, if not, show all.\n"
             "For [start|stop|restart] mode: if you want to run user[u]'s program you must switch to user[u]"
    )
    (options, args) = parser.parse_args()

    if len(args) < 2:
        print('argument error ')
        parser.print_help()
    else:
        configFile = args[1]
        if not os.path.exists(configFile):
            print('configFile not exist! %s' % configFile)
            parser.print_help()
        else:
            sec = str(options.section)
            if sec != "":
                temp_sec = sec.split(",")
                sec = [i.strip() for i in temp_sec]
            user = options.user
            pb = ProcBoot(configFile)
            mode = args[0].upper()
            if not pb.cfg.is_ok_cfg():
                parser.print_help()
                exit(-1)
            pb.pblfs.check_lockfile_with_process()
            if mode == "START" or mode == "STOP" or mode == "RESTART":
                my_name = os.getlogin()
                if user == "":
                    user = my_name
                else:
                    if user != my_name:
                        print("ERROR: You must be login user to change procBoot")
                        parser.print_help()
                        exit(0)
                if user != "":
                    if mode == "START":
                        pb.procboot_start(sec, user)
                    elif mode == "STOP":
                        pb.procboot_stop(sec, user)
                    elif mode == "RESTART":
                        pb.procboot_restart(sec, user)
                    else:
                        parser.print_help()
            elif mode == "DETAIL" or mode == "STATUS":
                if mode == "STATUS":
                    pb.procboot_print_status(sec, user)
                elif mode == "DETAIL":
                    pb.proboot_print_detail(sec, user)
                else:
                    parser.print_help()
            else:
                print("ERROR: command error %s" % mode)
                parser.print_help()
                exit(0)
