'''
Created on Jun 1, 2010

@author: Shreyas Joshi
@summary: Just a quick way to test the DataAccess class... nothing more "I dare do all that may become a DataAccessTester. Who dares do more is none"
'''

#Due to the momentary lack of a HDF viewer that installs/works without hassle- I decided to write a little something to check if the alpha 
#values were being written properly

#Main begins
#from DataAccess import *
import DataAccess as da
import tables as pt
import numpy as np
from itertools import izip 
import time
import dircache

def getStocks(listOfPaths):
        
            listOfStocks=list()
            #Path does not exist
            print "Reading in all stock names..."
            fileExtensionToRemove=".h5"   
            
            for path in listOfPaths:
               stocksAtThisPath=list ()
               
               stocksAtThisPath= dircache.listdir(str(path))
               #Next, throw away everything that is not a .h5 And these are our stocks!
               stocksAtThisPath = filter (lambda x:(str(x).find(str(fileExtensionToRemove)) > -1), stocksAtThisPath)
               #Now, we remove the .h5 to get the name of the stock
               stocksAtThisPath = map(lambda x:(x.partition(str(fileExtensionToRemove))[0]),stocksAtThisPath)
               
               for stock in stocksAtThisPath:
                   listOfStocks.append(stock)
               return listOfStocks
    #readStocksFromFile done






print "Starting..."
dataItemsList=[]

dataItemsList.append('alphaValue')

listOfPaths=list()
listOfPaths.append("C:\\temp\\temp\\")#listOfPaths.append("C:\\tempoutput\\")
#listOfPaths.append("C:\\fin\\tempoutput\\tempoutput2\\")


#"C:\\fin\\tempoutput\\" is the path to where all the hdf files are. This has to be chaanged accordingly

listOfStocks= getStocks(listOfPaths)
alpha= da.DataAccess (True, listOfPaths, "/StrategyData", "StrategyData", True, listOfStocks )

tslist= list(alpha.getTimestampArray())

for ts in tslist:
    for stock in listOfStocks:
        print str(stock)+"  "+ str(ts)+"   "+str(alpha.getStockDataItem(str(stock), 'volume', ts)) 




#alpha= da.DataAccess (False, "curveFittingAlphaVals.h5", "/alphaData", "alphaData", True, listOfStocks, None, None, None, dataItemsList)


listOfTS= alpha.getTimestampArray()
for stock in listOfStocks:
            alphaList= alpha.getStockDataList(stock, 'volume')
            ctr=0
            for val in alphaList:
                print "stock: " + str(stock) + ", val: "+str(val) + ", ts: " + str(listOfTS[ctr])
                ctr+=1
                
print "DONE!"                
            
            
            
            
            
            
            
            

