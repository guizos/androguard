import sys
import acidutils
PATH_INSTALL = "./"
sys.path.append(PATH_INSTALL)
from sets import Set
from androguard.core.bytecodes import dvm
from androguard.core.bytecodes import apk
from androguard.core.androconf import CONF
from androguard.core.analysis import analysis, ganalysis




def trans_shared_prefs_same_package(name,dalvik,apk,add_package):
    channels = Set()
    for m in dalvik.get_methods():
        for index,i in enumerate(m.get_instructions()):
            if (i.get_op_value()==0x6E) and ("Landroid/support" not in m.get_class_name()):#invoke-virtual
                if ("getSharedPreferences" in i.get_output()):
                    if(not is_create_package_context_present(m,index-1)):
                        if(edit_is_present_later(m,index)):
                            new_var = i.get_output().split(",")[1].strip()
                            pref_file = acidutils.track_string_value(m,index-1,new_var)
                            package = apk.get_package()
                            if(pref_file!=""):
                                found = 1
                                if(add_package):
                                    channels.add("prefs_"+package+"_"+pref_file)
                                else:
                                    channels.add("prefs_"+pref_file)
    return channels

def trans_shared_prefs_other_package(name,dalvik,apk,add_package):
    #print "*********"+name+"*********"
    channels = Set()
    for m in dalvik.get_methods():
        for index,i in enumerate(m.get_instructions()):
            if (i.get_op_value()==0x6E) and ("Landroid/support" not in m.get_class_name()):#invoke-virtual
                if ("createPackageContext" in i.get_output()):
                    if(edit_is_present_later(m,index)):
                        var = i.get_output().split(",")[2].strip()
                        file_name = track_get_shared_preferences_direct(m,index+1,var)
                        name_var = i.get_output().split(",")[1].strip()
                        package = acidutils.track_string_value(m,index-1,name_var)
                        package2 = apk.get_package()
                        if(package2==package):
                            print "Packages are equal WHY change???!!!"
                        if(file_name!=""):
                            found = 1
                            if(add_package):
                                channels.add("prefs_"+package+"_"+file_name)
                            else:
                                channels.add("prefs_"+file_name)
    return channels

def edit_is_present_later(method,index):
    present = None
    try:
        while index < method.get_length():
            ins = method.get_instruction(index)
            if("android/content/SharedPreferences;->edit()" in ins.get_output()):
                return True
            index = index + 1
    except IndexError:
        #Fail gently. beginning of the array reached
        return None
    return None

def recv_shared_prefs_same_package(name,dalvik,apk,add_package):
    channels = Set()
    for m in dalvik.get_methods():
        for index,i in enumerate(m.get_instructions()):
            if (i.get_op_value()==0x6E) and ("Landroid/support" not in m.get_class_name()):#invoke-virtual
                if ("getSharedPreferences" in i.get_output()):
                    if(not is_create_package_context_present(m,index-1)):
                        new_var = i.get_output().split(",")[1].strip()
                        pref_file = acidutils.track_string_value(m,index-1,new_var)
                        package = apk.get_package()
                        if(pref_file!=""):
                            found = 1
                            if(add_package):
                                channels.add("prefs_"+package+"_"+pref_file)
                            else:
                                channels.add("prefs_"+pref_file)
    #if found == 0:
        #print "No action intent found in "+name
    return channels

def recv_shared_prefs_other_package(name,dalvik,apk,add_package):
    #print "*********"+name+"*********"
    channels = Set()
    for m in dalvik.get_methods():
        for index,i in enumerate(m.get_instructions()):
            if (i.get_op_value()==0x6E) and ("Landroid/support" not in m.get_class_name()):#invoke-virtual
                if ("createPackageContext" in i.get_output()):
                    var = i.get_output().split(",")[2].strip()
                    file_name = track_get_shared_preferences_direct(m,index+1,var)
                    name_var = i.get_output().split(",")[1].strip()
                    package = acidutils.track_string_value(m,index-1,name_var)
                    package2 = apk.get_package()
                    #if(package2==package):
                        #print "Packages are equal WHY change???!!!"
                    if(file_name!=""):
                        found = 1
                        if(add_package):
                            channels.add("prefs_"+package+"_"+file_name)
                        else:
                            channels.add("prefs_"+file_name)
    #if found == 0:
        #print "No action intent found in "+name
    return channels

def is_create_package_context_present(method,index):
    while index >= 0:
        ins = method.get_instruction(index)
        #print "1---"+ins.get_output()
        if ("createPackageContext" in ins.get_output()):#0x1A is const-string
            return True
        index = index - 1
    return None

def track_get_shared_preferences_direct(method,index,variable):
    action = ""
    ins = method.get_instruction(index)
    if (ins.get_op_value() in [0x0C]):
        variable = ins.get_output().split(",")[0].strip()
        index = index + 1
    try:
        while index < method.get_length():
            #print str(method.get_length()/2)+"-"+str(index)
            ins = method.get_instruction(index)
            #print ins.get_output().split(",")[1].strip()
            #print ins.get_output().split(",")[0].strip()
            if(variable in ins.get_output() and "getSharedPreferences" in ins.get_output()):
                new_var = ins.get_output().split(",")[1].strip()
                action = acidutils.track_string_value(method,index-1,new_var)
                return action
            elif (variable in ins.get_output().split(",")[1].strip() and ins.get_op_value() in [0x07, 0x08]):
                # Move operation, we just need to track the new variable now.
                variable = ins.get_output().split(",")[0].strip()
            index = index + 1
    except IndexError:
        #Fail gently. beginning of the array reached
        return action
    return action
