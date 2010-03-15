import models.StockPriceModel, tables as pt

'''
Based on the model:
PriceData:
    adj_high = pt.Float32Col()
    adj_low = pt.Float32Col()
    adj_open = pt.Float32Col()
    adj_close = pt.Float32Col()
    close = pt.Float32Col()
    volume = pt.Int32Col()
    
StockPriceModel:
    symbol = pt.StringCol(4)           #4 char string; Ticker
    exchange = pt.StringCol(10)         #10 char string; NYSE or NASDAQ
    timestamp = pt.Time64Col()         #timestamp of price
    when_available = pt.Time64Col()    #time when data is available to simulator
    interval = pt.Time64Col()          #interval since previous data point
    data = PriceData()     
'''

class StockPrice:
    def __init__(self,dataFile = None):
        if dataFile == None:
            self.stockPriceFile = pt.openFile('StockPriceModel.h5', mode = "w")
            self.stockPrice = stockPriceFile.createTable('/', 'stockPrice', StockPriceModel)
        else:
            self.stockPriceFile = dataFile

    
    def getStocks(self, startTime=None, endTime=None, ticker=None):
        '''
        Returns iterable pytables row objects based on the given parameters
        Can be called independantly or used as part of the getPrices function
        description: the field from data that is desired IE. adj_high
        startTime: checks stocks >= startTime
        endTime: checks stocks <= endTime
        ticker: the ticker/symbol of the stock   
        '''
        str = ''
        if(startTime!=None):
            str+='timestamp>=%i'%startTime
        if(endTime!=None):
            if(str!= ''):
                str+=' and timestamp<=%i'%endTime
            else:
                str+='timestamp<=%i'%endTime
        if(ticker!=None):          
            if(str!= ''):
                str+=' and symbol==' +'"'+ticker+'"'
            else:
                str+='symbol==' +'"'+ticker+'"'
        if(str == ''):
            result = self.stockPrice.iterrows()              
        else:
            #pytables throws an error if there are no results
            try:
                result = self.stockPrice.where(str)
            except: 
                result = []
        return result
    
    def getPrice(self, timestamp, ticker, description):
        '''
        table: the table that contains the stock data (stockPrice table from simulator usually)
        timestamp: the exact timestamp of the desired stock data
        ticker: the ticker/symbol of the stock
        description: the field from data that is desired IE. adj_high
        NOTE: If the data is incorrect or invalid, the function will return None    
        '''
        str='timestamp==%i'%timestamp
        str+=' and symbol==' +'"'+ticker+'"'
        try:
            row = self.stockPricewhere(str)
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
        self.stockPriceFile.close()
 
    
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