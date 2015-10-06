#!/usr/bin/env python

import sys
import acidutils
import permission_detector
import intent_detector
import external_storage_detector
import shared_prefs_detector
import ntpath
PATH_INSTALL = "./"
sys.path.append(PATH_INSTALL)
from androguard.core.bytecodes import dvm
from androguard.core.bytecodes import apk



#CONF["LAZY_ANALYSIS"] = True

if(len(sys.argv)!=2):
    print "app set folder is missing"
else:
    search_folder =  sys.argv[1]
    files = acidutils.get_all_apk_in_dir(search_folder,"apk")
    #Get permissions
    for file in files:
        try:
            a = apk.APK( file )
            j = dvm.DalvikVMFormat( a.get_dex() )
            permissions = permission_detector.get_permissions(a)
            for p in permissions:
                print "uses('"+a.get_package()+"','"+p+"')."
        except:
            pass
    #Get transmissions
    for file in files:
        try:
            a = apk.APK( file )
            j = dvm.DalvikVMFormat( a.get_dex() )
            channels = external_storage_detector.trans_external_storage(a)
            channels = channels.union(intent_detector.trans_broadcast_intents(j))
            channels = channels.union(shared_prefs_detector.trans_shared_prefs_other_package(ntpath.basename(file),j,a,True))
            channels = channels.union(shared_prefs_detector.trans_shared_prefs_same_package(ntpath.basename(file),j,a,True))
            for channel in channels:
                print "trans('"+a.get_package()+"','"+channel+"')."
        except Exception,e:
            print str(e)
    #Get receives
    for file in files:
        try:
            a = apk.APK( file )
            j = dvm.DalvikVMFormat( a.get_dex() )
            channels = external_storage_detector.recv_external_storage(a)
            channels = channels.union(intent_detector.recv_static_receiver_intents(a))
            channels = channels.union(intent_detector.recv_dynamic_receiver_intents(j))
            channels = channels.union(shared_prefs_detector.recv_shared_prefs_same_package(ntpath.basename(file),j,a,True))
            channels = channels.union(shared_prefs_detector.recv_shared_prefs_other_package(ntpath.basename(file),j,a,True))
            for channel in channels:
                print "recv('"+a.get_package()+"','"+channel+"')."
        except Exception,e:
            print str(e)
