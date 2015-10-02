#!/usr/bin/env python

import sys
import os
from subprocess import check_output
folder = sys.argv[2]

#dentro del folder, ejecutar para cada carpeta que haya dentro.
folders = next(os.walk(folder))[1]
output_name = sys.argv[1]
trans_results = []
recv_results = []
for subfolder in folders:
    app_folder = folder+"/"+subfolder
    print app_folder
    trans_intent_result = check_output(["./acid/trans_intent_prolog_generator.py", "1",app_folder])
    trans_results.append(trans_intent_result)
    with open(output_name+"_trans_intent_result_"+subfolder, "w") as text_file:
        text_file.write(trans_intent_result)
    print "Trans_intent for "+app_folder+" finished"
    recv_intent_result = check_output(["./acid/recv_intent_prolog_generator.py", "1",app_folder])
    recv_results.append(recv_intent_result)
    with open(output_name+"_recv_intent_result_"+subfolder, "w") as text_file:
        text_file.write(recv_intent_result)
    print "Recv_intent for "+app_folder+" finished"
    trans_external_storage_result = check_output(["./acid/trans_external_storage_prolog_generator.py", "1",app_folder])
    trans_results.append(trans_external_storage_result)
    with open(output_name+"_trans_external_storage_result_"+subfolder, "w") as text_file:
        text_file.write(trans_external_storage_result)
    print "Trans_external storage for "+app_folder+" finished"
    recv_external_storage_result = check_output(["./acid/recv_external_storage_prolog_generator.py", "1",app_folder])
    recv_results.append(recv_external_storage_result)
    with open(output_name+"_recv_external_storage_result_"+subfolder, "w") as text_file:
        text_file.write(recv_external_storage_result)
    print "Recv_external storage for "+app_folder+" finished"
    trans_sharedprefs_result = check_output(["./acid/trans_sharedprefs_detector_prolog_generator.py", "1",app_folder])
    trans_results.append(trans_sharedprefs_result)
    with open(output_name+"_trans_sharedprefs_result_"+subfolder, "w") as text_file:
        text_file.write(trans_sharedprefs_result)
    print "Trans_sharedprefs for "+app_folder+" finished"
    recv_sharedprefs_result = check_output(["./acid/recv_sharedprefs_prolog_generator.py", "1",app_folder])
    recv_results.append(recv_sharedprefs_result)
    with open(output_name+"_recv_sharedprefs_result_"+subfolder, "w") as text_file:
        text_file.write(recv_sharedprefs_result)
    print "Recv_sharedprefs for "+app_folder+" finished"
with open(output_name+"_overall", "w") as text_file:
    for res in trans_results:
        text_file.write(res)
    for res in recv_results:
        text_file.write(res)
print "Overall Results finished"
print "All done."
