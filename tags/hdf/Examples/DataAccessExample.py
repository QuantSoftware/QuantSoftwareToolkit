'''
Created on Jun 1, 2010

@author: Shreyas Joshi
@summary: An example to show how dataAccess works.
'''

import sys
sys.path.append(str(sys.path[0])+str("/../qstkutil/"))

for i in range (0, len(sys.path)):
    print sys.path[i]

#from DataAccess import *
import DataAccess as da
import tables as pt
import numpy as np
from itertools import izip 
import time
import dircache

def getStocks(listOfPaths):
    '''
    @param listofPaths: A list of strings. Each string is a path to a folder containing stock data.
    @summary: This function gets the names of all the HDF files at the provided paths.
    '''
        
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





#for gekko
#listOfPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_NASDAQ/")
#listOfPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/Delisted_US_Recent/")
#listOfPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/OTC/")
#listOfPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_AMEX/")
#listOfPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_Delisted/")
#listOfPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_NYSE/")
#listOfPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_NYSE Arca/")
#gekko paths end



listOfStocks= list()
listOfStocks.append("AAPL")
listOfStocks.append("AMZN")

listOfPaths=list()
listOfPaths.append("C:\\test\\temp\\")

data_access= da.DataAccess (True, listOfPaths, "/StrategyData", "StrategyData", True, listOfStocks) # , 946702800 , 1262322000 

#alpha= da.DataAccess (False, "C:\\test\\temp\\AAPL.h5", "/StrategyData", "StrategyData", True, None) # reading a single hdf5 file

tslist= list(data_access.getTimestampArray()) #get all the timestamps
list_of_stocks= data_access.getListOfSymbols();

print 'The stocks are: '+ str (list_of_stocks)    
print 'These data items are stored per stock per timestamp '+ str(data_access.getListOfDynamicData())
print "These data items are stored only one per stock because they do not change with time  "+str(data_access.getListOfStaticData())                
print "DONE!"                
            
            
            
            
            
            
            
            

