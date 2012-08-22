import tables as pt #@UnresolvedImport

class PortfolioModel(pt.IsDescription):
    cash = pt.Float32Col()
    timestamp = pt.Time64Col()