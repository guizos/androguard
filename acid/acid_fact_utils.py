#!/usr/bin/env python
from sys import argv
from scipy import stats
from collections import Counter
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import re
#

def read_intent_file(name):
    txt = open(name)
    p = re.compile('trans\(\'([a-z\.]*)\',\'i\_([\w|\/|_|;|\-|.|>|\)|\(|\s]*)\'', re.MULTILINE)
    matches = p.findall(txt.read())
    return matches

def intents_per_app(matches):
    apps = {}
    for match in matches:
        if(match[0] in apps):
            apps[match[0]].add(match[1])
        else:
            apps[match[0]]=set()
            apps[match[0]].add(match[1])
    return apps

def count_most_frequent_intents_per_app(apps,n):
    intents = []
    for key in apps:
        intents.extend(list(apps[key]))
    return Counter(intents).most_common(n)



# Example data
#people = ('Tom', 'Dick', 'Harry', 'Slim', 'Jim')

#performance = 3 + 10 * np.random.rand(len(people))
#error = np.random.rand(len(people))

#plt.barh(y_pos, performance, xerr=error, align='center', alpha=0.4)
#plt.yticks(y_pos, people)
#plt.xlabel('Performance')
#plt.title('How fast do you want to go today?')

#plt.show()

matches = read_intent_file(argv[1])
apps =  intents_per_app(matches)
print len(apps)
result = count_most_frequent_intents_per_app(apps,50)
intents, counts = zip(*result)
pos = range(0,len(counts),1)
print(intents)
plt.bar(pos, counts, alpha=0.4)
plt.show()
