'''
Created on Jun 1, 2010

@author: Shreyas Joshi
@contact: shreyasj@gatech.edu
@summary: This module is used to generate random alpha values that will then be looked at by the simulator when running. The alpha values have to
          be generated before the simulator starts. 
'''
import tables as pt
import time
import random
#from AlphaDataModel import *

import AlphaDataModel as adm
#Main begins

#alpha val writing begins

adm.openFile("randomAlpha.h5")

#of ("myAlphaFile.h5")

startDate=19840101
endDate=20100101

tsStart= time.mktime(time.strptime(str(startDate),'%Y%m%d'))

tsEnd= time.mktime(time.strptime(str(endDate),'%Y%m%d'))

while (tsStart <= tsEnd):
    adm.addRow("AAPL", "EXCHG", random.random(), tsStart)
    
    tsStart+=86400
    #While ends    

tsStart= time.mktime(time.strptime(str(startDate),'%Y%m%d'))
while (tsStart <= tsEnd):
    adm.addRow("GOOG", "EXCHG", random.random(), tsStart)
    
    tsStart+=86400
    #While ends
tsStart= time.mktime(time.strptime(str(startDate),'%Y%m%d'))
while (tsStart <= tsEnd):
    adm.addRow("MSFT", "EXCHG", random.random(), tsStart)
    
    tsStart+=86400
    #While ends

    
    
tsStart= time.mktime(time.strptime(str(startDate),'%Y%m%d'))
while (tsStart <= tsEnd):
    adm.addRow("YHOO", "EXCHG", random.random(), tsStart)
    
    tsStart+=86400
    #While ends
    
print "Finished adding all data"

#print "Reading it in now..."
#adm.readAllData()
adm.closeFile()
print "All done"
#Main ends
        