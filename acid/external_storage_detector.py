import sys
import acidutils
PATH_INSTALL = "./"
from sets import Set
sys.path.append(PATH_INSTALL)
from androguard.core.bytecodes import apk



# Only detects those broadcast intents that are directly defined by constant string
# in the same method.

def trans_external_storage(apk):
    #print "*********"+name+"*********"
    channels = Set()
    if("android.permission.WRITE_EXTERNAL_STORAGE" in apk.get_permissions()):
        channels.add("external_storage")
    return channels

def recv_external_storage(apk):
    channels = Set()
    if("android.permission.READ_EXTERNAL_STORAGE" in apk.get_permissions() or "android.permission.WRITE_EXTERNAL_STORAGE" in apk.get_permissions()):
        channels.add("external_storage")
    return channels
