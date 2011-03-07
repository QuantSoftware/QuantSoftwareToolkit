'''
Created on Sep 22, 2010

@author: sjoshi42
'''

import tables as pt
import time

h5f = pt.openFile("C:\\generated data files\\timestamp files\\timestamps.h5" , mode = "a")
fileIter=h5f.getNode('/timestamps','timestamps')

for row in fileIter:
    print str(time.strftime("%Y%m%d", time.gmtime(row['timestamp'])))
    
h5f.close()
    
    
    


