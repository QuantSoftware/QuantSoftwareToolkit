'''
Created on Jun 2, 2010

@author: Shreyas Joshi
@contact: shreyasj@gatech.edu
'''

import tables as pt
#import sys


class DataAccess:
    '''
    @attention:  Assumption is that the data has symbols and timestamps. Also assumes that data is read in from low timestamp to high timestamp.
                 data is not sorted after reading in.
    @warning: No checks are perform to prevent this function from returning future data. You will get what you ask for! (assuming its there!)
    @summary: The purpose of this class is to be a general way to access any data about stocks- that is in a 2-D array with one dimension
              being stock symbols and the other being time. Each element of data can be an encapsulation of things like opening price, closing
              price, adj_close etc... or it can just be a single value.
    '''

    def __init__(self, fileIterator, noisy, dataItemsList=None, SYMBOL='symbol', TIMESTAMP='timestamp'):
        '''
        @param fileIterator: [filename].[root].[group name].[table name] as needed to read in and hdf5 file 
        @param noisy: is it noisy?  
        @param dataItemList: should be a list of all the data items that need to be read in from the file. If None then all will data will be read
        @param SYMBOL: just in case that the name of the "symbol" data item is not exactly "symbol" this can be changed.
        '''
        
        self.allDataList=[]
        self.dataItemsList=[]
#        self.SYMBOL=[]
#        self.TIMESTAMP=[]    
        self.SYMBOL= SYMBOL
        self.TIMESTAMP= TIMESTAMP
        self.noisy=noisy
        
        
       #Making sure dataItemsList has symbols and timestamps
        if (dataItemsList is not None):
         try:
          dataItemsList.index("symbol")
         except ValueError:
           print "adding SYMBOL"   
           dataItemsList.append(self.SYMBOL)
          
         try:
          dataItemsList.index("timestamp")
         except ValueError:  
           print "adding TIMESTAMP"
           dataItemsList.append(self.TIMESTAMP)  
          
        else:
         #adding all known items to the list- change this list to change default behaviour (ie when dataItemsList is none)
         dataItemsList= list()
         dataItemsList.append('symbol')
         dataItemsList.append('timestamp')
         dataItemsList.append('exchange')
         dataItemsList.append('adj_open')    
         dataItemsList.append('adj_close')
         dataItemsList.append('adj_high')
         dataItemsList.append('adj_low')
         dataItemsList.append('close')
         dataItemsList.append('volume')
         
        self.dataItemsList= dataItemsList
        for row in fileIterator.iterrows():  
#          print "SYM: "+str(row['symbol'])+", EX: "+ str(row['exchange'])+", ALPHA: "+str(row['alphaValue'])+", TIMESTAMP: "+str(row['timestamp'])
          self.allDataList.append(self.cloneRow(row, dataItemsList))
#          print self.allDataList[len(self.allDataList)-1]
        self.allDataList.sort(cmp=None, key=None, reverse=False)  
    # constructor ends
    

    def getData (self, stockList=None, dataList=None, beginTS=None, endTS=None):            
        '''
        @param stockList: If data about only 1 stock is needed then this param can be a string- else a list of strings of names of all the stocks that you want data about. If not specified data about all stocks will be returned
        @param dataList: If only one dataItem is needed (say adj_open only) then this param can be a string- else a list of strings of the names of all the data items you want. If not specified all data items will be returned.
        @param beginTS: If specified- only rows with timestamp greater than or equal to this will be returned
        @param endTS: If specified- only rows with timestamp smaller than or equal to this will be returned
        
        @warning: function does not check if beginTS < endTS- but violating this will result in None being returned.       
        @summary: this function just traverses over the data. It assumes that all the data fits into memory.
                  The real reading from disk is done in the constructor
                  To get data for one timestamp only- set beginTS=endTS= the timestamp you want.
        @return: returns the requested data as a list. NOTE: the returned list will always have symbol and timestamp- 
                 even if they weren't explicitly asked for in the dataItemsList. If no data is found then an empty list is returned.
        '''
        
        #stockList (despite its name) can be a string or a list
        if (stockList is not None):
         if (type(stockList) is not list):
            if (type (stockList) is not str):
                print "Stocks must either be a string (if you want only 1 stock) or a list of strings"
                raise TypeError
            else:
                #its not a list but its a string
                tempStr= str(stockList)
                stockList= list()
                stockList.append(tempStr)
#                print "changed stockList from str to list!"
#                print "Printing first in the list: " + stockList[0]
        
        
        #dataList (despite its name) can be a string or a list
        if (dataList is not None):
         if (type(dataList) is not list):
            if (type (dataList) is not str):
                print "data items you want must either be a string (of you want only one data item) or a list of strings"
                raise TypeError
            else:
                #its not a list but its a string
                tempStr= str(dataList)
                dataList= list()
                dataList.append(tempStr)
#                print "changed dataList from str to list!"
#                print "Printing first in the list: " + dataList[0]
        else:
            #dataList is None
            dataList= self.dataItemsList
                
        #Making sure dataList has symbols and timestamps
        try:
         dataList.index("symbol")
        except ValueError:
#          print "adding SYMBOL"   
          dataList.append(self.SYMBOL)
          
        try:
         dataList.index("timestamp")
        except ValueError:  
#          print "adding TIMESTAMP"
          dataList.append(self.TIMESTAMP)
               
        #Now, filter out the data from allDataList, put it in another list (inefficient?) and return the other list
        tempFilteredList=[]
        for item in self.allDataList:
            if (beginTS is not None):
              # which means we need to reject all rows with timestamp < beginTS
              if item[self.TIMESTAMP]< beginTS: # so = will be included
#                  print "rejecting because of beginning TS"
                  continue #skipping this item
            
            if (endTS is not None):
               # which means we need to reject all rows with timestamp > endTS
               if item[self.TIMESTAMP]> endTS: # so = will be included
#                  print "rejecting because of ending TS" 
                  continue #skipping this item
            
            if (stockList is not None):
             # We need to return this item only if its name is present in the stockList
             nameFound= False
             for item2 in stockList:
                 if (item2== item [self.SYMBOL]):
                    nameFound= True
             #searching done
             if (nameFound== False):
#                 print "rejecting because of stock name not found"
                 continue #skipping this item
                                  
             # if we got till here then the row must be returned. Hence adding to list
            if (dataList is None): 
             tempFilteredList.append(self.cloneRow(item, self.dataItemsList))
            else:
             tempFilteredList.append(self.cloneRow(item, dataList))    
        # for item in self.allDataList done
        
        if (len (tempFilteredList)==0):
            if self.noisy is True:
             print "Warning: no data found"
#            sys.stdout.flush()
        
        
        return tempFilteredList        
        
    # getData ends
    
    def getDataList(self, stockName, dataItemName, beginTS=None, endTS=None):
     '''
     @param stockName: The name of the stock whose data you need. This has to be a string. One stock only
     @param dataItemName:The data item that you need like open, close, volume etc. This has to be a string. Only one can be specified.
     @param beginTS: Optional parameter. If specified only data for timestamp >= beginTS will be considered.
     @param endTS: Optional paramter. If specified only data for timestamp <= endTS will be considered.
      
     @warning: function does not check if beginTS < endTS- but violating this will result in None being returned.
     @summary: Use this function to get a list of values of some dataItem of a particular stock. Unlike the getData function this function 
               does not return a list of dictionaries with the stock symbol and timestamp. 
               To get data for one timestamp only- set beginTS=endTS= the timestamp you want.
     @return: A list of dataItemName values for stockName between beginTS and endTS- if specified - or values for all timestamps if not
              specified. If no data is found then an empty list is returned.          
     '''   
    
     if (type(stockName) is not str):
         print "stock name must be a string"
         raise TypeError
     
     if (type(dataItemName) is not str):
         print "data item must be a string"
         raise TypeError
     
     tempList=[]
     
     for item in self.allDataList:
         if beginTS is not None:
           if item[self.TIMESTAMP]< beginTS:
               continue #skipping this item
         
         if endTS is not None:
             if item[self.TIMESTAMP] > endTS:
                 continue #skipping this item
             
         if item[self.SYMBOL] == stockName:
             tempList.append(item[dataItemName])
     #for loop ends
     
     if (len (tempList)==0):
         if self.noisy is True:
           print "Warning: no data found"
#         sys.stdout.flush()
                 
     return tempList              
    #getDataList ends
    
    
    def getDataItem (self, stockName, dataItemName, timestamp):
        
     '''
     @param stockName: The name of the stock whose data you need. This has to be a string. One stock only
     @param dataItemName:The data item that you need like open, close, volume etc. This has to be a string. Only one can be specified.
     @param timestamp: Required parameter. Only data for this timestamp will be considered.
    
     @summary: Use this function to get one value of some dataItem of a particular stock. Unlike the getData function, this function 
               does not return a list of dictionaries with the stock symbol and timestamp. Unlike the getDataList function, this 
               function does not return an array of values. 
     @return: The value of dataItemName value for stockName at the specified timestamp
     '''   
        
     if (type(stockName) is not str):
         print "stock name must be a string"
         raise TypeError
     
     if (type(dataItemName) is not str):
         print "data item must be a string"
         raise TypeError
     
#       tempStr=str("")
     
     for item in self.allDataList:
           if item[self.SYMBOL]== stockName:
               if item[self.TIMESTAMP]== timestamp:
                   return item[dataItemName]            
       
     if self.noisy is True:
      print "Warning: no data found"
#     sys.stdout.flush()
     return None
    #getDataitem ends    
    
    
    def cloneRow(self, row, itemsList):
        
        dct={}
        for dataItem in itemsList:
            try:
             dct[str(dataItem)]= row[str(dataItem)] 
            except KeyError:
             print "Error: "+str(dataItem)+" not available"
             raise KeyError
        return dct