#!/usr/bin/env python

import sys
import acidutils
import intent_detector
import ntpath
PATH_INSTALL = "./"
sys.path.append(PATH_INSTALL)
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm



#CONF["LAZY_ANALYSIS"] = True


if (len(sys.argv)==1):
    print "****Extracts static recievers from apk files**** "
    print " Usage:"
    print " Single file mode:"
    print '> run_static_receiver_detector 0 filename [extension_addition]'
    print " Recursive mode:"
    print '> run_static_receiver_detector 1 folder [extension_filter]'
    sys.exit()

mode = int(sys.argv[1])
extension =""
if (len(sys.argv)==4):
    extension = sys.argv[3]

if mode==0:
    file  =  sys.argv[2]
    a = apk.APK( file+extension )
    j = dvm.DalvikVMFormat( a.get_dex() )
    channels = intent_detector.recv_static_receiver_intents(ntpath.basename(file),a)
    channels = channels.union(intent_detector.recv_dynamic_receiver_intents(ntpath.basename(file),j))
    for channel in channels:
        print "recv('"+a.get_package()+"','"+channel+"')."
elif mode== 1:
    search_folder =  sys.argv[2]
    files = acidutils.get_all_apk_in_dir(search_folder,extension)
    for file in files:
        try:
            a = apk.APK( file )
            j = dvm.DalvikVMFormat( a.get_dex() )
            channels = intent_detector.recv_static_receiver_intents(ntpath.basename(file),a)
            channels = channels.union(intent_detector.recv_dynamic_receiver_intents(ntpath.basename(file),j))
            for channel in channels:
                print "recv('"+a.get_package()+"','"+channel+"')."
        except:
            #print "--Error with file "+file
            pass
