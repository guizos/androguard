#!/usr/bin/env python

import sys
import acidutils
import permission_detector
import ntpath
from subprocess import check_output
PATH_INSTALL = "./"
sys.path.append(PATH_INSTALL)
from androguard.core.bytecodes import dvm
from androguard.core.bytecodes import apk



#CONF["LAZY_ANALYSIS"] = True


app_folder =  sys.argv[1]
option = ""
if(len(sys.argv)>2):
    option = sys.argv[2]
trans_results = ""
recv_results = ""
permissions = ""
trans_intent_result = check_output(["./acid/trans_intent_prolog_generator.py", "1",app_folder])
trans_results = trans_results + trans_intent_result
recv_intent_result = check_output(["./acid/recv_intent_prolog_generator.py", "1",app_folder])
recv_results = recv_results + recv_intent_result
if(option != "no_external"):
    trans_external_storage_result = check_output(["./acid/trans_external_storage_prolog_generator.py", "1",app_folder])
    trans_results = trans_results + trans_external_storage_result
    recv_external_storage_result = check_output(["./acid/recv_external_storage_prolog_generator.py", "1",app_folder])
    recv_results = recv_results + recv_external_storage_result
trans_sharedprefs_result = check_output(["./acid/trans_sharedprefs_prolog_generator.py", "1",app_folder])
trans_results = trans_results + trans_sharedprefs_result
recv_sharedprefs_result = check_output(["./acid/recv_sharedprefs_prolog_generator.py", "1",app_folder])
recv_results = recv_results + recv_sharedprefs_result
permissions = check_output(["./acid/permission_prolog_generator.py", "1",app_folder])
print permissions.strip('\n')
for r in trans_results.split("\n"):
    print r.strip('\n')
for r in recv_results.split("\n"):
    print r.strip('\n')
