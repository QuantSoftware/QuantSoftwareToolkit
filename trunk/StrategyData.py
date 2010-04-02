import models.StrategyDataModel, tables as pt, numpy as np
from numpy import NaN 
#WARNING DATA MODEL IS CHANGING METHODS WILL NEED TO BE MODIFIED
'''
Based on the model:
class PriceData(pt.IsDescription):
    adj_high = pt.Float32Col()
    adj_low = pt.Float32Col()
    adj_open = pt.Float32Col()
    adj_close = pt.Float32Col()
    close = pt.Float32Col()
    volume = pt.Int32Col()
    timestamp = pt.Time64Col()         #timestamp of price
    when_available = pt.Time64Col()    #time when data is available to simulator
    interval = pt.Time64Col()          #market close time - market open time
    
class StockPriceModel(pt.IsDescription):
    symbol = pt.StringCol(30)           #30 char string; Ticker
    exchange = pt.StringCol(10)         #10 char string; NYSE, NASDAQ, etc.
    data = PriceData()                  #creates a nested table for PriceData (see above)
  
'''

class StrategyData:
    def __init__(self,dataFile = None):
        #for pytables
        if dataFile == None:
            self.strategyDataFile = pt.openFile('StrategyDataModel.h5', mode = "w")
            self.strategyData = self.strategyDataFile.createTable('/', 'strategyData', StrategyDataModel)
        else:
            self.strategyDataFile = pt.openFile(dataFile, mode = "r")
            self.strategyData = self.strategyDataFile.root.tester.testTable
            
        #for array
        self.prevTsIdx = 0
        self.symbolIndex = np.array()
        self.timestampIndex = np.array()
        self.descriptionIndex = np.array(['adj_high','adj_low','adj_open','adj_close','close','volume'])
        
    def populateArray(self, timestamps):
        self.timestampIndex = np.array(timestamps)
        self.symbolIndex = self.findStocks()   
        self.priceArray = np.ndarray(self.timestampIndex.size,self.symbolIndex.size,self.descriptionIndex.size)
        for symbol in self.symbolIndex:
            for time in self.timestampsIndex:
                pass
        
    def findStocks(self):
        temp = []
        for i in self.strategyData.iterrows():
            if i['symbol'] not in temp:
                temp.append(cloneRow(i)['symbol'])
        temp.sort()
        return temp
        
    def cloneRow(self,row):
        dct = {}  
        dct['symbol'] = row['symbol']
        dct['exchange'] = row['exchange']
        dct['data/adj_high'] = row['data/adj_high']
        dct['data/adj_low'] = row['data/adj_low']
        dct['data/adj_open'] = row['data/adj_open']
        dct['data/adj_close'] = row['data/adj_close']
        dct['data/close'] = row['data/close']
        dct['data/volume'] = row['data/volume']
        dct['data/timestamp'] = row['data/timestamp']
        dct['data/when_available'] = row['data/when_available']
        dct['data/interval'] = row['data/interval']            
        return dct
    
    def getStocks(self, startTime=None, endTime=None, ticker=None):
        '''
        Returns a list of dictionaries that mimic the pytables rows in accessing
        Can be called independently or used as part of the getPrices function
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock   
        '''
        
#    for row in p.table.where('id==4'):
#        if row['nest/f1'] == 10:
#          print row
        tempList = []
        if(ticker!=None):    
            for row in self.strategyData.where('symbol=="%s"'%ticker):
                if(startTime!=None and endTime!=None):
                    if(row['data/timestamp']>=startTime and row['data/timestamp']<=endTime):
                        tempList.append(self.cloneRow(row))
                elif(startTime!=None):
                    if(row['data/timestamp']>=startTime):
                        tempList.append(self.cloneRow(row))
                elif(endTime!=None):
                    if(row['data/timestamp']<=endTime):
                        tempList.append(self.cloneRow(row))
                else: #no time given
                    tempList.append(self.cloneRow(row))    
        else:
            for row in self.strategyData.iterrows():
                if(startTime!=None and endTime!=None):
                    if(row['data/timestamp']>=startTime and row['data/timestamp']<=endTime):
                        tempList.append(self.cloneRow(row))
                elif(startTime!=None):
                    if(row['data/timestamp']>=startTime):
                        tempList.append(self.cloneRow(row))
                elif(endTime!=None):
                    if(row['data/timestamp']<=endTime):
                        tempList.append(self.cloneRow(row))
                else: #no time given
                    tempList.append(self.cloneRow(row))                    
        return tempList
    
    def getPrice(self, timestamp, ticker, description):
        '''
        timestamp: the exact timestamp of the desired stock data
        ticker: the ticker/symbol of the stock
        description: the field from data that is desired IE. adj_high
        NOTE: If the data is incorrect or invalid, the function will return None    
        '''
        result = None
        for row in self.strategyData.where('symbol=="%s"'%ticker):
            if row['data/timestamp']==timestamp:
                result = row['data/%s'%description]
        return result
        
    def getPrices(self, startTime=None, endTime=None, ticker=None, description=None):
        '''
        Returns a list of prices for the given description or a list of tuples of prices if no description is given
        description: the field from data that is desired IE. adj_high
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock   
        '''
        rows = self.getStocks(startTime, endTime, ticker)
        result = []
        if(description==None):
            for row in rows:
                result.append(row['data'])
        else:
            for row in rows:
                result.append(row['data/%s'%description])
        return result
    
    def close(self):
        self.strategyDataFile.close()
 
    def getStocksArray(self, startTime=None, endTime=None, ticker=None):
        tickerIdx = self.symbolIndex.searchSorted(ticker)
        if self.priceArray[tickerIdx] != ticker:
            tickerIdx =  None       
        if startTime != None:
            startIdx = self.symbolIndex.searchSorted(startTime)
        else:
            startIdx = None
        if endTime != None:
            endIdx = self.descriptionIndex.searchSorted(endTime)
        else:
            endIdx = None
        if tickerIdx != None:
            return self.priceArray[tickerIdx,startIdx:endIdx,:]
        else:
            return self.priceArray[:,startIdx:endIdx,:]

   
        return self.priceArray[tickerIdx,startTime:endTime,]
        
        
    def getPriceArray(self, timestamp, ticker, description):
        tsIdx = self.timestampIndex.searchSorted(ticker)
        if self.priceArray[tsIdx] != timestamp:
            return NaN
        tickerIdx = self.symbolIndex.searchSorted(ticker)
        if self.priceArray[tickerIdx] != ticker:
            return NaN
        descIdx = self.descriptionIndex.searchSorted(ticker)
        if self.priceArray[descriptionIdx] != description:
            return NaN
        return self.priceArray[tickerIdx,startIdx,descIdx]
 
 

def methodTest():
    strat = StrategyData('models/PriceTestData.h5')
    print strat.getStocks(startTime=0, ticker='KO')
#methodTest()
    
def classTest():
    '''
    Needs to be updated to reflect move from data class to interpreter class
    '''
    rows = getStocks(ticker = 'KO')
    rows = getStocks(1020, 1050)
    for row in rows:
        print row['symbol'], row['exchange'], row['timestamp'],\
            row['when_available'], row['interval'], row['data']
    
    price = getPrice('adj_high', 1020, 'KO')
    print price
    prices = getPrices('adj_high',ticker='KO')
    print prices