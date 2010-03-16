import models.PositionModel, tables as pt

'''
Based on the model:
PositionModel:
    timestamp = pt.Time64Col()
    symbol = pt.StringCol(4) 
    shares = pt.Int32Col()
    open_price = pt.Int32Col()
'''

class Position:
    def __init__(self):
        self.positionFile = pt.openFile('PositionModel.h5', mode = "w")
        self.position = positionFile.createTable('/', 'position', PositionModel)

    def addPosition(self,timestamp,symbol,shares,open_price):
        row = self.position.row
        row['timestamp'] = timestamp
        row['symbol'] = symbol 
        row['shares'] = shares
        row['open_price'] = open_price
        row.append()     
    
    def close(self):
        self.positionFile.close()
