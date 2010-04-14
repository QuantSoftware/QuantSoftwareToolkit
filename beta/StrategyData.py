import tables as pt, numpy as np, pickle
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
    class OutputOrder:
        '''
        Subclass to make adding strategies easier
        '''
        def __init__(self,symbol = "",volume = 0,task = "",duration = 0,closeType = "",orderType = "",limitPrice = 0):
            self.symbol = symbol
            self.volume = volume
            self.task = task
            self.duration = duration
            self.closeType = closeType
            self.orderType = orderType
            self.limitPrice = limitPrice
            
        def getOutput(self):
            if self.symbol == "":
                print "No symbol in output."
                return None
            if self.volume == 0:
                #print (self.task,self.volume,self.symbol,self.orderType,self.duration,self.closeType,self.limitPrice)
                print "No volume in output."
                return None
            if self.task == "":
                print "No task in output."
                return None
            if self.duration == 0:
                print "No duration in output."
                return None
            if self.orderType == "":
                print "No orderType in output."
                return None
            if self.task.upper() == "SELL" or self.task.upper() == "COVER":
                if self.closeType == "":
                    print "No closeType specified for %s." % self.task
                    return None
            if self.orderType.upper() == "LIMIT":
                if self.limitPrice == 0:
                    print "No limitPrice specified."
                    return None
            return (self.task,self.volume,self.symbol,self.orderType,self.duration,self.closeType,self.limitPrice)
        '''
        END OutputOrder SUBLCLASS
        '''
    
    def __init__(self,dataFile,isTable = False):
        #for pytables
        self.currTimestamp = 0
        if(isTable):
            self.strategyDataFile = pt.openFile(dataFile, mode = "r")
            self.strategyData = self.strategyDataFile.root.tester.testTable
            self.timestampIndex = None
            self.stocksIndex = self.findStocks()
        else:
            self.prevTsIdx = 0
            #(self.timestampIndex2, self.symbolIndex2, self.priceArray2) = generateRandomArray()

            f = open(dataFile,'r')
            ts = pickle.load(f)
            st = pickle.load(f)
            pA = pickle.load(f)
            f.close()
            
            self.symbolIndex = st
            self.timestampIndex = ts
            self.priceArray = pA
            
            
            #(self.timestampIndex, self.symbolIndex, self.priceArray) = generateKnownArray()
                    
    def populateArray(self):
        for symbol in self.symbolIndex:
            for time in self.timestampsIndex:
                pass
        
    def findStocks(self):
        temp = []
        for i in self.strategyData.iterrows():
            if i['symbol'] not in temp:
                temp.append(self.cloneRow(i)['symbol'])
        temp.sort()
        return temp
    
    def calculatePortValue(self,stocks,timestamp, isTable = False):
        total = 0
        for stock in stocks:
            prices = self.getPrices(timestamp - 86400, timestamp, stock, 'adj_close', isTable = isTable)
            i = 86400
            count = 0
            while(len(prices)==0 and count<10):
                prices = self.getPrices(timestamp - i, timestamp - i - 86400, stock, 'adj_close')
                i += 86400
                count+=1
            #prices3 = self.getPrices(timestamp - 86400, timestamp, stock, 'adj_low')
            #prices4 = self.getPrices(timestamp - 86400, timestamp, stock, 'adj_high')
            #print "Low: %f"%(prices3[len(prices3)-1])# * stocks[stock])
            #print "High: %f"%(prices4[len(prices4)-1])# * stocks[stock])
            #print "timestamp: %d" % 
            if(len(prices) != 0):
                total += prices[len(prices)-1] * stocks[stock]
            
            #print total
        return total
    
    def getStocks(self, startTime=None, endTime=None, ticker=None, isTable = False):
        '''
        Returns a list of dictionaries that contain all of the valid stock data as keys
        or an empty list if no results are found
        Can be called independently or used as part of the getPrices function
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock or a list of tickers
        isTable: Using PyTables version (opposed to NumPy array version)
        '''
        if isTable:
            if endTime == None:
                endTime = self.currTimestamp
            if endTime > self.currTimestamp:
                print 'Tried to access a future time %i, endTime set to %i' %(endTime, self.currTimestamp)
                endTime = self.currTimestamp
            tempList = []
            if(ticker!=None):    
                if(type(ticker)==str):
                    for row in self.strategyData.where('symbol=="%s"'%ticker):
                        if(startTime!=None and endTime!=None):
                            if(row['timestamp']>=startTime and row['timestamp']<=endTime):
                                tempList.append(self.cloneRow(row))
                        elif(startTime!=None):
                            if(row['timestamp']>=startTime and row['timestamp']<=self.currTimestamp):
                                tempList.append(self.cloneRow(row))
                        elif(endTime!=None):
                            if(row['timestamp']<=endTime):
                                tempList.append(self.cloneRow(row))
                        else: #no time given
                            tempList.append(self.cloneRow(row))
                elif(type(ticker)==list):
                    for tick in ticker:
                        for row in self.strategyData.where('symbol=="%s"'%tick):
                            if(startTime!=None and endTime!=None):
                                if(row['timestamp']>=startTime and row['timestamp']<=endTime):
                                    tempList.append(self.cloneRow(row))
                            elif(startTime!=None):
                                if(row['timestamp']>=startTime and row['timestamp']<=self.currTimestamp):
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
                        if(row['timestamp']>=startTime and row['timestamp']<=self.currTimestamp):
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
        Returns a single price based on the parameters
        timestamp: the exact timestamp of the desired stock data
        ticker: the ticker/symbol of the stock
        description: the field from data that is desired IE. adj_high
        isTable: Using PyTables version (opposed to NumPy array version)  
        NOTE: If the data is incorrect or invalid, the function will return None  
        '''
        if isTable:
            result = None
            for row in self.strategyData.where('symbol=="%s"'%ticker):
                if row['timestamp']==timestamp:
                    result = row[description]
            return result
        else:
            return self.getPriceArray(timestamp, ticker, description)
        
    def getPrices(self, startTime=None, endTime=None, ticker=None, description=None, isTable=False):
        '''
        Returns a list of prices for the given description: [adj_high1, adj_high2, adj_high3...]
        or a tuple if no description is given: [ (adj_high1, adj_low1, adj_open1, adj_close1, close1), (adj_high2, adj_low2...), .... ]
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock or a list of tickers
        description: the field from data that is desired IE. adj_high
        isTable: Using PyTables version (opposed to NumPy array version)  
        '''
        if isTable:
            rows = self.getStocks(startTime, endTime, ticker, isTable = True)
            result = []
            if(description==None):
                for row in rows:
                    row = self.cloneRow(row)
                    result.append((row['adj_high'],row['adj_low'],row['adj_open'],row['adj_close'],row['close']))
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
        Returns a list of dictionaries that contain all of the valid stock data as keys
        or an empty list if no results are found
        Can be called independently or used as part of the getPrices function
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock or a list of tickers
        isTable: Using PyTables version (opposed to NumPy array version)
        '''
        #print "GSA ST ET TKER", startTime, endTime, ticker
        if endTime == None:
            endTime = self.currTimestamp
        if endTime > self.currTimestamp:
            print 'Tried to access a future time %i, endTime set to %i' %(endTime, self.currTimestamp)
            endTime = self.currTimestamp
        if ticker != None:
            if type(ticker)==str:
                tickIdxList = []
                tickerIdx = self.symbolIndex.searchsorted(ticker)
                if tickerIdx < self.symbolIndex.size and self.symbolIndex[tickerIdx] == ticker:
                    tickIdxList.append(tickerIdx)
            elif type(ticker)==list:
                for tick in tickerIdx:
                    tickerIdx = self.symbolIndex.searchsorted(ticker)
                    if tickerIdx < self.symbolIndex.size and self.symbolIndex[tickerIdx] == ticker:
                        tickIdxList.append(tickerIdx)
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
            #print "GSA with tkrIdx",startIdx, endIdx, tickerIdx, self.priceArray[startIdx:endIdx+1,tickerIdx][0]
            #print "priceArray[endIndex]: %d" % self.priceArray[endIdx][0]['timestamp']
            #print "priceArray[endIndex+1]: %d" % self.priceArray[endIdx+1][0]['timestamp']
            #print self.priceArray[startIdx:endIdx,tickerIdx]
            result = np.array([])
            for tickerIdx in tickIdxList:
                result = np.append(result,self.priceArray[startIdx:endIdx,tickerIdx])
            return result
        else:
            result = self.priceArray[startIdx:endIdx,:]
            #print 'GSA no tkrIdx',startIdx, endIdx, result
            if len(result) ==0:
                return []
            else:
                return result[0]
        
        
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
        Returns a list of prices for the given description: [adj_high0, adj_high1, adj_high2...]
        or a tuple if no description is given: [ (adj_high0, adj_low0, adj_open0, adj_close0, close0), (adj_high1, adj_low1...), .... ]
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock or a list of tickers
        description: the field from data that is desired IE. adj_high 
        description: 
        '''
        rows = self.getStocksArray(startTime, endTime, ticker)
        #print "first timestamp: %d" % rows[0]['timestamp']
        #print "last timestamp: %d" % rows[len(rows)-1]['timestamp']
        #print 'ROWS',rows
        result = []
        if(description==None):
            for row in rows:
                result.append((row['adj_high'],row['adj_low'],row['adj_open'],row['adj_close'],row['close']))
        else:
            for row in rows:
                #print 'ROW', row
                #print "Timestamps: %d" % row['timestamp']
                result.append(row[description])
        #print "\nDone...\n"
        return result 

    def close(self):
        self.strategyDataFile.close()

def generateKnownArray():
    timestamps = np.array([])
    stocks = np.array([])
    for i in range(10,100):
        timestamps = np.append(timestamps, i*86400)
    for i in range(3):
        stocks = np.append(stocks,'stock%i'%i)
    priceArray = np.ndarray(shape=(timestamps.size,stocks.size),dtype=np.object)
    for i in range(timestamps.size):
        for j in range(stocks.size):
            row = {}
            row['exchange'] = 'NYSE'
            row['symbol'] = stocks[j]
            row['adj_open'] = (timestamps[i]/86400)  * (j+1)
            row['adj_close'] = (timestamps[i]/86400)  * (j+1)
            row['adj_high'] = (timestamps[i]/86400)  * (j+1)
            row['adj_low'] = (timestamps[i]/86400)  * (j+1)
            row['close'] = (timestamps[i]/86400)  * (j+1)
            row['volume'] = 200
            row['timestamp'] = timestamps[i]
            row['when_available'] = timestamps[i]
            row['interval'] = 86400
            priceArray[i,j] = row
    return (timestamps, stocks, priceArray)
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
            if j ==0:
                #adjOpen = random.random() * random.randint(1,100)   
                #adjClose = random.random() * random.randint(1,100) 
                row['exchange'] = 'NYSE'
                row['symbol'] = stocks[j]
                row['adj_open'] = 10 
                row['adj_close'] = 20
                row['adj_high'] = 22
                row['adj_low'] = 7
                row['close'] = 20
                row['volume'] = 200
                row['timestamp'] = timestamps[i]
                row['when_available'] = timestamps[i]
                row['interval'] = 86400
            else:
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
    '''
    pickle_output = open('randomArrayFile.pkl','w')
    pickler = pickle.dump(timestamps,pickle_output)
    pickler = pickle.dump(stocks,pickle_output)
    pickler = pickle.dump(priceArray,pickle_output)
    pickle_output.close()
    '''
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