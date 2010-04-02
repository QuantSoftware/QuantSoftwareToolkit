import tables as pt #@UnresolvedImport
import time

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
 

def generateDataFile():
    import random
    random.seed(1)    
    #86400 seconds in a day
    stocks = []
    for i in range(10): #stocks
        stocks.append('stock%i'%i)
    
    h5f = pt.openFile('PriceTestData.h5', mode = "w")
    group = h5f.createGroup("/", 'tester')
    table = h5f.createTable(group, 'testTable', StockPriceModel)
    row = table.row

    for i in range(100): #timestamps
        j = 0
        for stock in stocks:
            adjOpen = random.random() * random.randint(1,100)   
            adjClose = random.random() * random.randint(1,100) 
            row['exchange'] = 'NYSE'
            row['symbol'] = stock
            row['data/adj_open'] = adjOpen 
            row['data/adj_close'] = adjClose
            row['data/adj_high'] = max(adjOpen,adjClose) * random.randint(1,5)
            row['data/adj_low'] = min(adjOpen,adjClose) / random.randint(1,5)
            row['data/close'] = adjClose
            row['data/volume'] = random.randint(1000,10000)
            row['data/timestamp'] = i*86400
            row['data/when_available'] = i*86400
            row['data/interval'] = 86400         
            row.append()
            table.flush()
        if i%10==0:
            print i,
        if i%100==0:
            print ''
    h5f.close()
#generateDataFile()

def showData():
    h5f = pt.openFile('PriceTestData.h5', mode = "r")
    table = h5f.root.tester.testTable
    i = 0    
    for row in table.iterrows():
        if i<10:
            print row['data/adj_close']
        i+=1
        
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
    
    h5f.close()