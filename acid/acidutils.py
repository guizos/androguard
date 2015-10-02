import os
import fnmatch

def get_all_apk_in_dir(folder,extension):
    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for filename in fnmatch.filter(filenames, '*'+extension):
            matches.append(os.path.join(root, filename))
    return matches

# Tracks back the value of a string variable that has been declared in code
# If the value comes from a literal string, it returns it.
# If the valua cannot be traced back to a literal string, it returns the chain
# of method calls that resulted in that string until initialization of the object

def track_string_value(method,index,variable):
    action = "NotTracedBackPossibleParameter"
    while index >= 0:
        ins = method.get_instruction(index)
        #print "1---"+ins.get_output()
        if (variable in ins.get_output() and ins.get_op_value() in [0x1A]):#0x1A is const-string
            action = ins.get_output().split(",")[1].strip()
            return action[1:-1]
        elif (variable in ins.get_output() and ins.get_op_value() in [12] ):#12 is move-result-object
            ins2 = method.get_instruction(index-1)
            #print "2---"+ins2.get_name()+" "+ins.get_output()
            if(len(ins2.get_output().split(","))==2):
                action = ins2.get_output().split(",")[1] + action
            elif len(ins2.get_output().split(","))==3 and variable == ins2.get_output().split(",")[0]:
                action = ins2.get_output().split(",")[2] + action
        elif variable in ins.get_output() and ins.get_name()=="new-instance":
            # The register might being reused in another variable after this instruction
            # Stop here
            index = -1
            action = ins.get_output().split(",")[1] + action
        elif (variable in ins.get_output().split(",")[0].strip() and ins.get_op_value() in [0x07, 0x08]):
            # Move operation, we just need to track the new variable now.
            variable = ins.get_output().split(",")[1].strip()
        elif (variable in ins.get_output().split(",")[0].strip() and ins.get_op_value() in [0x54]):#taking value from a method call.
            action = "got it from method call:"+ins.get_output().split(",")[2].strip()
            instance_name = ins.get_output().split(",")[2].strip()
            action = look_for_put_of_string_instance(method,instance_name)
            index = -1
        index = index - 1
    return action

def look_for_put_of_string_instance(method, instance_name):
    for m in method.CM.vm.get_methods():
        for index,i in enumerate(m.get_instructions()):
            if( i.get_op_value() in [0x5B] and instance_name in i.get_output()):#iput
                 string_var = i.get_output().split(",")[0].strip()
                 return track_string_value(m,index,string_var)
    return instance_name
