#!/usr/bin/env python

import sys
import acidutils
import permission_detector
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
    #try:
    a = apk.APK( file+extension )
    permissions = permission_detector.get_permissions(a)
    for p in permissions:
        print "uses('"+a.get_package()+"','"+p+"')."
    #except:
    #    print "--Error with file "+file
elif mode== 1:
    search_folder =  sys.argv[2]
    files = acidutils.get_all_apk_in_dir(search_folder,extension)
    for file in files:
        try:
            a = apk.APK( file )
            j = dvm.DalvikVMFormat( a.get_dex() )
            permissions = permission_detector.get_permissions(a)
            for p in permissions:
                print "uses('"+a.get_package()+"','"+p+"')."
        except:
            pass
