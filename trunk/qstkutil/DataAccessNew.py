'''
Created on Sep 22, 2010

@author: sjoshi42
'''

'''
Created on Jun 14, 2010

@author: Shreyas Joshi
@contact: shreyasj@gatech.edu
'''

__version__ = "$Revision: 156 $"

import numpy as np
import tables as pt
import time
import os
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
    @summary: This class will be used to access all stock data
    @attention: This will not work if the timestamps are out of order. It should work for increasing timestamps whether the data is 1 timestamp all stocks (and then the next timestamp) or 1 stock all timestamps (and then the next stock)
    '''
    
    def __init__(self, isFolderList, folderList, groupName, nodeName, verbose, listOfStocks=None, beginTS=None, endTS=None, staticDataItemsList=None, dataItemsList=None, SYMBOL='symbol', TIMESTAMP='timestamp'):
        '''
        @summary: When reading in stock data- each stock has its own hdf5 file. All the files are stored in a list of folders (which should be given
        to this function as the folderList argument.) The files relevant to the stocks in the listOfStocks are opened- the data is read in and
        the file is then closed. All data is assumed to fit into memory. (2GB mem = ~1000 stocks)
        @attention: When reading in data from multiple files- it is assumed that all stock data is read in at one time and once only. No such assumption is made when reading in from one file only. However- the timestamps must be in ascending oder. Both: the data is 1 timestamp all stocks (and then the next timestamp) or 1 stock all timestamps (and then the next stock) should work.
        @param isFolderList: Indicates if folderList is a folder name or a file name. True if is folder. False if is file.
        @param folderList: list of folder names where the hdf files are located / one file 
        @param verbose: verbose or not True/False
        @param listOfStocks: specifies which list of stocks to read in. This is ignored if isFolderList = False
        @param beginTS: specifies the timestamp since epoch from which data should be read in. Value of beginTS itself will be included.
        @param endTS: specified the timestamp since epoch upto which data whould be read in. Value of endTS itself will be included.
        @param staticDataItemsList: The list of items that need to be stored only once per stock. Like symbol, exchange etc
        @param dataItemsList: List of items that need to be stored once per timestamp per stock
        @bug: For some reason windows did not allow creation of a file called PRN.csv. Norgate renames it to PRN_.csv making the file name different from
        the symbol name. Currently the CSV to HDF5 converter will create a PRN_.h5 file. DataAccess API has not been tested for this yet. My guess is that everything
        should be OK if the listOfStocks has PRN_ as the name and later the actual symbol (PRN only w/o the underscore) is used.
        A quick ls | grep *_* shows that this is the only stock with an '_'- so I guess the only stock with the problem. Crazy huh? (Lucky we found it though!)
        @bug: If endTS is not itself present in the file then (sometimes) one timestamp after the end timestamp is returned. A similar (but yet unobserved) possibility exists with beginTS. ts values which cause this behaviour:  946702800 , 1262322000. As of now fix is unknown.
        '''
    
        
        self.SYMBOL= SYMBOL
        self.TIMESTAMP= TIMESTAMP
        self.folderList= folderList
        self.previousTimestampIndex=0
        self.previousTimestamp=0
        
        if (staticDataItemsList is None):
            staticDataItemsList= list()
            staticDataItemsList.append(self.SYMBOL)
            staticDataItemsList.append('exchange')
        
        if (dataItemsList is None):
        
         dataItemsList= list()
         dataItemsList.append('volume')
         dataItemsList.append('adj_open')    
         dataItemsList.append('adj_close')
         dataItemsList.append('adj_high')
         dataItemsList.append('adj_low')
         dataItemsList.append('close')
#         dataItemsList.append('ogre')
         
        self.isFolderList= isFolderList
        self.verbose= verbose 
        self.dataItemsList= dataItemsList
        self.staticDataItemsList= staticDataItemsList
        self.stocksList=[] # This is different from listOfStocks in that listOfStocks is the list that was passed to this- stocksList refelcts the current state of how many stocks have been read in etc.
        self.listOfStocks= listOfStocks
        self.timestamps= np.array([])
#        self.nanArray= np.zeros((1, len(self.dataItemsList)), dtype=float) #Possible bug
        
        if (listOfStocks is None):
          self.allStocksData= np.zeros((len(dataItemsList), 1, 1), dtype=float) # dataItems, timestamps, stocks
          self.allStocksData[:][:][:]=np.NaN #Set all elements to NaN
        #if ends
        
        
        self.allTimestampsAdded= False
        self.allStocksDataInited= False
        
        print "Starting to read in data..." + str(time.strftime("%H:%M:%S"))
        
#        for stockName in listOfStocks:
#          
##          try:
#          h5f = pt.openFile(str(folderName)+ str(stockName)+".h5", mode = "r") # if mode ='w' is used here then the file gets overwritten!
#          print h5f
#        #end for  
        
        if (isFolderList is True):
         for stockName in listOfStocks:
        
#          try:
          if (True):
             h5f = pt.openFile(self.getPathOfFile(stockName), mode = "a") # if mode ='w' is used here then the file gets overwritten!
#             fileIterator= h5f.root.StrategyData.StrategyData
             fileIteratorNode= h5f.getNode(groupName, nodeName)
             noOfElements = -1
             
             if (beginTS is not None): #This is not pretty, I know
                 #beginTS is not none
                 if (endTS is not None):
                     #Both beginTS and endTS are not none
                     fileIterator = fileIteratorNode.where ('(('+str(self.TIMESTAMP)+'>='+str(beginTS)+')&('+str(self.TIMESTAMP)+'<='+str(endTS)+'))') 
                     if (self.allStocksDataInited is False):
                         noOfElements= len (list(fileIteratorNode.where ('(('+str(self.TIMESTAMP)+'>='+str(beginTS)+')&('+str(self.TIMESTAMP)+'<='+str(endTS)+'))')))  
                 
                 else:
                      #beginTS is not none BUT endTS is none
                      fileIterator= fileIteratorNode.where (str(self.TIMESTAMP)+'>='+str(beginTS))
                      #print "TYPE2: " + str(type(fileIteratorNode.where (str(self.TIMESTAMP)+'>='+str(beginTS))))
                      if (self.allStocksDataInited is False):
                          noOfElements= len(list(fileIteratorNode.where (str(self.TIMESTAMP)+'>='+str(beginTS))))
             else:
                 #beginTS is None
                 if (endTS is not None):
                     fileIterator= fileIteratorNode.where (str(self.TIMESTAMP)+'<='+str(endTS))
                     if (self.allStocksDataInited is False):
                         noOfElements= len(list(fileIteratorNode.where (str(self.TIMESTAMP)+'<='+str(endTS))))
                 else:
                     fileIterator= fileIteratorNode.iterrows() #a hack so that the rest of the program works    
#          except:
#             print str(stockName)+" not found."
#             continue #skipping the rest of the processing for this stock
              
          
          if (self.allStocksDataInited is False):  
             self.allStocksDataInited= True
             if (noOfElements > -1):
                 self.allStocksData= np.zeros((len(dataItemsList), noOfElements, len (listOfStocks)), dtype=float) # dataItems, timestamps, stocks
             else:
                 self.allStocksData= np.zeros((len(dataItemsList), fileIteratorNode.nrows, len (listOfStocks)), dtype=float) # dataItems, timestamps, stocks
                     
             self.allStocksData[:][:][:]=np.NaN #Set all elements to NaN
          #if (self.allStocksDataInited is False): ends   
          
          for row in fileIterator:
            
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
               
               if (self.verbose is True):
                   print "Adding stock " + str(row[self.SYMBOL])+ ". Current no. of stocks: " + str(len(self.stocksList))+"  "+str(time.strftime("%H:%M:%S"))
               #if self.verbose ends    
               
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
                  pass #commenting out code that used to make space for new stock
              
                  #tempArray= np.zeros((len(dataItemsList), len(self.timestamps), 1), dtype=float)
                  #tempArray[:][:][:]= np.NaN
#                  print "temp: " + str (tempArray.shape)
#                  print "allStocksData: " + str (self.allStocksData.shape)
                  
                  #self.allStocksData= np.append (self.allStocksData, tempArray, axis=2)
               #if (len(self.stocksList) > 1) ends
           #if stockFound is False ends
           
            tsIndex= self.appendToTimestampsAndGetIndex(row[self.TIMESTAMP]) # will be ZERO for first timestamp
            #self.insertIntoArrayFromRow(tsIndex, self.allStocksData.shape[2]-1, row) #NOTE: different from reading a single hdf5 file
            self.insertIntoArrayFromRow(tsIndex, len(self.stocksList) -1 , row) #NOTE: different from reading a single hdf5 file
          
          #for row in fileIter ends
          h5f.close()
         #for stockName in listOfStocks: ends
        #if (isFolderName is True) ends
        else:
            #THIS IS NOT IDEAL!
            #if (isFolderName is True) is False
            h5f = pt.openFile(str(folderList), mode = "a") # This is not the folderList but in this case, a string which is the path of 1 file only
            fileIteratorNode= h5f.getNode(groupName, nodeName)

            if (beginTS is not None):
                 #beginTS is not none
                 if (endTS is not None):
                     #Both beginTS and endTS are not none
                     fileIterator = fileIteratorNode.where ('(('+str(self.TIMESTAMP)+'>='+str(beginTS)+')&('+str(self.TIMESTAMP)+'<='+str(endTS)+'))')
                 else:
                      #beginTS is not none BUT endTS is none
                      fileIterator= fileIteratorNode.where (str(self.TIMESTAMP)+'>='+str(beginTS))
            else:
                 #beginTS is None
                 if (endTS is not None):
                     fileIterator= fileIteratorNode.where (str(self.TIMESTAMP)+'<='+str(endTS))
                 else:
                      fileIterator= fileIteratorNode.iterrows() #a hack so that the rest of the program works    
                         

            
            
            #rowCtr=0
            for row in fileIterator:
             
             #print "Adding " + str(rowCtr)+ " of "+ str(totalRows) 
             #rowCtr+=1
             
             #print "Adding row for stock: " + str(row[self.SYMBOL])
             stockFound=False
             stockIndex=0
             if (len(self.stocksList) > 0):
#               if (self.stocksList[len(self.stocksList) -1].getSymbol()== row[self.SYMBOL]):
                try:
                    stockIndex= self.getListOfStocks().index(row[self.SYMBOL])
                    stockFound= True
                except:    
                    stockIndex= len(self.stocksList)# because we will now add one more entry to the end
                    stockFound= False
             #inner if done
            #if (len(self.stocksList) > 0) done 
          
             if (stockFound is False): #Should happen only once for every stock
               #this is the first time we are seeing this stock...
#               print "Stocknotfound begins " + str(time.time())
               
               if (self.verbose is True):
                   #print "Adding stock " + str(row[self.SYMBOL])+ ". Current no. of stocks: " + str(len(self.stocksList))+"  "+str(time.strftime("%H:%M:%S"))
                   print "Adding stock " + str(row[self.SYMBOL])+"  "+str(time.strftime("%H:%M:%S"))
               #if self.verbose ends    
               
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
             self.insertIntoArrayFromRow(tsIndex, stockIndex, row) #NOTE: different from reading a multiple hdf5 files
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
    def getMatrixFromTS(self, stocksList, dataItem, ts, days):
        '''
        @summary: Gets the desired data item for 'days' no of trading days from the timestamp ts. If days <0 then data if from 'days' no of days before the timestamp ts. Else it is 'days' no of days after the timestamp ts. Both the begin and the end timestamps are inclued. So- asking for 'n' days will cause this to return (n+1) timestamps. This is a lot more convenient because you don't have to bother about non-trading days.
        @param stocksList: list of stocks- whose data you need
        @param dataItem: The data item you need. Ex adj_close, adj_open etc...
        @param ts: The timestamp- relative to which you need the data
        @param days: No of days for which you need the data 
        '''
        
        try:
            
          index1= self.timestamps.searchsorted(ts)
          if (self.timestamps[index1]== ts):
            #timestamp found!
            if (days < 0):
                if (index1 + days >=0): #remember days is -ve here
                    return (self.getMatrixBetweenIndex(stocksList, dataItem, index1+ days, index1))
                else:
                    print "Index out of bounds 0 "+ str(ts)
                    return None
            else:
                #days >= 0
                if (index1 + days < len (self.timestamps)):
                    return (self.getMatrixBetweenIndex(stocksList, dataItem, index1, index1+ days))
                else:
                    print "Index out of bounds 1 "+ str(ts)
                    return None
            #if (self.timestamps[index1]== ts): ends
          else:
            #Timestamp not found  
            print "Timestamp " + str(ts) +" not found."
            return None
            
        except IndexError:
            print "IndexError: " + str(ts)
            return None #Possible bug?
        #getMatrixFromTS done        
                
    
    

    def getMatrixBetweenTS (self, stocksList, dataItem, beginTS=None, endTS=None):
        '''
        @summary: includes beginTS and endTS. This uses the getMatrixBetweenIndex function.
        @param stocksList: The list of stock names for which you want the data.
        @param dataItem: The dataItem that you want ex, open , close
        @param beginTS: The beginning timestamp
        @param endTS: The ending timestamp
        @return: a 2D numpy array such that: No. or rows = (endTS- beginTS +1) becuase both timestamps are included. No. of cols.= len (@param stocksList )
        '''
        
        if (len (stocksList)==0):
            print "Stock list is empty."
            return None
        
        
        if (beginTS is None):
            beginIndex=0
                
        else:
            if (endTS is not None): # if both are not none
                if (endTS< beginTS):
                    print "End timestamp is smaller than begin timestamp. Returning nothing."
                    return None
                
            try:
                beginIndex= self.timestamps.searchsorted(beginTS)
                if (self.timestamps[beginIndex] != beginTS): #sadly searchsorted does not indicate whether the item is actually present or not
                    raise ValueError
                
                print "beginIndex is: " + str(beginIndex)
            except ValueError:
                print "Begin timestamp not found"
                return None
        #else done
        
        if (endTS is None):
            endIndex= len(self.timestamps) -1
        else:
            try:
                endIndex= self.timestamps.searchsorted(endTS)
                if (self.timestamps[endIndex] != endTS):
                    raise ValueError
                
                print "endIndex is: " + str(endIndex)
            except ValueError:
                print "End timestamp not found"
                return None
        #else done
        return (self.getMatrixBetweenIndex(stocksList, dataItem, beginIndex, endIndex))
        #getMatrix ends
        
        
        
        
    def getMatrixBetweenIndex (self, stocksList, dataItem, beginIndex, endIndex):
        '''
        @return: returns data for the specific stocks between and inclusive of the beginIndex and the endIndex. So it returns (endindex- beginIndex)+1 number of rows and len (stockList) number of columns.
        @return: a 2D numpy array such that: No. or rows = (endIndex- beginIndex +1) becuase both timestamps are included. No. of cols.= len (@param stocksList ) The data will be in the same order as the list of stocks passed to this function and not the same as the order in which the stock data was read in from disk
        @attention: If a stock is not found the data values for that stock in the array will be all NaN
        '''      
        tempArray= np.zeros((endIndex- beginIndex +1, len(stocksList)), dtype=float)
        tempArray[:][:]=np.NAN
        
        try:
            dataItemIndex= self.dataItemsList.index(dataItem)
        except ValueError:
            print str(dataItem)+" not found."
            return None
        
        listOfStocks= self.getListOfStocks()
        
        ctr=-1
        for stock in stocksList:
               ctr+=1
               try:
                 tempArray[:, ctr]= self.allStocksData[dataItemIndex, beginIndex:(endIndex+1), listOfStocks.index(stock)]
               except ValueError:
                   print "No data for stock " + str(stock)
               
               #for ends
        
        return tempArray
        #return getMatrixBetweenIndex ends

    def getPathOfFile(self, stockName):
        '''
        @summary: Since a given HDF file can exist in any of the folder- we need to look for it in each one until we find it. Thats what this function does.
        
        '''
        for path1 in self.folderList:
            if (os.path.exists(str(path1)+str(stockName+".h5"))):
                # Yay! We found it!
                return (str(str(path1)+str(stockName)+".h5"))
                #if ends
#            else:
#                print str(path1)+str(stockName)+".h5" + " does not exist!"
            #for ends
        print "Did not find " + str (stockName)+" anywhere."
        #getPathOfFile done  
    
    def getStaticData(self, stockName, staticDataItem):
        '''
        @summary: Provides access to those properties of a stock that do not change with time
        @param stockName: The name of the stock- of which the properties are needed.
        @param staticDataItem: The name of the property whose value is needed
        @return: The asked for staticDataItem of the stock
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
        for i in range (0, self.timestamps.size): #enhancememnt : can be made faster with a np.searchsorted
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
     @note: Since most likely the simulation is going to proceed from earlier timestamps to newer timestamps. I decided to get sneaky here and optimize for that.
     '''    
        #deal with stock not found
     stockCtr=0
     for stock in self.stocksList:
         
         stockFound=False
         if (str(stock.getSymbol())== str(stockName)):
             #We've found the stock!
             stockFound=True
             #Now lets look through the timestamps
             timestampFound=False
             
             
             if (timestamp > self.previousTimestamp):
                 #most likely the case
                 for i in range (self.previousTimestampIndex, self.timestamps.size):
                     if (self.timestamps[i]== timestamp):
                         timestampFound=True
                         self.previousTimestampIndex=i
                         self.previousTimestamp= self.timestamps[i]
                        
                         # Checking if the dataitem asked for exists or not... POSSUBLE BUG MUST BE TESTED
                         try:
                            if (self.dataItemsList.index(str(dataItem))>= 0):
                            # item exists..so we can return it. Note: the value returned can be NaN
                              return self.allStocksData [self.dataItemsList.index(dataItem)][i][stockCtr]
                         except:
                           raise ValueError                         
                     #for i in range... ends
                 #if (timestamp > self.previousTimestamp) ends
             else:
                 #timestamp is smaller or equal
                 ctr= self.previousTimestampIndex
                 while (ctr>=0):
                     if (self.timestamps[ctr]== timestamp):
                         timestampFound=True
                         self.previousTimestampIndex=ctr
                         self.previousTimestamp= self.timestamps[ctr]
                         # Checking if the dataitem asked for exists or not... POSSUBLE BUG MUST BE TESTED
                         #try:
                         if (self.dataItemsList.index(str(dataItem))>= 0):
                            # item exists..so we can return it. Note: the value returned can be NaN
                              return self.allStocksData [self.dataItemsList.index(dataItem)][ctr][stockCtr]
                         #except:
                             #pass
                           #raise ValueError  
                                                   
                         #if ends
                     ctr-=1
                     #while ends    
                 #else ends
                 
             
             
             
#             timestampFound=False
#             for i in range(0, self.timestamps.size): #enhancement: This can be made faster
#                 if (self.timestamps[i]== timestamp):
#                     timestampFound=True
#                     
#                     # Checking if the dataitem asked for exists or not... POSSUBLE BUG MUST BE TESTED
#                     try:
#                       if (self.dataItemsList.index(str(dataItem))>= 0):
#                          # item exists..so we can return it. Note: the value returned can be NaN
#                          return self.allStocksData [self.dataItemsList.index(dataItem)][i][stockCtr]
#                     except:
#                         raise ValueError
#                         if (self.verbose is True):
#                           print "Data item not found"
                           
                 #if (self.timestamps[i]== timestamp) ends          
             #for i in range(0, self.timestamps.size) ends              
             if (timestampFound is False):
               #Found the stock but not the timestamp
               
               if (self.verbose is True):
                  print "In getStockDataItem: Timestamp not found for " + str(stockName)+" at " + (str(timestamp))
               
               return np.NaN
               #raise ValueError
         
         #if (stock.getSymbol()== stockName) ends
         stockCtr+=1
     #for stock in self.stocksList ends    
     
     if (stockFound is False):
         #Could not find the stock
         print "Could not find data for stock " + str(stockName)
         raise ValueError
#getStockDataItem ends


    def getTimestampArray(self):
        '''
        @summary: returns the numpy array of all timestamps
        '''
        return self.timestamps
    
    def getListOfStocks(self):
        tempList=[]
        
        for stock in self.stocksList:
            tempList.append(stock.getSymbol())
        #for ends
        return tempList    

    def appendToTimestampsAndGetIndex (self, ts):
       '''
       @attention: This will not work if the timestamps are out of order. It should work for increasing timestamps whether the data is 1 timestamp all stocks (and then the next timestamp) or 1 stock al timestamps (and then the next stock) 
       '''
        
       if (self.isFolderList is True): 
        if (self.allTimestampsAdded== False):
          index= np.searchsorted(self.timestamps, ts)
          if (index== self.timestamps.size):
              self.timestamps= np.append(self.timestamps, [ts], axis=0)
              if (len(self.timestamps) > 1):
                  pass
              
#                tempArray= np.zeros ((len(self.dataItemsList), 1, len(self.listOfStocks)), dtype=float) 
#                tempArray[:][:][:]=np.NaN
#                print "Appending"
#                self.allStocksData= np.append(self.allStocksData, tempArray, axis=1)
#                print "Appended"
#              print "self.allStocksData.shape: " + str(self.allStocksData.shape)
#              print "Ts list length: " + str (len(self.timestamps))
          #if done
          
          if ((ts == self.timestamps[0]) and (self.timestamps.size > 1)):
              self.allTimestampsAdded= True
              print "Done adding all timestamps"
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
                if (self.timestamps[self.currIndex]!= ts): #Checking for the just in case scenario
                    print "ERROR. Something is wrong. This timestamp was not seen in previous stock"
                    raise ValueError 
                
            return self.currIndex
        #else ends      
       #if (self.folderList is True): ends
       else:
           #if (self.folderList is True): is false
           if (self.allTimestampsAdded== False):
            index= np.searchsorted(self.timestamps, ts)
            
            if (index== self.timestamps.size):
               self.timestamps= np.append(self.timestamps, [ts], axis=0)
               if (len(self.timestamps) > 1):
                  tempArray= np.zeros ((len(self.dataItemsList), 1, 1), dtype=float)
                  tempArray[:][:][:]=np.NaN
                  self.allStocksData= np.append(self.allStocksData, tempArray, axis=1)
               return index
            elif (self.timestamps[index]== ts):
                return index 
    #appendToTimestampsAndGetIndex done             
            
    def insertIntoArrayFromRow(self, tsIndex, stockIndex, row):
        
        for dataItem in self.dataItemsList:
           try:
#               print "self.allStocksData.shape: " + str(self.allStocksData.shape)+ "self.dataItemsList.index(dataItem): " + str (self.dataItemsList.index(dataItem))+ ", tsIndex: "+ str(tsIndex)+", stockIndex"+ str(stockIndex)
               self.allStocksData[self.dataItemsList.index(dataItem)][tsIndex][stockIndex]= row[str(dataItem)]
               #print "Value of: " + str(dataItem)+" is: " + str(row[str(dataItem)])                
           except:
               if (self.verbose is True):
                 print str(dataItem)+ " not available for "+ row[self.SYMBOL]+" at "+ str(row[self.TIMESTAMP])
                 raise KeyError 
               #We are done with all the data
    #insertIntoArrayFromRow ends         
# class DataAccess ends
