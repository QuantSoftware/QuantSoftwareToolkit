import tables as pt, numpy as np
from models.OrderModel import OrderModel

class Order:
    def __init__(self, isTable):
        self.isTable = isTable
        self.orderFile = pt.openFile('OrderModel.h5', mode = "w")
        self.order = self.orderFile.createTable('/', 'order', OrderModel)
        if isTable == False:
            self.orderArray = np.array([])
    
    def addOrder(self,timestamp,task,shares,symbol,orderType,duration,closeType,limitPrice): 
        ''' 
        @param timestamp: the exact timestamp when the order was submitted
        @param task: buy, sell, short, cover
        @param shares: the number of shares to trade
        @param symbol: the symbol abbreviation of the stock
        @param orderType: they type of order (moo, moc, limit, vwap)
        @param duration: the length of time the order is valid for
        @param closeType: sell first or sell last (lifo,fifo)
        
        @summary: adds a new unfulfilled order to the orders table
        @returns a reference to the row
        '''  
        if self.isTable:
            row = self.order.row
            row['task'] = task
            row['shares'] = shares
            row['symbol'] = symbol
            row['order_type'] = orderType
            row['duration'] = duration
            row['timestamp'] = timestamp
            row['close_type'] = closeType
            row['limit_price'] = limitPrice
            return row
        else:
            return self.addOrderArray(timestamp,task,shares,symbol,orderType,duration,closeType,limitPrice = 0)
        
    def fillOrder(self, timestamp, rowIterator, quantity, price, commission, impactCost):
        ''' 
        @param timestamp: the exact timestamp when the order was fufilled
        @param rowIterator: a pytables iteratable rows object with 1 row, the row to be filled in it
        @param quantity: the number of shares successfully traded
        @param price: the purchase price per share

        @warning: CURRENTLY DONE IN THE SIMULATOR BUY/SELL METHODS THIS METHOD CURRENTLY WILL NOT FUCTION IF USED
        @summary: adds a fill to a given order
        '''  
        for row in rowIterator:
            row['fill/timestamp'] = timestamp
            row['fill/quantity'] = quantity
            row['fill/cashChange'] = price
            row['fill/commission'] = commission
            row['fill/impactCost'] = impactCost
            row.update()
    
    def getOrders(self):
        '''
        @return: Returns all of the orders
        '''
        if self.isTable:
            return self.order.iterrows()
        else:
            return self.orderArray
        
    def addOrderArray(self,timestamp,task,shares,symbol,orderType,duration,closeType,limitPrice):  
        ''' 
        @param timestamp: the exact timestamp when the order was submitted
        @param task: buy, sell, short, cover
        @param shares: the number of shares to trade
        @param symbol: the symbol abbreviation of the stock
        @param orderType: they type of order (moo, moc, limit, vwap)
        @param duration: the length of time the order is valid for
        @param closeType: sell first or sell last (lifo,fifo)
        
        @summary: adds a new unfulfilled order to the orders table and returns the order
        '''  
        row = {}
        row['task'] = task
        row['shares'] = shares
        row['symbol'] = symbol
        row['order_type'] = orderType
        row['duration'] = duration
        row['timestamp'] = timestamp
        row['close_type'] = closeType
        row['limit_price'] = limitPrice
        row['fill/timestamp'] = 0
        row['fill/quantity'] = 0
        row['fill/cashChange'] = 0
        row['fill/commission'] = 0
        row['fill/impactCost'] = 0
        self.orderArray = np.append(self.orderArray,row)
        return row
      
    def fillOrderArray(self, timestamp, row, quantity, price, commission, impactCost):
        '''
        @summary: CURRENTLY DONE IN THE SIMULATOR BUY/SELL METHODS. adds a fill to a given order
        @param timestamp: the exact timestamp when the order was fufilled
        @param row: the dictionary representing the row
        @param quantity: the number of shares successfully traded
        @param price: the purchase price per share
        '''  
        row['fill/timestamp'] = timestamp
        row['fill/quantity'] = quantity
        row['fill/cashChange'] = price
        row['fill/commission'] = commission
        row['fill/impactCost'] = impactCost
        
    def fillTable(self):
        '''
        @summary: converts all orders to HDF5 and outputs the file
        '''
        for arrRow in self.orderArray:
            row = self.order.row
            row['task'] = arrRow['task']
            row['shares'] = arrRow['shares']
            row['symbol'] = arrRow['symbol']
            row['order_type'] = arrRow['order_type']
            row['duration'] = arrRow['duration']
            row['timestamp'] = arrRow['timestamp']
            row['close_type'] = arrRow['close_type']
            row['limit_price'] = arrRow['limit_price']
            row['fill/timestamp'] = arrRow['fill/timestamp']
            row['fill/quantity'] = arrRow['fill/quantity']
            row['fill/cashChange'] = arrRow['fill/cashChange']
            row['fill/commission'] = arrRow['fill/commission']
            row['fill/impactCost'] = arrRow['fill/impactCost']
            row.append()
        self.order.flush() 
        
    def close(self):
        if self.isTable:
            self.orderFile.close()
        else:
            self.fillTable()
            self.orderFile.close()
        