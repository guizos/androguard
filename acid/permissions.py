#!/usr/bin/env python
from __future__ import division
import sys
import acidutils
import permission_detector
import intent_detector
import external_storage_detector
import shared_prefs_detector
import ntpath
PATH_INSTALL = "./"
sys.path.append(PATH_INSTALL)
from androguard.core.bytecodes import apk
import fnmatch

search_folder = sys.argv[1]
extension = ''
permissions_dict = {}
with open("mainpermissions.txt") as f:
    main_permissions = f.readlines()
main_permissions = [ x.rstrip() for x in main_permissions]
permission_set = set()
permission_matrix = {}
files = acidutils.get_all_apk_in_dir(search_folder,extension)
for file in files:
    try:
        a = apk.APK( file )
        permissions = fnmatch.filter(set(permission_detector.get_permissions(a)), 'android.permission.*')
        permissions = [element for element in permissions if element in main_permissions]
        permissions_dict[a.get_package()] = permissions
        permission_set = permission_set.union(permissions)
        for p in permissions:
            for p2 in permissions:
                if(p,p2) in permission_matrix:
                    permission_matrix[(p,p2)]+=1
                else:
                    permission_matrix[(p,p2)]=1
        #for p in new_set:
        #    print a.get_package()+","+p+"\n"
    except:
        pass
totals = {}
for p in permission_set:
    totals[p] = permission_matrix[(p,p)]
    #print p,totals[p]


print ("\t"),
for p in permission_set:
    print (p+", "),
print ""
for p in permission_set:
    print (p+"\t"),
    for p2 in permission_set:
        if (p,p2) in permission_matrix:
            print (str(permission_matrix[(p,p2)]/totals[p])+", "),
        else:
            print ("0, "),
    print ""
