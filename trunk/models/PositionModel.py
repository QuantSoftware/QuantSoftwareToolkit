import tables as pt #@UnresolvedImport
import numpy as np

class PositionModel(pt.IsDescription):
    timestamp = pt.Time64Col()
    symbol = pt.StringCol(30) 
    shares = pt.Int32Col()
    purchase_price = pt.Float32Col()
    closed = pt.Int32Col()
    
        
def classTest():        
    h5f = pt.openFile('PositionTest.h5', mode = "w")
    group = h5f.createGroup("/", 'tester')
    table = h5f.createTable(group, 'testTable', PositionModel)
    row = table.row
    for i in range(10):
        row['timestamp'] = 1000*i
        row['symbol'] = "KO%s"%i
        row['shares'] = 100
        row['purchase_price'] = 25
        row.append()
    table.flush()
    lst = []  
    for row in table.iterrows():
        dct = {}  
        print row
        dct['timestamp'] = row['timestamp']
        dct['symbol'] = row['symbol']
        dct['shares'] = row['shares']
        dct['purchase_price'] = row['purchase_price']
        lst.append(dct)        
    h5f.close()
    print lst
    print lst[0]['timestamp']
    
    h5f = pt.openFile('PositionTest.h5', mode = "r")
    table = h5f.root.tester.testTable
    #for row in table.iterrows():
    #    print row['timestamp'], row['symbol'], row['shares'], row['open_price']  
    #result = [ row['timestamp'] for row in table 
    #          if row['symbol'] == 'KO' and row['shares']==100 ] 
    #print result
    #for row in table.where('(symbol=="%s"%ticker) and shares==100',ticker):
    #   print row['timestamp'],
    #note the where clause, the condition is in quotes
    h5f.close()