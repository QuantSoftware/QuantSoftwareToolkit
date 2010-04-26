import tables as pt, numpy as np
from models.PositionModel import PositionModel
'''
Based on the model:
PositionModel:
    timestamp = pt.Time64Col()
    symbol = pt.StringCol(4) 
    shares = pt.Int32Col()
    purchase_price = pt.Int32Col()
'''

class Position:
    def __init__(self):
        self.position = np.array([])
    
    def getPositions(self):
        output = []
        self.position
    
    def addPosition(self,timestamp,symbol,shares,purchase_price):
        row = {}
        row['timestamp'] = timestamp
        row['symbol'] = symbol 
        row['shares'] = shares
        row['purchase_price'] = purchase_price
        self.position = np.append(self.position, row)
    
    def removePosition(self, symbol, shares, closeType):
        '''
        symbol: the representation of the shares to be removed
        shares: the number of shares to remove
        closeType: removal order "lifo" or "fifo"
        Removes/modifies positions until the total number of shares have been removed
        NOTE: Method assumes that verification of valid sell has already been completed
        '''
        rowIndexes = []
        rows = []
        debug = False
        short = False
        if shares<0:
            short = True
        if debug:
            print 'REMOVING POSITIONS'
            print 'REMOVE:',symbol,shares,closeType
            for row in self.position:
                print 'CURRROWS:', row
        rows = self.position
        if(closeType=='fifo'):
            i = 0
            row = rows[i]
            if debug:
                print 'FIFO', row
            posShares = row['shares']
            posShares = abs(posShares)            
            while(shares>posShares):
                shares-=posShares
                i+=1
                row = rows[i]
                posShares = row['shares']
                posShares = abs(posShares)
            cnt=0
            while cnt<i:                
                cnt+=1
                if debug:
                    print 'ROWCLOSED', rows[cnt]
            if short:
                shares *= -1
                posShares *= -1
            newRow = rows[i]
            newShares = posShares-shares
            newRow['shares'] = newShares
            if debug:
                print 'UPDATEDROW(FIFO):', newRow
                
        elif(closeType=='lifo'):
            i = len(rows)-1
            row = rows[i]
            if debug:
                print "LIFO",row
            posShares = row['shares']
            posShares = abs(posShares)        
            while(shares>posShares):
                shares-=posShares
                i-=1
                row = rows[i]
                posShares = row['shares']
                posShares = abs(posShares)
            cnt=i+1
            while cnt<len(rows):
                cnt+=1
                if debug:
                    print 'ROWREMOVED', row 
            if short:
                shares *= -1
                posShares *= -1              
            newRow = rows[i]
            newShares = posShares-shares
            newRow['shares'] = newShares
            if debug:
                print 'UPDATEDROW(FIFO):', newRow
        else:
            #invalid type
            raise TypeError("Not an existing close type '%s'." % str(newOrder.order_type))
    
    def fillTable(self):   
        self.positionFile = pt.openFile('PositionModel.h5', mode = "w")
        self.position = self.positionFile.createTable('/', 'position', PositionModel)     
        for arrRow in self.position:
            row = self.position.row
            row['timestamp'] = arrRow['timestamp']
            row['symbol'] = arrRow['symbol'] 
            row['shares'] = arrRow['shares']
            row['purchase_price'] = arrRow['purchase_price']
            row.append()
        self.position.flush() 
        self.positionFile.close()
    
    def close(self):
        self.fillTable()

