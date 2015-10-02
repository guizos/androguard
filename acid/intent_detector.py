import sys
import acidutils
PATH_INSTALL = "./"
from sets import Set
sys.path.append(PATH_INSTALL)
from androguard.core.bytecodes import dvm
from androguard.core.bytecodes import apk
from androguard.core.androconf import CONF
from androguard.core.analysis import analysis, ganalysis


# Only detects those broadcast intents that are directly defined by constant string
# in the same method.

def trans_broadcast_intents(name,dalvik):
    #print "*********"+name+"*********"
    channels = Set()
    found = 0
    for m in dalvik.get_methods():
        for index,i in enumerate(m.get_instructions()):
            if (i.get_op_value()==110) and ("Landroid/support" not in m.get_class_name()):#invoke-virtual
                if "Landroid/content/Intent;->setAction" in i.get_output():
                    intent = i.get_output().split(",")[1].strip()
                    back_index = index
                    while back_index > 0:
                        back_index = back_index - 1
                        i2 = m.get_instruction(back_index)
                        if (intent in i2.get_output() and i2.get_op_value() in [12] ):#12 is move-result-object
                            action = track_method_call_action(m,back_index,intent)
                            #print "---- Class: "+m.get_class_name()+"-----"
                            #print "---- Method: "+m.get_name()+"-----"
                            channels.add("i_"+action)
                            #print "trans("+name+","+action+")."
                            back_index = -1
                            found = 1
                        if (i2.get_op_value()==26 and intent in i2.get_output()):#const-string
                            action = i2.get_output().split(",")[1].strip()
                            #print "---- Class: "+m.get_class_name()+"-----"
                            #print "---- Method: "+m.get_name()+"-----"
                            channels.add("i_"+action[1:-1])
                            #print "trans("+name+","+action[1:-1]+")."
                            back_index = -1
                            found = 1
    if found == 0:
        #print "No action intent found in "+name
        pass
    return channels


def track_method_call_action(method, index, intent_variable):
    action = ""
    while index > 0:
        ins = method.get_instruction(index)
        #print "1---"+ins.get_name()+" "+ins.get_output()
        if (intent_variable in ins.get_output() and ins.get_op_value() in [12] ):#12 is move-result-object
            ins2 = method.get_instruction(index-1)
            #print "2---"+ins2.get_name()+" "+ins.get_output()
            if(len(ins2.get_output().split(","))==2):
                action = ins2.get_output().split(",")[1] + action
            elif len(ins2.get_output().split(","))==3 and intent_variable == ins2.get_output().split(",")[0]:
                action = ins2.get_output().split(",")[2] + action
        elif intent_variable in ins.get_output() and ins.get_name()=="new-instance":
            index = 0
            action = ins.get_output().split(",")[1] + action
        index = index - 1
    return action

def recv_static_receiver_intents(name,apk_object):
    channels = Set()
    manifest = apk_object.get_AndroidManifest()
    receiver_list = manifest.getElementsByTagName('receiver')
    for receiver in receiver_list:
        action_list = receiver.getElementsByTagName('action')
        for action in action_list:
            values = action.attributes.values()
            for val in values:
                if 'name' in val.name:
                    channels.add("i_"+val.value)
    return channels

def recv_dynamic_receiver_intents(name,dalvik):
    channels = Set()
    found = 0
    for m in dalvik.get_methods():
        for index,i in enumerate(m.get_instructions()):
            if (i.get_op_value()==0x22) and ("Landroid/support" not in m.get_class_name()):
                #print i.get_output()
                if "Landroid/content/IntentFilter" in i.get_output(): #we look for the registerReceiver method
                    var = i.get_output().split(",")[0].strip() #The second argument holds the IntentFilter with the action
                    action = track_intent_filter_direct(m,index+1,var)
                    found = 1
                    #print "---In "+m.get_name()
                    channels.add("i_"+action)

    if found == 0:
        #print "No action intent found in "+name
        pass
        #print ""
    return channels

# method is the method where we are searching
# index is the next instruction after the declaration of the IntentFilter has been found
# var is the register name where the IntentFilter is placed

def track_intent_filter_direct(method,index,variable):
    action = "notDefinedInMethod"
    try:
        while index < method.get_length():
            ins = method.get_instruction(index)
            #print ins.get_output().split(",")[1].strip()
            #print ins.get_output().split(",")[0].strip()
            if(variable in ins.get_output() and "Landroid/content/IntentFilter;-><init>(Ljava/lang/String;" in ins.get_output()):
                new_var = ins.get_output().split(",")[1].strip()
                action = acidutils.track_string_value(method,index-1,new_var)
                return action
            elif (variable in ins.get_output().split(",")[1].strip() and ins.get_op_value() in [0x07, 0x08]):
                # Move operation, we just need to track the new variable now.
                new_var = ins.get_output().split(",")[0].strip()
                #print "++++"+new_var
                action2 = track_intent_filter_direct(method,index+1,new_var)
                if(action2 not in ["notDefinedInMethod", "registerReceiver"]):# it may happen that the same variable is referenced in two register. One leads to nowehere and the other is the correct one.
                    action = action2
                    return action
            elif (variable in ins.get_output().split(",")[0].strip() and "Landroid/content/IntentFilter;-><init>(Landroid/content/IntentFilter;" in ins.get_output()):
                # The intent filter is initialized with other intent filter.
                # We update the register name to look for.
                #TODO THIS GENERATES FALSE POSITIVES
                new_var = ins.get_output().split(",")[1].strip()
                action2 = track_intent_filter_direct(method,index+1,new_var)
                if(action2 not in ["notDefinedInMethod", "registerReceiver"]):# it may happen that the same variable is referenced in two register. One leads to nowehere and the other is the correct one.
                    action = action2
                    return action
            elif (variable in ins.get_output() and "addAction" in ins.get_output()):
                # There is an addAction that declares the action
                # We need to look for its value
                new_var = ins.get_output().split(",")[1].strip()
                if "p" in new_var:# the varaible comes from a method parameter
                    action = "MethodParameter"
                    return action
                else:
                    action = acidutils.track_string_value(method,index-1,new_var)
                    return action
            elif (variable in ins.get_output().split(",")[0].strip() and ins.get_op_value() in [0x54]):#taking value from a method call.
                action = "got it from method call:"+ins.get_output().split(",")[2].strip()
                return action
            elif "registerReceiver" in ins.get_output():
                action = "registerReceiverFoundWithouBeingAbleToTrackParameters"
                return action
            index = index + 1
    except IndexError:
        #Fail gently. beginning of the array reached
        return action
    return action







def recv_dynamic_intents2(name,dalvik):
    #print "*********"+name+"*********"
    found = 0
    for m in dalvik.get_methods():
        for index,i in enumerate(m.get_instructions()):
            if (i.get_op_value()==110) and ("Landroid/support" not in m.get_class_name()):#invoke-virtual
                #print i.get_output()
                if "->registerReceiver" in i.get_output(): #we look for the registerReceiver method
                    var = i.get_output().split(",")[2].strip() #The second argument holds the IntentFilter with the action
                    action = track_intent_filter_action(m,index-1,var)
                    found = 1
                    #print "---In "+m.get_class_name()
                    print "recv("+name+","+action+")"
    if found == 0:
        pass
        #print "No action intent found in "+name
    return 'Finished'


def track_intent_filter_action(method,index,variable):
    action = "notDefinedInMethod"
    while index > 0:
        ins = method.get_instruction(index)
        #print ins.get_output()
        if(variable in ins.get_output() and "Landroid/content/IntentFilter;-><init>(Ljava/lang/String;" in ins.get_output()):
            # It is the initialization method of the Intent filter
            # (with String as 1st param) we need to look back for its value.
            new_var = ins.get_output().split(",")[1].strip()
            action = track_string_value(method,index-1,new_var)
            index = 0
        elif (variable in ins.get_output().split(",")[0].strip() and ins.get_op_value() in [0x07, 0x08]):
            # Move operation, we just need to track the new variable now.
            new_var = ins.get_output().split(",")[1].strip()
            action = track_intent_filter_action(method,index-1,new_var)
            if(action not in ["notDefinedInMethod", "registerReceiver"]):# it may happen that the same variable is referenced in two register. One leads to nowehere and the other is the correct one.
                return action
        elif (variable in ins.get_output().split(",")[0].strip() and "Landroid/content/IntentFilter;-><init>(Landroid/content/IntentFilter;" in ins.get_output()):
            # The intent filter is initialized with other intent filter.
            # We update the register name to look for.
            variable = ins.get_output().split(",")[1].strip()
        elif (variable in ins.get_output() and "addAction" in ins.get_output()):
            # There is an addAction that declares the action
            # We need to look for its value
            new_var = ins.get_output().split(",")[1].strip()
            if "p" in new_var:# the varaible comes from a method parameter
                action = "MethodParameter"
                index = 0
            else:
                action = track_string_value(method,index-1,new_var)
                index = 0
        elif (variable in ins.get_output().split(",")[0].strip() and ins.get_op_value() in [0x54]):#taking value from a method call.
            action = "got it from method call:"+ins.get_output().split(",")[2].strip()
            index = 0
        elif "registerReceiver" in ins.get_output():
            action = "registerReceiverFound"
            index = 0
        index = index - 1
    return action

 # for i in m.basic_blocks.get():
    #print "\t %s %x %x" % (i.name, i.start, i.end), i.get_instructions()[-1].get_name()
#    for ins in i.get_instructions():
#        if(ins.get_name()=="invoke-virtual"):
#            print "match!"
#            print ins.get_raw()
#print "***********************"
