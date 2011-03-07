import tables as pt #@UnresolvedImport
import numpy as np

class PositionModel(pt.IsDescription):
    timestamp = pt.Time64Col()
    symbol = pt.StringCol(30) 
    shares = pt.Int32Col()
    purchase_price = pt.Float32Col()