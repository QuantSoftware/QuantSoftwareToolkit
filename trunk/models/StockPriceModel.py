import numpy as np
import tables as pt #@UnresolvedImport
import time

class PriceData(pt.IsDescription):
    adj_high = pt.Float64Col()
    adj_low = pt.Float64Col()
    adj_open = pt.Float64Col()
    adj_close = pt.Float64Col()
    close = pt.Float64Col()
    volume = pt.Float64Col()
    
class StockPriceModel(pt.IsDescription):
    symbol = pt.StringCol(4)           #4 char string; Ticker
    exchange = pt.StringCol(6)         #10 char string; NYSE or NASDAQ
    timestamp = pt.Time32Col()            #timestamp of price
    when_available = pt.Time32Col()    #time when data is available to simulator
    interval = pt.Time32Col()          #interval since previous data point
    data = PriceData()                 #creates a nested table for PriceData (see above)
    

    
        
def classTest():        
    #populate data file
    h5f = pt.openFile('StockPriceTest.h5', mode = "w")
    group = h5f.createGroup("/", 'tester')
    table = h5f.createTable(group, 'testTable', StockPriceModel)
    row = table.row
    for i in range(10):
        row['symbol'] = 'AAPL'
        row['exchange'] = 'NYSE'
        row['timestamp'] = time.time()
        row['when_available'] = time.time()+100
        row['interval'] = time.time()+450
        row['data/adj_high'] = 25.32
            
        row.append()
    h5f.close()
    
    #reopen and access data file
    h5f = pt.openFile('StockPriceTest.h5', mode = "r")
    table = h5f.root.tester.testTable
    for row in table.iterrows():
        print row['timestamp'], row['symbol'], row['exchange'],\
        row['timestamp'], row['when_available'], row['interval'], row['data']
    h5f.close()
