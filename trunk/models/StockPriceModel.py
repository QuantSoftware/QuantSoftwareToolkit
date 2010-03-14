import tables as pt #@UnresolvedImport
import time

class PriceData(pt.IsDescription):
    adj_high = pt.Float32Col()
    adj_low = pt.Float32Col()
    adj_open = pt.Float32Col()
    adj_close = pt.Float32Col()
    close = pt.Float32Col()
    volume = pt.Int32Col()
    
class StockPriceModel(pt.IsDescription):
    symbol = pt.StringCol(4)           #4 char string; Ticker
    exchange = pt.StringCol(6)         #10 char string; NYSE or NASDAQ
    timestamp = pt.Time64Col()         #timestamp of price
    when_available = pt.Time64Col()    #time when data is available to simulator
    interval = pt.Time64Col()          #interval since previous data point
    data = PriceData()                 #creates a nested table for PriceData (see above)
    
    
def getStocks(table, startTime=None, endTime=None, ticker=None):
    '''
    Returns iterable pytables row objects based on the given parameters
    Can be called independantly or used as part of the getPrices function
    table: the table that contains the stock data (stockPrice table from simulator usually)
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
        result = table.iterrows()              
    else:
        #pytables throws an error if there are no results
        try:
            result = table.where(str)
        except: 
            result = []
    return result

def getPrice(table, timestamp, ticker, description):
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
        row = table.where(str)
        result = row['data/%s'%description]
    except:
        result = None
    return result
    
def getPrices(table, startTime=None, endTime=None, ticker=None, description=None):
    '''
    Returns a list of prices for the given description or a tuple of prices if no description is given
    table: the table that contains the stock data (stockPrice table from simulator usually)
    description: the field from data that is desired IE. adj_high
    startTime: checks stocks >= startTime
    endTime: checks stocks <= endTime
    ticker: the ticker/symbol of the stock   
    '''
    rows = getStocks(table,startTime, endTime, ticker)
    result = []
    if(description==None):
        for row in rows:
            result.append(row['data'])
    else:
        for row in rows:
            result.append(row['data/%s'%description])
    return result
    
def classTest():        
    #populate data file
    h5f = pt.openFile('StockPriceTest.h5', mode = "w")
    group = h5f.createGroup("/", 'tester')
    table = h5f.createTable(group, 'testTable', StockPriceModel)
    row = table.row
    for i in range(10):
        if(i<2):
            row['symbol'] = 'KO'
        else:
            row['symbol'] = 'AAPL'
        row['exchange'] = 'NYSE'
        row['timestamp'] = 1000+i*10
        row['when_available'] = 1100+i*10
        row['interval'] = 1000+i*10
        row['data/adj_high'] = 25.32
            
        row.append()
    h5f.close()
    
    #reopen and access data file
    h5f = pt.openFile('StockPriceTest.h5', mode = "r")
    table = h5f.root.tester.testTable
        
    #for row in table.iterrows():
    #    print row['timestamp'], row['symbol'], row['exchange'],\
    #    row['timestamp'], row['when_available'], row['interval'], row['data']
    
    #rows = getStocks(table,ticker = 'KO')
    #rows = getStocks(table, 1020, 1050)
    #for row in rows:
    #    print row['symbol'], row['exchange'], row['timestamp'],\
    #        row['when_available'], row['interval'], row['data']
    
    price = getPrice(table, 'adj_high', 1020, 'KO')
    print price
    #prices = getPrices(table,'adj_high',ticker='KO')
    #print prices
    
    h5f.close()