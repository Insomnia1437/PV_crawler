# -*- coding: utf-8 -*-
# @Time    : 2019-12-18
# @File    : dbReader
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp
import os
import re
import subprocess
import shlex
from pprint import pprint


class dbReader:
    """
    search the st.cmd or similar file for two functions:
    dbLoadRecords()
    dbLoadTemplate()
    expand macro to get real PV Name, record type etc.
    Using EPICS extensions: msi to expand.
    Command is like:
    ./msi -M "SYS=LIiEV,D=evg0,EVG=SKBEVG0" -o result.log ../workspace/SKBEVG-config.db
    ./msi -V -o outfile -I dir -M subs -S subfile template
    """

    def __init__(self, _msi_path):
        self.msi_path = _msi_path

    def stcmd_reader(self, stcmd):
        if not os.path.exists(stcmd) or not stcmd.endswith('.cmd'):
            return []
        ioc_path = '/'.join(stcmd.split('/')[:-3])
        all_pv = []
        with open(stcmd, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or len(line) == 0:
                    # comment line or blank line
                    continue
                if line.startswith("dbLoadTemplate"):
                    line = line.replace("dbLoadTemplate", "")
                    line = line.replace("(", "")
                    line = line.replace(")", "")
                    # line = line.replace("\"", "")
                    all_pv.extend(self.read_templates(ioc_path, stcmd, line.strip()))
                if line.startswith("dbLoadRecords"):
                    line = line.replace("dbLoadRecords", "")
                    line = line.replace("(", "")
                    line = line.replace(")", "")
                    # line = line.replace("\"", "")
                    db = line.split(',', 1)
                    if len(db) == 1:
                        # no substitution
                        all_pv.extend(self.read_records(ioc_path, stcmd, db[0].strip(), None))
                    else:
                        # with substitutions
                        all_pv.extend(self.read_records(ioc_path, stcmd, db[0].strip(), db[1]))
        return all_pv

    def read_records(self, ioc_path, stcmd, db, para):

        full_path = os.path.join(ioc_path, db)
        if para:
            cmd = self.msi_path + " -M " + para + " " + full_path
        else:
            cmd = self.msi_path + " " + full_path
        # print(cmd)
        return self.call_msi(ioc_path, cmd)

    def read_templates(self, ioc_path, stcmd, template):
        full_path = os.path.join(ioc_path, template)
        cmd = self.msi_path + " -S " + full_path
        return self.call_msi(ioc_path, cmd, stcmd)

    def call_msi(self, ioc_path, cmd, stcmd):
        args = shlex.split(cmd)
        try:
            obj = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=ioc_path)
            stdout, stderr = obj.communicate()
            if not stderr:
                return self.get_pv(ioc_path, str(stdout, encoding='utf-8'), stcmd)
            else:
                print(str(stderr, encoding='utf-8'), cmd)
        except subprocess.CalledProcessError as e:
            print(e.output, e.returncode)

    def get_pv(self, ioc_path, db_data, stcmd):
        # can not recognize correctly if several fields are in the same line (though allowed by EPICS IOC)
        pattern = r"^\s*record\((?P<record>.*)\)|^\s*field\((?P<field>.*)\)"
        match_res = re.finditer(pattern, db_data, re.M)
        pvs = []
        current_rec_dict = {}
        for mt in match_res:
            '''
                mt.groupdict is like:
                {'record': 'sub,"test:subExample"', 'field': None}
                {'record': None, 'field': 'INAM,"mySubInit"'}
                {'record': None, 'field': 'SNAM,"mySubProcess"'}
            '''
            line = mt.groupdict()
            record, field = line['record'], line['field']
            if not record and not field:
                continue
            if record and field:
                # give some waring
                print("Error in IOC: %s, db: %s-%s", ioc_path, record, field)
                return -1
            if record:
                if len(current_rec_dict) != 0:
                    pvs.append(current_rec_dict)
                current_rec_dict = {}
                try:
                    record_type, record_name = record.strip().split(',')
                    record_type = record_type.strip()
                    record_name = record_name.replace('\"', '').strip()
                    current_rec_dict['PVTYPE'] = record_type
                    current_rec_dict['PVNAME'] = record_name
                    # current_rec_dict['IOCPATH'] = stcmd
                except RuntimeError:
                    print(RuntimeError)
            if field:
                try:
                    field_type, field_value = field.strip().split(',', maxsplit=1)
                    field_type = field_type.strip()
                    field_value = field_value.replace('\"', '').strip()
                    current_rec_dict[field_type] = field_value
                except RuntimeError:
                    print(RuntimeError)
        return pvs

