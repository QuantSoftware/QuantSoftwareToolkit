import numpy
import tables as pt #@UnresolvedImport
import PositionModel as Position

class PortfolioModel(pt.IsDescription):
	cash = pt.Int32Col()
	positions = Position.PositionModel()    #creates a nested table of positions

        

def classTest():        
    h5f = pt.openFile('PortfolioTest.h5', mode = "w")
    group = h5f.createGroup("/", 'tester')
    table = h5f.createTable(group, 'testTable', PortfolioModel)
    row = table.row
    for i in range(10):
        row['cash'] = 1000
        row['positions/timestamp'] = 10510
        row['positions/symbol'] = "KO"
        row['positions/shares'] = 100
        row['positions/open_price'] = 25
        row.append()
    h5f.close()
    
    #reopen and access data file
    h5f = pt.openFile('PortfolioTest.h5', mode = "r")
    table = h5f.root.tester.testTable
    for row in table.iterrows():
    	print row['cash'], row['positions'] 
        print row['positions/symbol'] #note the way to access an item in the nested table
    print table[:] #note, alternate way to print
    h5f.close()