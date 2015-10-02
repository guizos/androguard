import sys
import acidutils
PATH_INSTALL = "./"
from sets import Set
sys.path.append(PATH_INSTALL)
from androguard.core.bytecodes import apk



# Only detects those broadcast intents that are directly defined by constant string
# in the same method.

def get_permissions(apk):
    #print "*********"+name+"*********"
    permissions = Set()
    permissions = [ "'%s'",x for x in apk.get_permissions() ]
    return permissions
