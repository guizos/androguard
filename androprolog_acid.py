#!/usr/bin/env python
from sets import Set


__author__ = 'guizos'

import sys
import os
import traceback
import fnmatch
from optparse import OptionParser
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis


def get_all_apk_in_dir(folder,extension):
    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for filename in fnmatch.filter(filenames, '*'+extension):
            if ".DS_Store" not in filename:
                matches.append(os.path.join(root, filename))
    return matches


app_folder =  sys.argv[1]
result = sys.argv[2]
sends = Set()
receives = Set()
permissions = []
files = get_all_apk_in_dir(app_folder,"*")
for file in files:
    print "analyzing file "+file
    try:
        a = apk.APK(file)
        j = dvm.DalvikVMFormat(a.get_dex())
        ja = analysis.newVMAnalysis(j)
        permissions.extend([(str(a.get_package()), permission) for permission in a.get_permissions()])
        print "Looking for Intent Sends"
        sends.update([(str(a.get_package()),"i_"+intent.action) for intent in ja.get_implicit_intents()])
        print "Looking for Shared Prefs Sends"
        sends.update([(str(a.get_package()),"sp_"+shared.package+"_"+shared.preference_file) for shared in ja.get_shared_preferences_writes(a)])
        print "Looking for Dynamic Receivers"
        receives.update([(str(a.get_package()),"i_"+receiver.get_action()) for receiver in ja.get_dynamic_receivers()])
        print "Looking for Static Receivers"
        receives.update([(str(a.get_package()),"i_"+receiver.get_action()) for receiver in ja.get_static_receivers(a)])
        print "Looking for Shared Prefs Receives"
        receives.update([(str(a.get_package()),"sp_"+shared.package+"_"+shared.preference_file) for shared in ja.get_shared_preferences_reads(a)])
    except:
        print "--Error with file "+file
        traceback.print_exc()
with open(result, 'w') as f:
    for permission in permissions:
        f.write("uses("+permission[0]+","+permission[1]+").\n")
    for send in sends:
        f.write("trans("+send[0]+","+send[1]+").\n")
    for receive in receives:
        f.write("recv("+receive[0]+","+receive[1]+").\n")
print "Results saved in "+result






