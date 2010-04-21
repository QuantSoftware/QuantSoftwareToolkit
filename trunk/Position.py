import tables as pt, numpy as np
from models.PositionModel import PositionModel
'''
Based on the model:
PositionModel:
    timestamp = pt.Time64Col()
    symbol = pt.StringCol(4) 
    shares = pt.Int32Col()
    purchase_price = pt.Int32Col()
    closed = pt.Int32Col()
'''

class Position:
    def __init__(self, isTable = False):
        self.isTable = isTable
        self.positionFile = pt.openFile('PositionModel.h5', mode = "w")
        self.position = self.positionFile.createTable('/', 'position', PositionModel)
        if isTable == False:
            self.positionArray = np.array([])
    
    def getPositions(self, isTable = False):
        output = []
        for row in self.position.iterrows():
            output.append(self.cloneRow(row))
        return output
    
    def addPosition(self,timestamp,symbol,shares,purchase_price,isTable = False):
        '''
        Adds a position to the current list of positions
        '''
        if isTable:
            row = self.position.row
            row['timestamp'] = timestamp
            row['symbol'] = symbol 
            row['shares'] = shares
            row['purchase_price'] = purchase_price
            row.append()
            self.position.flush()
        else:
            self.addPositionArray(timestamp,symbol,shares,purchase_price)
    
    def removePosition(self, symbol, shares, closeType, isTable = False):
        '''
        symbol: the representation of the shares to be removed
        shares: the number of shares to remove
        closeType: removal order "lifo" or "fifo"
        Removes/modifies positions until the total number of shares have been removed
        NOTE: Method assumes that verification of valid sell has already been completed
        '''
        #print "RP:", shares
        if isTable:
            short = False
            if shares<0:
                short = True
            shares = abs(shares)
            rowIndexes = []
            rows = []
            debug = False
            if debug:
                print 'REMOVING POSITIONS'
                print 'REMOVE:',symbol,shares,closeType
                for row in self.position.iterrows():
                    print 'CURRROWS:', row
            for row in self.position.where("symbol=='%s'"%symbol):
                if debug:
                    print 'SELEROWS:', row  
                rows.append(self.cloneRow(row))
                rowIndexes.append(row.nrow)
            if(closeType=='fifo'):
                i = 0
                row = rows[i]
                if debug:
                    print 'FIFO', row
                posShares = row['shares']
                posShares = abs(posShares)  
                #print "RP pos:", posShares          
                while(shares>posShares):
                    shares-=posShares
                    i+=1
                    row = rows[i]
                    posShares = row['shares']
                    posShares = abs(posShares)  
                cnt=0
                while cnt<i:                
                    for row in self.position.iterrows(rowIndexes[cnt]-cnt,rowIndexes[cnt]-cnt+1):
                        row['closed'] = 1
                        row.update()
                    self.position.flush()
                    cnt+=1
                    if debug:
                        print 'ROWCLOSED', row
                cnt=0
                if short:
                    shares *= -1
                    posShares *= -1
                for newRow in self.position.where('(symbol=="%s") & (timestamp==%i)'%(symbol,row['timestamp'])):
                    if(cnt==0):
                        newShares = posShares-shares
                        newRow['shares'] = newShares
                        newRow.update()
                        if debug:
                            print 'UPDATEDROW(FIFO):', newRow
                    cnt+=1
                self.position.flush()
                    
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
                cnt=0
                i+=1
                while i<len(rows):
                    for row in self.position.removeRows(rowIndexes[i]-cnt,rowIndexes[i]-cnt+1):
                        row['closed'] = 1
                        row.update()
                    self.position.flush()
                    i+=1
                    cnt+=1
                    if debug:
                        print 'ROWREMOVED', row
                cnt=0
                if short:
                    shares *= -1
                    posShares *= -1
                for newRow in self.position.where('(symbol=="%s") & (timestamp==%i)'%(symbol,row['timestamp'])):
                    if(cnt==0):
                        newShares = posShares-shares
                        newRow['shares'] = newShares
                        newRow.update()
                        if debug:
                            print 'UPDATEDROW(LIFO):', newRow
                    cnt+=1
                self.position.flush()
            else:
                #invalid type
                raise TypeError("Not an existing close type '%s'." % str(closeType))
        else:
            self.removePositionArray(symbol, shares, closeType)
       
    def cloneRow(self,row):
        ''' 
        Makes a copy of the row so that the correct information will be appended to the list
        '''
        dct = {}  
        dct['symbol'] = row['symbol']
        dct['shares'] = row['shares']
        dct['timestamp'] = row['timestamp']
        dct['purchase_price'] = row['purchase_price']
        return dct   
            
    def addPositionArray(self,timestamp,symbol,shares,purchase_price):
        row = {}
        row['timestamp'] = timestamp
        row['symbol'] = symbol 
        row['shares'] = shares
        row['purchase_price'] = purchase_price
        np.append(self.positionArray, row)
    
    def removePositionArray(self, symbol, shares, closeType):
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
            for row in self.positionArray:
                print 'CURRROWS:', row
        rows = self.positionArray
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
                rows[cnt]['closed']=1
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
                rows[cnt]['closed']=1
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
        for arrRow in self.positionArray:
            row = self.position.row
            row['timestamp'] = arrRow['timestamp']
            row['symbol'] = arrRow['symbol'] 
            row['shares'] = arrRow['shares']
            row['purchase_price'] = arrRow['purchase_price']
            row.append()
        self.position.flush() 
    
    def close(self, isTable = False):
        if isTable:
            self.positionFile.close()
        else:
            self.fillTable()
            self.positionFile.close()
