import tables as pt #@UnresolvedImport
import time
    
#I DON'T THINK THIS FILE IS NEEDED ANYMORE SHREYAS JOSHI 22 JUN 2010    
    
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
    date = pt.Int32Col()
    interval = pt.Time64Col()
    
    def __init__(selfparams):
        print "In the constructor"
    #constructor done

def generateDataFile():
    import random
    random.seed(1)    
    #86400 seconds in a day
    stocks = []
    for i in range(30): #stocks
        stocks.append('stock%.6i'%i)
    
    h5f = pt.openFile('defaultPytablesFile.h5', mode = "w")
    group = h5f.createGroup("/", 'StrategyData')
    table = h5f.createTable(group, 'StrategyData', StrategyDataModel)
    row = table.row

    for i in range(100): #timestamps
        j = 0
        for stock in stocks:
            adjOpen = random.random() * random.randint(1,100)   
            adjClose = random.random() * random.randint(1,100) 
            row['exchange'] = 'NYSE'
            row['symbol'] = stock
            row['adj_open'] = adjOpen 
            row['adj_close'] = adjClose
            row['adj_high'] = max(adjOpen,adjClose) * random.randint(1,5)
            row['adj_low'] = min(adjOpen,adjClose) / random.randint(1,5)
            row['close'] = adjClose
            row['volume'] = random.randint(1000,10000)
            row['timestamp'] = i*86400
            row['when_available'] = i*86400
            row['interval'] = 86400         
            row.append()
            table.flush()
        if i%10==0:
            print i,
        if i%100==0:
            print ''
    h5f.close()
#generateDataFile()
