__author__ = 'guizos'

from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis

a = apk.APK("examples/TestSet3/Send_WeatherApp_StaticIntent.apk")
print "1"
d = dvm.DalvikVMFormat(a.get_dex())
print "2"
da = analysis.newVMAnalysis(d)
print "3"
intents = da.get_implicit_intents()
print "4"
for i in intents:
    print i.action