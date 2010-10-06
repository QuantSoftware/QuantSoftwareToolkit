import tables as pt #@UnresolvedImport
import time

class FillModel(pt.IsDescription):
    timestamp = pt.Time64Col()
    quantity = pt.Int32Col()
    cashChange = pt.Float32Col()
    commission = pt.Float32Col()
    impactCost = pt.Float32Col()
    
class OrderModel(pt.IsDescription):
    task = pt.StringCol(5)
    shares = pt.Int32Col()
    symbol = pt.StringCol(30)
    order_type = pt.StringCol(5)       #moo moc limit vwap
    duration = pt.Time64Col()
    timestamp = pt.Time64Col()
    close_type = pt.StringCol(4)       #lifo or fifo for a sell, none for a buy
    limit_price = pt.Float32Col()
    fill = FillModel()