import numpy
import tables as pt #@UnresolvedImport
import time

class FillModel(pt.IsDescription):
    timestamp = pt.Time32Col()
    quantity = pt.Int32Col()
    price = pt.Float64Col()

class OrderModel(pt.IsDescription):
    shares = pt.Int32Col()
    symbol = pt.StringCol(4)
    order_type = pt.StringCol(5)       #moo moc limit vwap
    duration = pt.Time32Col()
    timestamp = pt.Time32Col()
    close_type = pt.StringCol(4)       #lifo or fifo
    fill = FillModel()
        
def classTest():        
    h5f = pt.openFile('StockPriceTest.h5', mode = "w")
    group = h5f.createGroup("/", 'tester')
    table = h5f.createTable(group, 'testTable', OrderModel)
    row = table.row
    for i in range(10):
        row['shares'] = 100
        row['symbol'] = 'NYSE'
        row['order_type'] = 'moo'
        row['duration'] = 1000
        row['timestamp'] = time.time()
        row['close_type'] = 'lifo'
        row.append()
    h5f.close()
    
    #reopen and access data file
    h5f = pt.openFile('StockPriceTest.h5', mode = "r")
    table = h5f.root.tester.testTable
    for row in table.iterrows():
        print row['shares'], row['symbol'], row['order_type'],\
        row['duration'], row['timestamp'], row['close_type']
    h5f.close()