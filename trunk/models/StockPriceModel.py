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
    exchange = pt.StringCol(10)         #10 char string; NYSE or NASDAQ
    timestamp = pt.Time64Col()         #timestamp of price
    when_available = pt.Time64Col()    #time when data is available to simulator
    interval = pt.Time64Col()          #interval since previous data point
    data = PriceData()                 #creates a nested table for PriceData (see above)
 
    
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