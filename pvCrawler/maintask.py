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
    if not es.index_exist(ioc_index):
        # es.index_create(ioc_index)
        resp = es.insert_data(index=ioc_index, doc=iocs)
        print("Insert all ioc " + ' to ES index: ' + ioc_index)
        print("Error?: " + str(resp['errors']))

    if not es.index_exist(pv_index):
        es.index_create(pv_index)
        for ioc in iocs:
            all_pv = dbreader.stcmd_reader(ioc['IOCPATH'])
            if not all_pv:
                print("Info: PVs are empty in this ioc: " + ioc['IOCPATH'])
                continue
            print(ioc['IOCPATH'], len(all_pv))
            resp = es.insert_data(index=pv_index, doc=all_pv)
            print("Insert ioc " + ioc['IOCNAME'] + ' to ES index: ' + pv_index)
            print("Error?: " + str(resp['errors']))


if __name__ == '__main__':
    maintask()
