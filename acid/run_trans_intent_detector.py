#!/usr/bin/env python

import sys
import acidutils
import intent_detector
import ntpath
PATH_INSTALL = "./"
sys.path.append(PATH_INSTALL)
from androguard.core.bytecodes import dvm
from androguard.core.bytecodes import apk



#CONF["LAZY_ANALYSIS"] = True

mode = int(sys.argv[1])
extension =""
if (len(sys.argv)==4):
    extension = sys.argv[3]

if mode==0:
    file  =  sys.argv[2]
    try:
        a = apk.APK( file+extension )
        j = dvm.DalvikVMFormat( a.get_dex() )
        channels = intent_detector.trans_broadcast_intents(ntpath.basename(file),j)
        for channel in channels:
            print "trans('"+a.get_package()+"','"+channel+"')."
    except:
        print "--Error with file "+file
elif mode== 1:
    search_folder =  sys.argv[2]
    files = acidutils.get_all_apk_in_dir(search_folder,extension)
    for file in files:
        try:
            a = apk.APK( file )
            j = dvm.DalvikVMFormat( a.get_dex() )
            channels = intent_detector.trans_broadcast_intents(ntpath.basename(file),j)
            for channel in channels:
                print "trans('"+a.get_package()+"','"+channel+"')."
        except:
            pass
