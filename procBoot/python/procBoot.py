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
        usage="%prog [start|stop|restart|status|] [options] configFile")
    parser.add_option(
        "-n", "--name",
        action="store",
        type="string",
        default="",
        dest="section",
        help="process(section) names(any sections join \',\')"
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
        help="Execute user name(default: execute user)"
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
            sec = options.section
            user = options.user
            pb = ProcBoot(configFile)
            mode = args[0].upper()
            if not pb.cfg.is_ok_cfg():
                print(parser.print_help())
            if mode == "START" or mode == "STOP" or mode == "RESTART" or mode == "DETAIL" or mode == "STATUS":
                my_name = os.getlogin()
                if user == "":
                    user = my_name
                else:
                    if user != my_name:
                        print("ERROR: execute user is not permit")
                        parser.print_help()
                        exit(-1)
                if user != "":
                    if mode == "START":
                        pb.procboot_start(sec, user)
                    elif mode == "STOP":
                        pb.procboot_stop(sec, user)
                    elif mode == "RESTART":
                        pb.procboot_restart(sec, user)
                    elif mode == "STATUS":
                        pb.procboot_print_status(sec, user)
                    elif mode == "DETAIL":
                        pass
                    else:
                        parser.print_help()
            else:
                print("ERROR: command error %s" % mode)
                parser.print_help()
