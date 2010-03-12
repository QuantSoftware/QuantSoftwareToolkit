import numpy
import tables as pt #@UnresolvedImport

class PositionModel(pt.IsDescription):
    timestamp = pt.Time32Col()
    symbol = pt.StringCol(4) 
    shares = pt.Int32Col()
    open_price = pt.Int32Col()
    
        
def classTest():        
    h5f = pt.openFile('PositionTest.h5', mode = "w")
    group = h5f.createGroup("/", 'tester')
    table = h5f.createTable(group, 'testTable', PositionModel)
    row = table.row
    for i in range(10):
        row['timestamp'] = 1000
        row['symbol'] = "KO"
        row['shares'] = 100
        row['open_price'] = 25
        row.append()
    h5f.close()
    
    h5f = pt.openFile('PositionTest.h5', mode = "r")
    table = h5f.root.tester.testTable
    for row in table.iterrows():
        print row['timestamp'], row['symbol'], row['shares'], row['open_price']  
    result = [ row['timestamp'] for row in table 
              if row['symbol'] == 'KO' and row['shares']==100 ] 
    print result
    #for row in table.where('(symbol=="%s"%ticker) and shares==100',ticker):
    #   print row['timestamp'],
    #note the where clause, the condition is in quotes
    h5f.close()
