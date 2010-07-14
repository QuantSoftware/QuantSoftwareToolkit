'''
Created on Jun 14, 2010

@author: Shreyas Joshi
@contact: shreyasj@gatech.edu
'''

import numpy as np
import tables as pt
import time
class Stock:
    
    def __init__(self, noOfStaticDataItems, symbol): #, stockIndex
       '''
       @attention: Here it is assumed that all the stocks will have the same static data. So, we don't need to store the names of the data
                  items separately for every stock. Only the values need to be stored on a per stock basis.
                  
        @param noOfStaticDataItems:  the number of items that will be be stored only once per stock
        @param symbol: the symbol of the current stock          
       '''
       self.dataVals=[]
#       self.stockIndex= stockIndex
       self.symbol=symbol

       while (len(self.dataVals) < noOfStaticDataItems):
           self.dataVals.append("No Data")
    #__init__ done       
       
    #according to http://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html
    #this is compatible with python float
    
    def addStaticDataVal(self, value, valIndex):
        self.dataVals[valIndex]= value
    #addStaticDataVal done
    
    def getStaticDataVal(self, valIndex):
        return self.dataVals[valIndex]
    #getStaticDataVal
    
#    def getStockIndex(self):
#        return self.stockIndex
    #getIndex done
        
    def setSymbol(self, symbolName):
        self.symbol= symbolName
    #setSymbol ends
    
    def getSymbol(self):
        return self.symbol
    #getSymbol ends        
        
#class Stock ends    


class DataAccess:
    
    '''
    @summary: This class will be used to access the data for all stocks.
    
    '''
    
    def __init__(self, isFolderName, folderName, groupName, nodeName, noisy, listOfStocks, staticDataItemsList=None, dataItemsList=None, SYMBOL='symbol', TIMESTAMP='timestamp'):
        '''
        @param isFolderName: Indicates if folderName is a folder name or a file name. True if is folder. False if is file.
        @param folderName: name of folder/ file 
        @param noisy: noisy or not True/False
        @param listOfStocks: specifies which list of stocks to read in from the hdf5 file.  
        @param staticDataItemsList: The list of items that need to be stored only once per stock. Like symbol, exchange etc
        @param dataItemsList: List of items that need to be stored once per timestamp per stock
        @summary: When reading in stock data- each stock has its own hdf5 file. All the files are stored in a folder (which should be given
        to this function as the folderName argument.) The files relevant to the stocks in the listOfStocks are opened- the data is read in and
        the file is then closed. All data is assumed to fit into memory. (2GB mem = ~1000 stocks)
        
        @bug: For some reason windows did not allow creation of a file called PRN.csv. Norgate renames it to PRN_.csv making the file name different from
        the symbol name. Currently the CSV to HDF5 converter will create a PRN_.h5 file. DataAccess API has not been tested for this yet. My guess is that everything
        should be OK if the listOfStocks has PRN_ as the name and later the actual symbol (PRN only w/o the underscore) is used.
        A quick ls | grep *_* shows that this is the only stock with an '_'- so I guess the only stock with the problem.
        '''
    
        
        self.SYMBOL= SYMBOL
        self.TIMESTAMP= TIMESTAMP
        
        
        if (staticDataItemsList is None):
            staticDataItemsList= list()
            staticDataItemsList.append(self.SYMBOL)
            staticDataItemsList.append('exchange')
        
        #Making sure dataItemsList has symbols and timestamps. Is this necessary?
        if (dataItemsList is None):
        
         dataItemsList= list()
         dataItemsList.append('volume')
         dataItemsList.append('adj_open')    
         dataItemsList.append('adj_close')
         dataItemsList.append('adj_high')
         dataItemsList.append('adj_low')
         dataItemsList.append('close')
#         dataItemsList.append('ogre')
         
         
        self.noisy= noisy 
        self.dataItemsList= dataItemsList
        self.staticDataItemsList= staticDataItemsList
        self.stocksList=[]
        self.timestamps= np.array([])
        self.nanArray= np.zeros((1, len(self.dataItemsList)), dtype=float) #Possible bug
        self.allStocksData= np.zeros((len(dataItemsList), 1, 1), dtype=float) # dataItems, timestamps, stocks
        self.allStocksData[:][:][:]=np.NaN #Set all elements to NaN
        self.allTimestampsAdded= False
        
        print "Starting to read in file..." + str(time.strftime("%H:%M:%S"))
        
        
        
#        for stockName in listOfStocks:
#          
##          try:
#          h5f = pt.openFile(str(folderName)+ str(stockName)+".h5", mode = "r") # if mode ='w' is used here then the file gets overwritten!
#          print h5f
#        #end for  
        
        if (isFolderName is True):
         for stockName in listOfStocks:
          
          try:
             h5f = pt.openFile(str(folderName)+ str(stockName)+".h5", mode = "a") # if mode ='w' is used here then the file gets overwritten!
#             fileIterator= h5f.root.StrategyData.StrategyData
             fileIterator= h5f.getNode(groupName, nodeName)
          except:
             print str(stockName)+" not found."
             continue #skipping the rest
          
          
          for row in fileIterator.iterrows():
            
#            print "Adding row for stock: " + str(stockName)
            stockFound=False
            if (len(self.stocksList) > 0):
              if (self.stocksList[len(self.stocksList) -1].getSymbol()== row[self.SYMBOL]):
                stockFound= True
            #inner if done
           #if (len(self.stocksList) > 0) done 
          
            if (stockFound is False): #Should happen only once for every stock
               #this is the first time we are seeing this stock...
#               print "Stocknotfound begins " + str(time.time())
               
               if (self.noisy is True):
                   print "Adding stock " + str(row[self.SYMBOL])+ ". Current no. of stocks: " + str(len(self.stocksList))+"  "+str(time.strftime("%H:%M:%S"))
               #if self.noisy ends    
               
               tempStock= Stock(len(self.staticDataItemsList), row[self.SYMBOL]) #...so we create a new stock object
               
               #...and store its static data in the stock object
               for staticData in self.staticDataItemsList:
                   try:
                       tempStock.addStaticDataVal(row[str(staticData)], self.staticDataItemsList.index(str(staticData)))
                   except:
                       print "Static value " + str(staticData) + " not available for stock " + str(row[self.SYMBOL])
               #Done adding all the static data to the stock object
               
               #...and add this stock to the stock list
               self.stocksList.append(tempStock)
               
               #Change the shape of the allStocksData and add this stock to it. 
               #We don't need to do this if this is the first stock we are adding...
               
               #HIGHLY LIKELY THAT THERE IS A BUG HERE
               if (len(self.stocksList) > 1):
                  tempArray= np.zeros((len(dataItemsList), len(self.timestamps), 1), dtype=float)
                  tempArray[:][:][:]= np.NaN
#                  print "temp: " + str (tempArray.shape)
#                  print "allStocksData: " + str (self.allStocksData.shape)
                  
                  self.allStocksData= np.append (self.allStocksData, tempArray, axis=2)
               #if (len(self.stocksList) > 1) ends
           #if stockFound is False ends
           
            tsIndex= self.appendToTimestampsAndGetIndex(row[self.TIMESTAMP]) # will be ZERO for first timestamp
            self.insertIntoArrayFromRow(tsIndex, self.allStocksData.shape[2]-1, row)
          #for row in fileIter ends
          h5f.close()
         #for stockName in listOfStocks: ends
        #if (isFolderName is True) ends
        else:
            #if (isFolderName is True) is False
            h5f = pt.openFile(str(folderName), mode = "a")
            fileIterator= h5f.getNode(groupName, nodeName)
#            fileIterator= h5f.root.alphaData.alphaData
            for row in fileIterator.iterrows():
             
#            print "Adding row for stock: " + str(stockName)
             stockFound=False
             if (len(self.stocksList) > 0):
               if (self.stocksList[len(self.stocksList) -1].getSymbol()== row[self.SYMBOL]):
                 stockFound= True
             #inner if done
            #if (len(self.stocksList) > 0) done 
          
             if (stockFound is False): #Should happen only once for every stock
               #this is the first time we are seeing this stock...
#               print "Stocknotfound begins " + str(time.time())
               
               if (self.noisy is True):
                   print "Adding stock " + str(row[self.SYMBOL])+ ". Current no. of stocks: " + str(len(self.stocksList))+"  "+str(time.strftime("%H:%M:%S"))
               #if self.noisy ends    
               
               tempStock= Stock(len(self.staticDataItemsList), row[self.SYMBOL]) #...so we create a new stock object
               
               #...and store its static data in the stock object
               for staticData in self.staticDataItemsList:
                   try:
                       tempStock.addStaticDataVal(row[str(staticData)], self.staticDataItemsList.index(str(staticData)))
                   except:
                       print "Static value " + str(staticData) + " not available for stock " + str(row[self.SYMBOL])
               #Done adding all the static data to the stock object
               
               #...and add this stock to the stock list
               self.stocksList.append(tempStock)
               
               #Change the shape of the allStocksData and add this stock to it. 
               #We don't need to do this if this is the first stock we are adding...
               
               #HIGHLY LIKELY THAT THERE IS A BUG HERE
               if (len(self.stocksList) > 1):
                  tempArray= np.zeros((len(dataItemsList), len(self.timestamps), 1), dtype=float)
                  tempArray[:][:][:]= np.NaN
#                  print "temp: " + str (tempArray.shape)
#                  print "allStocksData: " + str (self.allStocksData.shape)
                  
                  self.allStocksData= np.append (self.allStocksData, tempArray, axis=2)
               #if (len(self.stocksList) > 1) ends
             #if stockFound is False ends
           
             tsIndex= self.appendToTimestampsAndGetIndex(row[self.TIMESTAMP]) # will be ZERO for first timestamp
             self.insertIntoArrayFromRow(tsIndex, self.allStocksData.shape[2]-1, row)
            #for row in fileIter ends
            h5f.close()
         #for stockName in listOfStocks: ends  
          
        #checking out what is NaN
#        print self.allStocksData
        
        
#        print "Looking for NaNs"
#        for i in range (0, self.allStocksData.shape[0]):
#            for j in range (0, self.allStocksData.shape[1]):
#                for k in range (0, self.allStocksData.shape[2]):
#                       print str (i)+ "  " + str(j)+"  "+str(k)+":  "+ str(self.allStocksData[i][j][k])
#                    
#
##                    if (self.allStocksData[i][j][k] == np.NaN):
##                        print self.dataItemsList[i]+ " for "+ self.stocksList[k].getSymbol()+ " is NaN at: "+ self.timestamps[j]
#                        
#        print "Looking for NaNs done"
    print "Finished reading all data." + str(time.strftime("%H:%M:%S"))
    # constructor ends
    
    def getStaticData(self, stockName, staticDataItem):
        '''
        @summary: Provides access to those properties of a stock that do not change with time
        @param stockName: The name of the stock- of which the properties are needed.
        @param staticDataItem: The name of the property whose value is needed
        '''
        #Check if have this item at all
        try:
           valIndex= self.staticDataItemsList.index(str(staticDataItem))
        except:
            raise ValueError #staticDataItem not present
#        stockIndex=0
#        stockFound=False
        for stock in self.stocksList:
            if (stock.getSymbol()== stockName):
                #Found the stock
#                stockFound = True
                return stock.getStaticDataVal(valIndex)  
#            stockIndex+=1
        #for ends
        
        #if control ever comes here it will be only because the stock name was not found. So,
        raise ValueError
    #getStaticData ends
                       
    
    def getStockDataList (self, stockName, dataItem, beginTS=None, endTS=None):
        '''
        @summary: Returns a list of values of a specified time dependent property for a specified stock and for the specified time period
        @param stockName: name of the stock 
        @param dataItem: the name of the property whose value is needed
        @param beginTS: specifies the beginning of the time period. If not specified, considers all data from the beginning.
        @param endTS:  specifies the ending of the time period. If not specified, considers all data upto the end.
        @return: Returns a 1D numpy array of floats with the requested values. begin and endTS values are included.
        '''
        
#        print "in getStockDataList"
        
        #Checking if we have dataItem at all
        try:
            valIndex= self.dataItemsList.index(str(dataItem))
        except:
            raise ValueError #dataItem is not present.
        
        
        #Checking is beginTS < endTS if both are present...
        if ((beginTS is not None) and (endTS is not None)):
            if (beginTS> endTS):
              raise ValueError #End timestamp must be greater than begin timestamp
        
        #deal with stock not found, timestamps not found
        if (beginTS is None):
            beginTS=0
#        else:
#            tsFound=False
#            for i in range (0, self.timestamps.size):
#                if (beginTS == self.timestamps[i]):
#                    beginIndex=i
#                    tsFound=True
#                    break
#            #for ends
#            if (tsFound is False):
#                raise ValueError #Begin timestamp not found. 
            
            
        if (endTS is None):
            endTS= self.timestamps[self.timestamps.size -1] #because we need to iterate till <=
#        else:
#            tsFound=False
#            for i in range (0, self.timestamps.size):
#                if (endTS == self.timestamps[i]):
#                    endIndex=i
#                    tsFound=True
#                    break
#            #for ends        
#            if (tsFound is False):
#                raise ValueError #End timestamp not found
            
            
        #Now we've found the beginning and ending indices of the data that we need to iterate over 
        
        #finding the stock
        
        stockIndex=0
        stockFound= False
        
        for stock in self.stocksList:
            if (stock.getSymbol()== stockName):
                #We've found the stock
                stockFound= True
                break
            
            stockIndex+=1
        #for ends
        
        if (stockFound is False):
            print "ERROR: Stock "+ stockName + " not found" 
#            raise ValueError
        
        
        tempArr= np.array([])
        for i in range (0, self.timestamps.size):
            if ((beginTS<= self.timestamps[i])and(self.timestamps[i]<= endTS)):
                tempArr= np.append (tempArr, self.allStocksData[valIndex][i][stockIndex])
            #if done
        #for done        
        
#        if (tempArr.size == 0):
#            print "WARNING tempARR is size ZERO"
#            print "start: " + str(beginTS)+", end: " + str(endTS)
#            return None  #bad idea
                
#        tempArr= np.zeros((endIndex- beginIndex +1), dtype=float)
#        tempArr[:]=np.NaN
         
          
        #Finally, we go over the data and copy relevant data to a temp array that is then returned
        
#        i= beginIndex
#        
#        while (i<= endIndex):
#            tempArr[i-beginIndex]= self.allStocksData[valIndex][i][stockIndex]
#            i+=1      
        return tempArr
               
    #getStockDataList done                            
                        
    def getStockDataItem(self, stockName, dataItem, timestamp):
     '''
     @summary: Returns the value of a time dependent property (like open, close) for a stock at a particular time
     @param stockName: name of the stock for which data is needed
     @param dataItem: name of the dataItem whose value is needed
     @param timestamp: The timestamp for which we need the value of 'dataItem'
     @return: one float value
     '''    
        #deal with stock not found
     stockCtr=0
     for stock in self.stocksList:
         stockFound=False
         
         if (stock.getSymbol()== stockName):
             #We've found the stock!
             stockFound=True
             #Now lets look through the timestamps
             
             timestampFound=False
             for i in range(0, self.timestamps.size):
                 if (self.timestamps[i]== timestamp):
                     timestampFound=True
                     
                     # Checking if the dataitem asked for exists or not... POSSUBLE BUG MUST BE TESTED
                     try:
                       if (self.dataItemsList.index(str(dataItem))>= 0):
                          # item exists..so we can return it. Note: the value returned can be NaN
                          return self.allStocksData [self.dataItemsList.index(dataItem)][i][stockCtr]
                     except:
                         raise ValueError
#                         if (self.noisy is True):
#                           print "Data item not found"
                           
                 #if (self.timestamps[i]== timestamp) ends          
             #for i in range(0, self.timestamps.size) ends              
             if (timestampFound is False):
               #Found the stock but not the timestamp
               raise ValueError
         
         #if (stock.getSymbol()== stockName) ends
         stockCtr+=1
     #for stock in self.stocksList ends    
     if (stockFound is False):
         #Could not find the stock
         raise ValueError
#getStockDataItem ends


    def getTimestampList(self):
        '''
        @summary: returns the list of all timestamps
        '''
        return self.timestamps
    
    def getListOfStocks(self):
        tempList=[]
        
        for stock in self.stocksList:
            tempList.append(stock.getSymbol())
        #for ends
        return tempList    

    def appendToTimestampsAndGetIndex (self, ts):
        
        
        if (self.allTimestampsAdded== False):
          index= np.searchsorted(self.timestamps, ts)
          if (index== self.timestamps.size):
              self.timestamps= np.append(self.timestamps, [ts], axis=0)
              if (len(self.timestamps) > 1):
                tempArray= np.zeros ((len(self.dataItemsList), 1, len(self.stocksList)), dtype=float) 
                tempArray[:][:][:]=np.NaN
                self.allStocksData= np.append(self.allStocksData, tempArray, axis=1)
              
#              print "self.allStocksData.shape: " + str(self.allStocksData.shape)
#              print "Ts list length: " + str (len(self.timestamps))
          #if done
          
          if ((ts == self.timestamps[0]) and (self.timestamps.size > 1)):
              self.allTimestampsAdded= True
              self.currIndex=0
              return self.currIndex
          #if done
          
          return index
        #if self.allTimestampsAdded done
        else:
            #all timestamps have been added
            if (ts == self.timestamps[0]):
                self.currIndex=0
            else:
                self.currIndex+=1
                
            return self.currIndex             
        #else ends      
             
    #appendToTimestampsAndGetIndex done             
            
    def insertIntoArrayFromRow(self, tsIndex, stockIndex, row):
        
#        print "tsIndex: " + str(tsIndex)+", stockIndex: "+ str(stockIndex)
        print "self.allStocksData.shape: " + str(self.allStocksData.shape)
        for dataItem in self.dataItemsList:
           try:
#               print "self.allStocksData.shape: " + str(self.allStocksData.shape)+ "self.dataItemsList.index(dataItem): " + str (self.dataItemsList.index(dataItem))+ ", tsIndex: "+ str(tsIndex)+", stockIndex"+ str(stockIndex)
               self.allStocksData[self.dataItemsList.index(dataItem)][tsIndex][stockIndex]= row[str(dataItem)]                
           except:
               if (self.noisy is True):
                 print str(dataItem)+ " not available for "+ row[self.SYMBOL]+" at "+ str(row[self.TIMESTAMP])
                 raise KeyError 
               #We are done with all the data
    #insertIntoArrayFromRow ends         
# class DataAccess ends