import tables as pt, numpy as np
from models.OrderModel import OrderModel
#play with iterator vs object for newOrder

'''
Based on the model:
FillModel:
    timestamp = pt.Time64Col()
    quantity = pt.Int32Col()
    cashChange = pt.Float32Col()
    commission = pt.Float32Col()
    
OrderModel:
    shares = pt.Int32Col()
    symbol = pt.StringCol(4)
    order_type = pt.StringCol(5)       #moo moc limit vwap
    duration = pt.Time64Col()
    timestamp = pt.Time64Col()
    close_type = pt.StringCol(4)       #lifo or fifo for a sell, none for a buy
    limit_price = pt.Float32Col()
    fill = FillModel()
'''

class Order:
    def __init__(self, isTable):
        self.orderFile = pt.openFile('OrderModel.h5', mode = "w")
        self.order = self.orderFile.createTable('/', 'order', OrderModel)
        if isTable == False:
            self.orderArray = np.array([])
    
    def addOrder(self,timestamp,task,shares,symbol,orderType,duration,closeType,limitPrice,isTable): 
        ''' 
        adds a new unfulfilled order to the orders table
        timestamp: the exact timestamp when the order was submitted
        task: buy, sell, short, cover
        shares: the number of shares to trade
        symbol: the symbol abbreviation of the stock
        orderType: they type of order (moo, moc, limit, vwap)
        duration: the length of time the order is valid for
        closeType: sell first or sell last (lifo,fifo)
        
        returns a reference to the row
        '''  
        if isTable:
            row = self.order.row
            row['task'] = task
            row['shares'] = shares
            row['symbol'] = symbol
            row['order_type'] = orderType
            row['duration'] = duration
            row['timestamp'] = timestamp
            row['close_type'] = closeType
            row['limit_price'] = limitPrice
            #row.append()
            #self.order.flush()
            return row
        else:
            return self.addOrderArray(timestamp,task,shares,symbol,orderType,duration,closeType,limitPrice = 0)
        
    def fillOrder(self, timestamp, rowIterator, quantity, price, commission, impactCost, isTable):
        ''' 
        CURRENTLY DONE IN THE SIMULATOR BUY/SELL METHODS
        adds a fill to a given order
        timestamp: the exact timestamp when the order was fufilled
        rowIterator: a pytables iteratable rows object with 1 row, the row to be filled in it
        quantity: the number of shares successfully traded
        price: the purchase price per share
        '''  
        for row in rowIterator:
            row['fill/timestamp'] = timestamp
            row['fill/quantity'] = quantity
            row['fill/cashChange'] = price
            row['fill/commission'] = commission
            row['fill/impactCost'] = impactCost
            row.update()
    
    def getOrders(self,isTable = False):
        if isTables:
            return self.order.iterrows()
        else:
            return self.orderArray
        
    def addOrderArray(self,timestamp,task,shares,symbol,orderType,duration,closeType,limitPrice):  
        ''' 
        adds a new unfulfilled order to the orders table
        timestamp: the exact timestamp when the order was submitted
        task: buy, sell, short, cover
        shares: the number of shares to trade
        symbol: the symbol abbreviation of the stock
        orderType: they type of order (moo, moc, limit, vwap)
        duration: the length of time the order is valid for
        closeType: sell first or sell last (lifo,fifo)
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
        np.append(self.orderArray,row)
        return row
      
    def fillOrderArray(self, timestamp, rowIterator, quantity, price, commission, impactCost):
        '''
        CURRENTLY DONE IN THE SIMULATOR BUY/SELL METHODS
        adds a fill to a given order
        timestamp: the exact timestamp when the order was fufilled
        rowIterator: a pytables iteratable rows object with 1 row, the row to be filled in it
        quantity: the number of shares successfully traded
        price: the purchase price per share
        '''  
        row['fill/timestamp'] = timestamp
        row['fill/quantity'] = quantity
        row['fill/cashChange'] = price
        row['fill/commission'] = commission
        row['fill/impactCost'] = impactCost
        
    def fillTable(self):
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
        
    def close(self, isTable = False):
        if isTable:
            self.orderFile.close()
        else:
            self.fillTable()
            self.orderFile.close()
        