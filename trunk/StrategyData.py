import models.StrategyDataModel, tables as pt, numpy as np
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
        if dataFile == None:
            self.strategyDataFile = pt.openFile('StrategyDataModel.h5', mode = "w")
            self.strategyData = self.strategyDataFile.createTable('/', 'strategyData', StrategyDataModel)
        else:
            self.strategyDataFile = pt.openFile(dataFile, mode = "r")
            self.strategyData = self.strategyDataFile.root.tester.testTable
        self.timestampsIndex = self.findTimestamps()
        self.stocksIndex = self.findStocks()   
        #self.pricesArray = self.populateArray()
        
    def populateArray(self):
        array = np.ndarray(len(self.timestampsIndex),len(self.stocksIndex),6)
        for stock in self.stocksIndex:
            pass
    
    def findTimestamps(self):
        temp = []
        for i in self.strategyData.iterrows():
            if i['data/timestamp'] not in temp:
                temp.append(i['data/timestamp'])
        temp.sort()
        return temp
        
    def findStocks(self):
        temp = []
        for i in self.strategyData.iterrows():
            if i['symbol'] not in temp:
                temp.append(i['symbol'])
        temp.sort()
        return temp
    
    def getStocks(self, startTime=None, endTime=None, ticker=None):
        '''
        Returns iterable pytables row objects based on the given parameters
        Can be called independantly or used as part of the getPrices function
        description: the field from data that is desired IE. adj_high
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
                        tempList.append(row)
                elif(startTime!=None):
                    if(row['data/timestamp']>=startTime):
                        tempList.append(row)
                elif(endTime!=None):
                    if(row['data/timestamp']<=endTime):
                        tempList.append(row)
                else: #no time given
                    tempList.append(row)    
        else:
            for row in self.strategyData.iterrows():
                if(startTime!=None and endTime!=None):
                    if(row['data/timestamp']>=startTime and row['data/timestamp']<=endTime):
                        tempList.append(row)
                elif(startTime!=None):
                    if(row['data/timestamp']>=startTime):
                        tempList.append(row)
                elif(endTime!=None):
                    if(row['data/timestamp']<=endTime):
                        tempList.append(row)
                else: #no time given
                    tempList.append(row)                    
        return tempList
    
    def getPrice(self, timestamp, ticker, description):
        '''
        table: the table that contains the stock data (stockPrice table from simulator usually)
        timestamp: the exact timestamp of the desired stock data
        ticker: the ticker/symbol of the stock
        description: the field from data that is desired IE. adj_high
        NOTE: If the data is incorrect or invalid, the function will return None    
        '''
        st='timestamp==%i'%timestamp
        st+=' and symbol==' +'"'+ticker+'"'
        try:
            row = self.strategyData.where(st)
            result = row['data/%s'%description]
        except:
            result = None
        return result
        
    def getPrices(self, startTime=None, endTime=None, ticker=None, description=None):
        '''
        Returns a list of prices for the given description or a tuple of prices if no description is given
        description: the field from data that is desired IE. adj_high
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock   
        '''
        rows = getStocks(startTime, endTime, ticker)
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
 

def methodTest():
    strat = StrategyData('models/PriceTestData.h5')
    print strat.getStocks(startTime=0, ticker='KO')
methodTest()
    
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