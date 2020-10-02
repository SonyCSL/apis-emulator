'''
Created on Aug 3, 2015

@author: annette
'''

oesunits = {}

displayNames={}

# variables for a given moment in time
is_bypassMode = {}
is_ACCharging = {}
acloss = {}
dcloss = {}
wasted={}

inData=None

#sums up all up until now
analyserObject=None

acc = 10 #acceleration rate
#count_h = 0 #time flag: count_h hours have passed from start
count_s = 0 #how many seconds have passed

startTime=None
endTime=None
now=None


sema=False

deals={}
