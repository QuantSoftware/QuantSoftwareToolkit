import tables as pt, numpy as np
from models.StrategyDataModel import StrategyDataModel
from numpy import NaN 
'''
Based on the model:
  
class StrategyDataModel(pt.IsDescription):
    symbol = pt.StringCol(30)           #30 char string; Ticker
    exchange = pt.StringCol(10)         #10 char string; NYSE, NASDAQ, etc.
    adj_high = pt.Float32Col()
    adj_low = pt.Float32Col()
    adj_open = pt.Float32Col()
    adj_close = pt.Float32Col()
    close = pt.Float32Col()
    volume = pt.Int32Col()
    timestamp = pt.Time64Col()
    when_available = pt.Time64Col()
    interval = pt.Time64Col()
'''

class StrategyData:
    def __init__(self,dataFile = None, isTable = False):
        #for pytables
        if dataFile == None:
            self.strategyDataFile = pt.openFile('StrategyDataModel.h5', mode = "w")
            self.strategyData = self.strategyDataFile.createTable('/', 'strategyData', StrategyDataModel)
        elif(dataFile != None and isTable == True):
            self.strategyDataFile = pt.openFile(dataFile, mode = "r")
            self.strategyData = self.strategyDataFile.root.tester.testTable
        elif(dataFile != None and isTable == False):
            self.prevTsIdx = 0
            #self.symbolIndex = np.array([])
            #self.timestampIndex = np.array([])
            #self.priceArray = np.ndarray(self.timestampIndex.size,self.symbolIndex.size)
        else:
            print 'You must specify type of dataFile: "pytables" or "array"'
        (self.timestampIndex, self.symbolIndex, self.priceArray) = generateRandomArray()
        
    def populateArray(self):
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
    
    def getStocks(self, startTime=None, endTime=None, ticker=None, isTable = False):
        '''
        Returns a list of dictionaries that mimic the pytables rows in accessing
        Can be called independently or used as part of the getPrices function
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock
        isTable: Using PyTables version (opposed to NumPy array version)
        '''
        if isTable:
            tempList = []
            if(ticker!=None):    
                for row in self.strategyData.where('symbol=="%s"'%ticker):
                    if(startTime!=None and endTime!=None):
                        if(row['timestamp']>=startTime and row['timestamp']<=endTime):
                            tempList.append(self.cloneRow(row))
                    elif(startTime!=None):
                        if(row['timestamp']>=startTime):
                            tempList.append(self.cloneRow(row))
                    elif(endTime!=None):
                        if(row['timestamp']<=endTime):
                            tempList.append(self.cloneRow(row))
                    else: #no time given
                        tempList.append(self.cloneRow(row))    
            else:
                for row in self.strategyData.iterrows():
                    if(startTime!=None and endTime!=None):
                        if(row['timestamp']>=startTime and row['timestamp']<=endTime):
                            tempList.append(self.cloneRow(row))
                    elif(startTime!=None):
                        if(row['timestamp']>=startTime):
                            tempList.append(self.cloneRow(row))
                    elif(endTime!=None):
                        if(row['timestamp']<=endTime):
                            tempList.append(self.cloneRow(row))
                    else: #no time given
                        tempList.append(self.cloneRow(row))                    
            return tempList
        else:
            return self.getStocksArray(startTime, endTime, ticker)
    
    def getPrice(self, timestamp, ticker, description, isTable=False):
        '''
        timestamp: the exact timestamp of the desired stock data
        ticker: the ticker/symbol of the stock
        description: the field from data that is desired IE. adj_high
        NOTE: If the data is incorrect or invalid, the function will return None  
        isTable: Using PyTables version (opposed to NumPy array version)  
        '''
        if isTable:
            result = None
            for row in self.strategyData.where('symbol=="%s"'%ticker):
                if row['timestamp']==timestamp:
                    result = row[description]
            return result
        else:
            return self.getPriceArray(timestamp, ticker, description)
        
    def getPrices(self, startTime=None, endTime=None, ticker=None, description=None, isTables=False):
        '''
        Returns a list of prices for the given description or a dictionary of information (accessed using field names) if no description is given
        description: the field from data that is desired IE. adj_high
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock 
        isTable: Using PyTables version (opposed to NumPy array version)  
        '''
        if isTables:
            rows = self.getStocks(startTime, endTime, ticker)
            result = []
            if(description==None):
                for row in rows:
                    result.append(self.cloneRow(row))
            else:
                for row in rows:
                    result.append(self.cloneRow(row)[description])
            return result
        else:
            return self.getPricesArray(startTime, endTime, ticker, description)
    
    def cloneRow(self,row):
        ''' 
        Makes a copy of the row so that the correct information will be appended to the list
        '''
        dct = {}  
        dct['symbol'] = row['symbol']
        dct['exchange'] = row['exchange']
        dct['adj_high'] = row['adj_high']
        dct['adj_low'] = row['adj_low']
        dct['adj_open'] = row['adj_open']
        dct['adj_close'] = row['adj_close']
        dct['close'] = row['close']
        dct['volume'] = row['volume']
        dct['timestamp'] = row['timestamp']
        dct['when_available'] = row['when_available']
        dct['interval'] = row['interval']            
        return dct
 
    def getStocksArray(self, startTime=None, endTime=None, ticker=None):
        '''
        Returns a list of dictionaries that mimic the pytables rows in accessing
        Can be called independently or used as part of the getPrices function
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock
        isTable: Using PyTables version (opposed to NumPy array version)
        '''
        #print "GSA ST ET TKER", startTime, endTime, ticker
        if ticker != None:
            tickerIdx = self.symbolIndex.searchsorted(ticker)
            if tickerIdx >= self.symbolIndex or self.symbolIndex[tickerIdx] != ticker:
                tickerIdx =  None 
        else:
            tickerIdx = None      
        if startTime != None:
            startIdx = self.timestampIndex.searchsorted(startTime)
        else:
            startIdx = None
        if endTime != None:
            endIdx = self.timestampIndex.searchsorted(endTime)
        else:
            endIdx = None
        if tickerIdx != None:
            #print "with tkrIdx",startIdx, endIdx+1, tickerIdx, self.priceArray[startIdx:endIdx+1,tickerIdx][0]
            return self.priceArray[startIdx:endIdx+1,tickerIdx]#[0]
        else:
            #print 'no tkrIdx',startIdx, endIdx+1, self.priceArray[startIdx:endIdx+1,:][0]
            return self.priceArray[startIdx:endIdx+1,:][0]
        
        
    def getPriceArray(self, timestamp, ticker, description):
        '''
        timestamp: the exact timestamp of the desired stock data
        ticker: the ticker/symbol of the stock
        description: the field from data that is desired IE. adj_high
        NOTE: If the data is incorrect or invalid, the function will return None  
        isTable: Using PyTables version (opposed to NumPy array version)  
        '''
        tsIdx = self.timestampIndex.searchsorted(timestamp)
        #print 'TSIDX', tsIdx
        if tsIdx >= self.timestampIndex.size or self.timestampIndex[tsIdx] != timestamp:
            #print 'first none'
            return None #NaN  
        tickerIdx = self.symbolIndex.searchsorted(ticker)
        #print "TICKERIDX", tickerIdx
        #print ticker, self.symbolIndex[tickerIdx]
        if tickerIdx >= self.symbolIndex.size or self.symbolIndex[tickerIdx] != ticker:
            #print 'second none'
            return None #NaN
        return self.priceArray[tsIdx,tickerIdx][description]
 
    def getPricesArray(self, startTime=None, endTime=None, ticker=None, description=None):
        '''
        Returns a list of prices for the given description or a list of tuples of prices if no description is given
        description: the field from data that is desired IE. adj_high
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock  
        '''
        rows = self.getStocksArray(startTime, endTime, ticker)
        #print 'ROWS',rows
        result = []
        if(description==None):
            result = rows
        else:
            for row in rows:
                #print 'ROW', row
                result.append({description:row[description],'timestamp':row[timestamp],'symbol':row[symbol]})
        return result 

    def close(self):
        self.strategyDataFile.close()

def generateRandomArray():
    import random
    random.seed(1)    
    #86400 seconds in a day
    timestamps = np.array([])
    stocks = np.array([])
    for i in range(10,100): #timestamps
        timestamps = np.append(timestamps,i*86400)
    for i in range(30): #stocks
        stocks = np.append(stocks,'stock%.6i'%i)

    priceArray = np.ndarray( shape=(timestamps.size, stocks.size), dtype=np.object)
    for i in range(timestamps.size):    
        for j in range(stocks.size):
            row = {}
            adjOpen = random.random() * random.randint(1,100)   
            adjClose = random.random() * random.randint(1,100) 
            row['exchange'] = 'NYSE'
            row['symbol'] = stocks[j]
            row['adj_open'] = adjOpen 
            row['adj_close'] = adjClose
            row['adj_high'] = max(adjOpen,adjClose) * random.randint(1,5)
            row['adj_low'] = min(adjOpen,adjClose) / random.randint(1,5)
            row['close'] = adjClose
            row['volume'] = random.randint(1000,10000)
            row['timestamp'] = timestamps[i]
            row['when_available'] = timestamps[i]
            row['interval'] = 86400
            priceArray[i,j] = row 
        if i%10==0:
            print i,
        if i%100==0:
            print ''
    print ''
    #print priceArray
    return (timestamps, stocks, priceArray)

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
#classTest()