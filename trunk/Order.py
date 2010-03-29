import tables as pt
from models.OrderModel import OrderModel
#play with iterator vs object for newOrder

'''
Based on the model:
FillModel:
    timestamp = pt.Time64Col()
    quantity = pt.Int32Col()
    price = pt.Float32Col()
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
    def __init__(self):
        self.orderFile = pt.openFile('OrderModel.h5', mode = "w")
        self.order = self.orderFile.createTable('/', 'order', OrderModel)
    
    def addOrder(self,timestamp,shares,symbol,orderType,duration,closeType,limitPrice = 0): 
        ''' 
        adds a new unfulfilled order to the orders table
        timestamp: the exact timestamp when the order was submitted
        shares: the number of shares to trade
        symbol: the symbol abbreviation of the stock
        orderType: they type of order (moo, moc, limit, vwap)
        duration: the length of time the order is valid for
        closeType: sell first or sell last (lifo,fifo)
        
        returns a reference to the row
        '''  
        row = self.order.row
        row['shares'] = shares
        row['symbol'] = symbol
        row['order_type'] = orderType
        row['duration'] = duration
        row['timestamp'] = timestamp
        row['close_type'] = closeType
        row['limit_price'] = limitPrice
        row.append()
        return row
        
    def fillOrder(self, timestamp, rowIterator, quantity, price):
        ''' 
        adds a fill to a given order
        timestamp: the exact timestamp when the order was fufilled
        rowIterator: a pytables iteratable rows object with 1 row, the row to be filled in it
        quantity: the number of shares successfully traded
        price: the purchase price per share
        '''  
        for row in rowIterator:
            row['timestamp'] = timestamp
            row['quantity'] = quantity
            row['price'] = price
            row.update()
        
    def close(self):
        self.orderFile.close()