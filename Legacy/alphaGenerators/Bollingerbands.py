'''
Created on Jul 30, 2010

@author: sjoshi42
@summary: This module generates alpha values based on bollinger bands
'''

import DataAccess
import dircache
import numpy
import alphaDataModel.AlphaDataModel as adm
#import alphaGenerator.AlphaDataModel as adm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

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



def removeNaNs(numArray):
    ctr=1
    #fill forward
    while (ctr< numArray.size):
        if (numpy.isnan(numArray[ctr])):
            if not (numpy.isnan(numArray[ctr-1])):
                numArray[ctr]= numArray[ctr-1]
                #if not ends
            #if ends
        ctr+=1
        #while ends        
    
    #fill back
    ctr= numArray.size-2
    while (ctr>=0):
        if (numpy.isnan(numArray[ctr])):
            if not (numpy.isnan(numArray[ctr+1])):
                numArray[ctr]= numArray[ctr+1]
                #if not ends
            #if ends
        ctr-=1
        #while ends        
    return numArray
#removeNaNs ends


def main():
    '''
    @summary: Calculates Bollinger bands
    '''
    
    folderList= list()
    folderList.append("C:\\tempoutput\\")
    listOfStocks= list()
#    listOfStocks.append("ACY")
    listOfStocks.append("AAPL")
    #listOfStocks= getStocks(folderList)
    
    
    
    dataAccess= DataAccess.DataAccess (True, folderList, "/StrategyData", "StrategyData", True, listOfStocks)
    timestamps= list(dataAccess.getTimestampArray())
    adm.openFile("AAPLonlybollingerBandsAlphaVals.h5")
    
    period= 10
    stdMultiplier=2
    noOfDays= len (timestamps) #400
    
    
    centerband= numpy.zeros(noOfDays, dtype= float) #len(timestamps)- period + 1 #Just to make it the same length as the adj_close to make it easier to plot
    upperBand= numpy.zeros(noOfDays, dtype= float)
    lowerBand= numpy.zeros(noOfDays, dtype= float)
    x= numpy.zeros(noOfDays, dtype= float)
    
    ctr=0
    while (ctr< noOfDays):
        x[ctr]=ctr
        ctr+=1
        #end while
        
    
    for stock in listOfStocks:
        print "Processing: " + str(stock)
        #adj_close= dataAccess.getStockDataList(str(stock), 'adj_close')
        adj_close= dataAccess.getStockDataList(stock, 'adj_close', timestamps[0], timestamps[noOfDays-1])
        
        adj_close= removeNaNs(adj_close)#nan's removed, unless all are nans
        
        #Now calculating bollinger bands
        for ctr in range (period, noOfDays):
            
            try:
               centerband[ctr]= numpy.average(adj_close[ctr- period:ctr])
               stdDev= numpy.std(adj_close[ctr- period:ctr])
               upperBand[ctr]= centerband[ctr] + (stdMultiplier* stdDev)
               lowerBand[ctr]= centerband[ctr] - (stdMultiplier* stdDev)
            except IndexError:
                print "ctr is: " + str(ctr)
        
        #writing alpha values to file
        for ctr in range (0, noOfDays):
            if (upperBand[ctr]== lowerBand[ctr])or (adj_close[ctr]== centerband[ctr]):
                adm.addRow(str(stock), "blah", 0.0, timestamps[ctr])
            elif (adj_close[ctr] < centerband[ctr]):
                alphaValue=  lowerBand[ctr]/ adj_close[ctr]
                adm.addRow (str(stock), "blah", alphaValue, timestamps[ctr])
            else:
                alphaValue= - adj_close[ctr]/ upperBand[ctr]
                adm.addRow (str(stock), "blah", alphaValue, timestamps[ctr])
            #done writing alpha values of this stock to file
            
                   
                       
            
            #calculating bollinger bands done!
            
#        fig = Figure()
#        canvas = FigureCanvas(fig)
#        ax = fig.add_subplot(111)
#        ax.plot(centerband)
#        ax.plot (lowerBand)
#        ax.plot (upperBand)
#        ax.plot (adj_close)
#
#        ax.set_title(str(stock)+' Bollinger bands')
#        ax.grid(True)
#        ax.set_xlabel('time')
#        ax.set_ylabel('')
#        canvas.print_figure(str(listOfStocks.index(stock)))
        #for stock in listOfStocks: done
        
    adm.closeFile()
        

#Main done        
            
        
if __name__ == '__main__':
    main()