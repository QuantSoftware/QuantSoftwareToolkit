'''
Created on Jul 26, 2010

@author: Shreyas Joshi
@contact: shreyasj@gatech.edu
'''

import tables
import DataAccess
import dircache
import numpy
import alphaGenerator.AlphaDataModel as adm

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



#Main begins
noOfDaysToUse=5
daysAhead=5
folderList=list()
folderList.append("C:\\tempoutput\\")
listOfStocks= getStocks(folderList)

beginTS= 473490000 #2 Jan 1985 0500 hrs GMT
endTS=  1262235600 #31 DEc 2009 0500 hrs GMT

print "list of stocks is: " + str(listOfStocks)
dataAccess= DataAccess.DataAccess(True, folderList, "/StrategyData", "StrategyData", True, listOfStocks, beginTS, endTS)
timestamps= list(dataAccess.getTimestampArray())

print "Printing all timestamps: "
for ts in timestamps:
    print ts
print "Printing ts done"


#alpha= alphaGenerator.AlphaDataModel.AlphaDataModelClass()
adm.openFile("curveFittingAlphaVals_Jan_85_to_2010.h5")
daysArray= numpy.zeros ((noOfDaysToUse+1), dtype=float)

ctr=0
while (ctr<= noOfDaysToUse): #because we get back noOfDaysToUse+1 rows
    daysArray[ctr]= ctr
    ctr+=1
    #while ends
    
try:
  beginIndex= timestamps.index(beginTS)
  endIndex= timestamps.index(endTS) 
except ValueError:
    print "beginTS or endTS not found!"
    raise ValueError


#beginTS+= (noOfDaysToUse*day)
beginIndex+=noOfDaysToUse


while (beginIndex<=endIndex):
    #closeData= dataAccess.getMatrixFromTS(listOfStocks, 'adj_close', beginTS, -noOfDaysToUse)
    closeData= dataAccess.getMatrixBetweenIndex(listOfStocks, 'adj_close', beginIndex- noOfDaysToUse, beginIndex)
    print "At ts: " + str (timestamps[beginIndex])
    
    if (closeData is not None):
        print "closeData is not none"
        stockCtr=0
        while (stockCtr < len (listOfStocks)):
            nanPresent=False
            closeData= numpy.ma.masked_values(closeData, numpy.NaN)
#            ctr=0
#            while (ctr<= noOfDaysToUse):
#              try:  
#                if (numpy.isnan(closeData[ctr][stockCtr])):
#                    nanPresent=True
#                    zeroDueToNaNCtr+=1
#                    adm.addRow(listOfStocks[stockCtr], "blah", 0.0, beginTS)
#                    break
#                ctr+=1
#              
#              
#              except IndexError:
#                    print "stockCtr: " + str(stockCtr)+", ctr: "+str(ctr)
#                    print "Shape is: "+str(closeData.shape)
                
                
                
                #while (ctr<= noOfDaysToUse) ends
            if (nanPresent is False):
                #calculate the best fit 3 degree polynomial
                #print "daysArray: "+str(daysArray.shape) +" closeData: " + str(blah.shape) + "the actual arr: " + str (closeData[:][stockCtr])
                polynomial= numpy.polyfit (daysArray, closeData[:, stockCtr], 3)
                predictedClosingValue= numpy.polyval(polynomial, noOfDaysToUse + daysAhead -1)
                #if (predictedClosingValue <0):
                    #print "predicted closing value negative! But that can't be!"
                    #predictedClosingValue=0
                #print "val: " + str(predictedClosingValue) + ", closingVal: "+ str(closeData[noOfDaysToUse][stockCtr])+", stock: " +str(listOfStocks[stockCtr]+ " ts: "+ str(timestamps[beginIndex]))
                #print "val: " + str(predictedClosingValue) +", stock: " +str(listOfStocks[stockCtr]+ " ts: "+ str(timestamps[beginIndex]))
                
                valueToBeAdded= (predictedClosingValue- closeData[noOfDaysToUse][stockCtr])/ closeData[noOfDaysToUse][stockCtr]
                adm.addRow(listOfStocks[stockCtr], "blah",valueToBeAdded , timestamps[beginIndex])
                #if ends
            
            stockCtr+=1
            #while ends
    else:
        #closeData is None
        print "closeData is None"
#        for stock in listOfStocks:
#            adm.addRow(stock, "blah", 0.0, beginTS)
#            zeroDueToNoneCtr+=1
    
    beginIndex+=1
    #while ends

adm.closeFile()