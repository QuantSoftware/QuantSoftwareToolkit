import tables as pt, numpy as np, pickle
from models.StrategyDataModel import StrategyDataModel
import numpy as np
            
class StrategyData: 
    def __init__(self,dataFile, dataAccess, isTable = False):
        '''
        @param dataFile: The filename of the data file (array or pytables)
        @param isTable: The runtype, true for table false for array
        @param dataAcess: is a DataAccess object that is used to access the stockData 
        '''
        #for pytables
        self.isTable = isTable
        self.currTimestamp = 0
        self.dataAccess=dataAccess
        if(isTable):
            isTable #do nothing.. just so that I don't have to remove the if/else
#            self.strategyDataFile = pt.openFile(dataFile, mode = "r")
#            self.strategyData = self.strategyDataFile.root.StrategyData.StrategyData
#            self.timestampIndex = None
#            self.stocksIndex = self.findStocks()
        else:
            self.prevTsIdx = 0
            f = open(dataFile,'r')
            ts = pickle.load(f)
            st = pickle.load(f)
            pA = pickle.load(f)
            f.close()
            self.symbolIndex = st
            self.timestampIndex = ts
            self.priceArray = pA
                    
    def findStocks(self):
        '''
        @summary: Populates the symbolIndex for table run
        '''
        temp = []
        for i in self.strategyData.iterrows():
            if i['symbol'] not in temp:
                temp.append(self.cloneRow(i)['symbol'])
        temp.sort()
        return temp
    
    def calculatePortValue(self,stocks,timestamp):
        '''
        @param stocks: the current stocks you hold as represented by currStocks in portfolio
        @param timestamp: the timestamp used to calculate the present value of stocks
        @summary: Calculates the current portfolio value: cash + stocks. If the value of a stock on a particular day is NaN then it keeps going back in time (upto 20 days) to find the first nonNan stock value. If a non NaN value is not found then the value of the portfolio is NaN
        
        '''
        
        total=0
        DAY=86400
        for stock in stocks:
            priceOfStock= self.dataAccess.getStockDataItem (stock, 'adj_close', timestamp- DAY) #close of previous day
            if not(np.isnan(priceOfStock)):
                total+= priceOfStock
            else:
                
                #Keep looking back in time till we get a non NaN closing value
                ctr=2
                while (np.isnan(priceOfStock) and ctr < 20):
                    priceOfStock= self.dataAccess.getStockDataItem (stock, 'adj_close', timestamp- (ctr*DAY))
                    ctr+=1
                    
                if np.isnan(priceOfStock):
                    return np.NaN
                     
                total+= priceOfStock
        
        return total            
                     
        
        
#        total = 0
#        for stock in stocks:
#            prices = self.dataAccess.getStockDataList(stock, 'adj_close', timestamp- 86400, timestamp)  #self.getPrices(timestamp - 86400, timestamp, stock, 'adj_close')
#            i = 86400
#            count = 0
#            while(len(prices)==0 and count<10):
#                prices = self.dataAccess.getStockDataList(stock, 'adj_close',timestamp - i - 86400, timestamp - i) #self.getPrices(timestamp - i, timestamp - i - 86400, stock, 'adj_close')
#                i += 86400
#                count+=1
#            if(len(prices) != 0):
#                total += prices[len(prices)-1] * stocks[stock]
#        return total
        #calculatePortValue
#    def getStocks(self, startTime=None, endTime=None, ticker=None):
#        '''
#        Returns a list of dictionaries that contain all of the valid stock data as keys
#        or an empty list if no results are found
#        Can be called independently or used as part of the getPrices function
#        startTime: checks stocks >= startTime
#        endTime: checks stocks <= endTime
#        ticker: the ticker/symbol of the stock or a list of tickers
#        '''
#        if self.isTable:
#            if endTime == None:
#                endTime = self.currTimestamp
#            if endTime > self.currTimestamp:
#                print 'Tried to access a future time %i, endTime set to %i' %(endTime, self.currTimestamp)
#                endTime = self.currTimestamp
#            tempList = []
#            if(ticker!=None):    
#                if(type(ticker)==str):
#                    for row in self.strategyData.where('symbol=="%s"'%ticker):
#                        if(startTime!=None and endTime!=None):
#                            if(row['timestamp']>=startTime and row['timestamp']<endTime):
#                                tempList.append(self.cloneRow(row))
#                        elif(startTime!=None):
#                            if(row['timestamp']>=startTime and row['timestamp']<self.currTimestamp):
#                                tempList.append(self.cloneRow(row))
#                        elif(endTime!=None):
#                            if(row['timestamp']<endTime):
#                                tempList.append(self.cloneRow(row))
#                        else: #no time given
#                            tempList.append(self.cloneRow(row))
#                elif(type(ticker)==list):
#                    for tick in ticker:
#                        for row in self.strategyData.where('symbol=="%s"'%tick):
#                            if(startTime!=None and endTime!=None):
#                                if(row['timestamp']>=startTime and row['timestamp']<endTime):
#                                    tempList.append(self.cloneRow(row))
#                            elif(startTime!=None):
#                                if(row['timestamp']>=startTime and row['timestamp']<self.currTimestamp):
#                                    tempList.append(self.cloneRow(row))
#                            elif(endTime!=None):
#                                if(row['timestamp']<endTime):
#                                    tempList.append(self.cloneRow(row))
#                            else: #no time given
#                                tempList.append(self.cloneRow(row))
#                     
#            else:
#                for row in self.strategyData.iterrows():
#                    if(startTime!=None and endTime!=None):
#                        if(row['timestamp']>=startTime and row['timestamp']<endTime):
#                            tempList.append(self.cloneRow(row))
#                    elif(startTime!=None):
#                        if(row['timestamp']>=startTime and row['timestamp']<self.currTimestamp):
#                            tempList.append(self.cloneRow(row))
#                    elif(endTime!=None):
#                        if(row['timestamp']<endTime):
#                            tempList.append(self.cloneRow(row))
#                    else: #no time given
#                        tempList.append(self.cloneRow(row))                    
#            return tempList
#        else:
#            return self.getStocksArray(startTime, endTime, ticker)
    
#    def getPrice(self, timestamp, ticker, description):
#        '''
#        Returns a single price based on the parameters
#        timestamp: the exact timestamp of the desired stock data
#        ticker: the ticker/symbol of the stock
#        description: the field from data that is desired IE. adj_high
#        NOTE: If the data is incorrect or invalid, the function will return None  
#        '''
#        if self.isTable:
#            result = None
#            for row in self.strategyData.where('symbol=="%s"'%ticker):
#                if row['timestamp']==timestamp:
#                    result = row[description]
#            return result
#        else:
#            return self.getPriceArray(timestamp, ticker, description)
        
#    def getPrices(self, startTime=None, endTime=None, ticker=None, description=None):
#        '''
#        Returns a list of prices for the given description: [adj_high1, adj_high2, adj_high3...]
#        or a tuple if no description is given: [ (adj_high1, adj_low1, adj_open1, adj_close1, close1), (adj_high2, adj_low2...), .... ]
#        startTime: checks stocks >= startTime
#        endTime: checks stocks <= endTime
#        ticker: the ticker/symbol of the stock or a list of tickers
#        description: the field from data that is desired IE. adj_high
#        '''
#        if self.isTable:
#            rows = self.getStocks(startTime, endTime, ticker)
#            result = []
#            if(description==None):
#                for row in rows:
#                    row = self.cloneRow(row)
#                    result.append((row['adj_high'],row['adj_low'],row['adj_open'],row['adj_close'],row['close']))
#            else:
#                for row in rows:
#                    result.append(self.cloneRow(row)[description])
#            return result
#        else:
#            return self.getPricesArray(startTime, endTime, ticker, description)
    
    def cloneRow(self,row):
        ''' 
        @summary: Makes a copy of the row so that the correct information will be appended to the list
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
        dct['date'] = row['date']
        dct['interval'] = row['interval']            
        return dct
 
#    def getStocksArray(self, startTime=None, endTime=None, ticker=None):
#        '''
#        Returns a list of dictionaries that contain all of the valid stock data as keys
#        or an empty list if no results are found
#        Can be called independently or used as part of the getPrices function
#        startTime: checks stocks >= startTime
#        endTime: checks stocks <= endTime
#        ticker: the ticker/symbol of the stock or a list of tickers
#        '''
#        if endTime == None:
#            endTime = self.currTimestamp
#        if endTime > self.currTimestamp:
#            print 'Tried to access a future time %i, endTime set to %i' %(endTime, self.currTimestamp)
#            endTime = self.currTimestamp
#        if ticker != None:
#            if type(ticker)==str:
#                tickIdxList = []
#                tickerIdx = self.symbolIndex.searchsorted(ticker)
#                if tickerIdx < self.symbolIndex.size and self.symbolIndex[tickerIdx] == ticker:
#                    tickIdxList.append(tickerIdx)
#            elif type(ticker)==list:
#                for tick in tickerIdx:
#                    tickerIdx = self.symbolIndex.searchsorted(ticker)
#                    if tickerIdx < self.symbolIndex.size and self.symbolIndex[tickerIdx] == ticker:
#                        tickIdxList.append(tickerIdx)
#        else:
#            tickerIdx = None      
#        if startTime != None:
#            startIdx = self.timestampIndex.searchsorted(startTime, 'left')
#        else:
#            startIdx = None
#        if endTime != None:
#            endIdx = self.timestampIndex.searchsorted(endTime, 'left')
#        else:
#            endIdx = None  
#        if tickerIdx != None:
#            result = np.array([])
#            for tickerIdx in tickIdxList:
#                result = np.append(result,self.priceArray[startIdx:endIdx,tickerIdx])
#            return result
#        else:
#            result = self.priceArray[startIdx:endIdx,:]
#            if len(result) ==0:
#                return []
#            else:
#                return result[0]
        
        
#    def getPriceArray(self, timestamp, ticker, description):
#        '''
#        timestamp: the exact timestamp of the desired stock data
#        ticker: the ticker/symbol of the stock
#        description: the field from data that is desired IE. adj_high
#        NOTE: If the data is incorrect or invalid, the function will return None  
#        '''
#        tsIdx = self.timestampIndex.searchsorted(timestamp)
#        if tsIdx >= self.timestampIndex.size or self.timestampIndex[tsIdx] != timestamp:
#            return None #NaN  
#        tickerIdx = self.symbolIndex.searchsorted(ticker)
#        if tickerIdx >= self.symbolIndex.size or self.symbolIndex[tickerIdx] != ticker:
#            return None #NaN
#        return self.priceArray[tsIdx,tickerIdx][description]
 
#    def getPricesArray(self, startTime=None, endTime=None, ticker=None, description=None):
#        '''
#        Returns a list of prices for the given description: [adj_high0, adj_high1, adj_high2...]
#        or a tuple if no description is given: [ (adj_high0, adj_low0, adj_open0, adj_close0, close0), (adj_high1, adj_low1...), .... ]
#        startTime: checks stocks >= startTime
#        endTime: checks stocks <= endTime
#        ticker: the ticker/symbol of the stock or a list of tickers
#        description: the field from data that is desired IE. adj_high 
#        description: 
#        '''
#        rows = self.getStocksArray(startTime, endTime, ticker)
#        result = []
#        if(description==None):
#            for row in rows:
#                result.append((row['adj_high'],row['adj_low'],row['adj_open'],row['adj_close'],row['close']))
#        else:
#            for row in rows:
#                result.append(row[description])
#        return result 

    def close(self):
        if self.isTable:
            self.isTable
#            self.strategyDataFile.close()
           
    class OutputOrder:
        '''
        @summary: Subclass to make adding strategies easier
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
            if self.symbol == "" or type(self.symbol) != str:
                print "Invalid symbol %s in output." % str(self.symbol)
                return None
            if self.volume == 0 or type(self.volume) != int:
                print "Invalid volume %s in output." % str(self.volume)
                return None
            if self.task == "" or type(self.task) != str:
                print "Invalid task %s in output." % str(self.task)
                return None
            if self.duration <= 0 or type(self.duration) != int:
                print "Invalid duration %s in output." % str(self.duration)
                return None
            if self.orderType == "" or type(self.orderType) != str:
                print "Invalid orderType %s in output." % str(self.orderType)
                return None
            if type(self.task) != str:
                print "Invalid closeType %s specified." % str(self.task)
                return None
            if self.task.upper() == "SELL" or self.task.upper() == "COVER":
                if self.closeType == "" or type(self.closeType) != str:
                    print "Invalid closeType %s specified for %s." % (str(self.closeType),self.task)
                    return None
            if type(self.orderType) != str:
                print "Invalid orderType %s specified." % str(self.orderType)
            if self.orderType.upper() == "LIMIT":
                if self.limitPrice == 0 or type(self.limitPrice) != int:
                    print "Invalid limitPrice specified."
                    return None
            if self.task.upper() not in ["BUY","SELL","SHORT","COVER"]:
                print "Invalid task %s specified." %self.task
                return None
            if self.orderType.upper() not in ["LIMIT","MOC","MOO","VWAP"]:
                print "Invalid orderType %s specified." % self.orderType
                return None
            return (self.task,self.volume,self.symbol,self.orderType,self.duration,self.closeType,self.limitPrice)
        
        #END OutputOrder SUBLCLASS
        

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