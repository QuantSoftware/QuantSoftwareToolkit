import tables as pt
import numpy as np
from models.PositionModel import PositionModel

class Position:
    def __init__(self):
        self.position = np.array([])
    
    def getPositions(self):
        '''
        Returns all of the positions
        '''
        return self.position
    
    def addPosition(self,timestamp,symbol,shares,purchase_price):
        '''
        Adds a new position
        timestamp: the time the position was entered
        symbol: the ticker of the stock
        shares: the number of shares
        purchase_price: the price per share (excludes any additional costs such as commission or impact)
        '''
        row = {}
        row['timestamp'] = timestamp
        row['symbol'] = symbol 
        row['shares'] = shares
        row['purchase_price'] = purchase_price
        self.position = np.append(self.position, row)
    
    def removePosition(self, symbol, shares, closeType):
        '''
        Removes/modifies positions until the total number of shares have been removed
        symbol: the ticker of the stock
        shares: the number of shares to remove
        closeType: removal order "lifo" or "fifo"
        NOTE: Method assumes that verification of valid sell has already been completed
        '''
        debug = False
        
        rowIndexes = []
        rows = []
        #check for negative shares, short or not
        if shares<0:
            short = True
        else:
            short = False
        if debug:
            print 'REMOVING POSITIONS'
            print 'REMOVE:',symbol,shares,closeType
            for row in self.position:
                print 'CURRROWS:', row
        #get all rows for the correct stock
        idx = 0
        for row in self.position:
            if(row['symbol']==symbol):
                row["keyIndex"]=idx
                rows.append(row)
            idx+=1
        if debug:
            print 'POSSIBLE ROWS TO REMOVE: ',rows
        if(closeType=='fifo'):
            i = 0
            row = rows[i] #get first row
            if debug:
                print 'FIFO', row
            posShares = row['shares'] #get shares
            posShares = abs(posShares) #account for shorts (make positive) 
            #determines the number of positions to remove
            while(shares>posShares):
                shares-=posShares
                i+=1
                row = rows[i]
                posShares = row['shares']
                posShares = abs(posShares)
            #converts shorts back to negative
            if short:
                shares *= -1
                posShares *= -1
            #change shares in the last (changed) row
            newRow = self.position[ rows[i]['keyIndex'] ]
            newShares = posShares-shares
            newRow['shares'] = newShares
            if debug:
                print 'UPDATEDROW(FIFO):', newRow            
            #removes old rows
            removes = []
            #remove updated row if it has 0 shares now
            if newShares == 0:
                removes.append(rows[i]['keyIndex'])
            #remove the rest of the rows
            cnt = 0
            while cnt<i:
                row = rows[cnt]
                removes.append(row['keyIndex'])
                cnt+=1
            if debug:
                for idx in removes:
                    print 'ROWREMOVED:', self.position[idx]
            self.position = np.delete(self.position,removes)
            #remove the keyIndex field from the data
            for row in rows:
               del row['keyIndex'] 
               
                    
        elif(closeType=='lifo'):
            i = len(rows)-1 #sets i to last row
            row = rows[i]
            if debug:
                print "LIFO",row
            #gets info from last row's position
            posShares = row['shares']
            posShares = abs(posShares) #account for shorts (make positive) 
            #determines number of positions to remove     
            while(shares>posShares):
                shares-=posShares
                i-=1
                row = rows[i]
                posShares = row['shares']
                posShares = abs(posShares)
            #converts shorts back to negative
            if short:
                shares *= -1
                posShares *= -1 
            #modifies changed row             
            newRow = self.position[ rows[i]['keyIndex'] ]
            newShares = posShares-shares
            newRow['shares'] = newShares
            if debug:
                print 'UPDATEDROW(LIFO):', newRow            
            #removes old rows
            removes = []
            #remove updated row if it has 0 shares now
            if newShares == 0:
                removes.append(rows[i]['keyIndex'])
            #remove the rest of the rows
            cnt = len(rows)-1
            while cnt>i:
                row = rows[cnt]
                removes.append(row['keyIndex'])
                cnt-=1
            if debug:
                for idx in removes:
                    print 'ROWREMOVED:', self.position[idx]
            self.position = np.delete(self.position,removes)
            for row in rows:
               del row['keyIndex']
        else:
            #invalid type
            raise TypeError("Not an existing close type '%s'." % str(closeType))
    
    def fillTable(self):
        '''
        Converts the arrays into HDF5 tables for post simulation review
        '''
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

