# -*- coding: utf-8 -*-
# @Time    : 2020-05-16
# @File    : maintask
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@gmail.com

import sys
import os

sys.path.append(sys.path[0])
import configparser
from dbReader import dbReader
from iocReader import iocReader
from esConnector import ESConnector


def maintask():
    # check config
    config_path = os.path.join(sys.path[0], 'epics.config')
    if not os.path.exists(config_path):
        print(config_path)
        print('Error: file not exist...exit now.')
        return -1
    cfg = configparser.ConfigParser()
    cfg.read(config_path)
    try:
        tbl_path = cfg.get('epics', 'tblpath')
        msi_path = cfg.get('epics', 'msipath')
        es_addr = cfg.get('epics', 'es')
        pv_index = cfg.get('epics', 'pvindex')
        ioc_index = cfg.get('epics', 'iocindex')
    except configparser.Error as e:
        print("Error: configparser error: %s \n please check your config file.", e)
        exit(-1)

    # chekc elastic search
    es = ESConnector("http://" + es_addr)
    if not es.es_ok():
        print("Elastic Search is not available, check again.")
        return -1
    iocreader = iocReader(tbl_path)
    dbreader = dbReader(msi_path)
    iocs = iocreader.read_ioc()
    if not es.es.indices.exists(ioc_index):
        print('Info: index already exists! %s' % ioc_index)
    else:
        resp = es.insert_ioc(index=ioc_index, ioc_doc=iocs)
        print("Insert ioc: " + str(resp['errors']) + ' to ES index: ' + ioc_index)
    if not es.es.indices.exists(ioc_index):
        print('Info: index already exists! %s' % pv_index)
    else:
        for ioc in iocs:
            all_pv = dbreader.stcmd_reader(ioc['IOCPATH'])
            resp = es.insert_pv(index=pv_index, db_doc=all_pv)
            print("Insert ioc: " + ioc['IOCNAME'] + str(resp['errors']) + ' to ES index: ' + pv_index)


if __name__ == '__main__':
    maintask()
