import models.PortfolioModel, models.PositionModel, models.OrderModel, models.StockPriceModel
import tables as pt
portfolio=None; position=None; order=None; stockPrice=None
portfolioFile=None; positionFile=None; orderFile=None; stockPriceFile=None

class Simulator():
    def __init__(self, initialPortfolio, strategy, startTime, endTime, interval):
        global portfolio, position, order, stockPrice
        global portfolioFile, positionFile, orderFile, stockPriceFile
        portfolioFile = pt.openFile('PortfolioModel.h5', mode = "w")
        positionFile = pt.openFile('PositionModel.h5', mode = "w")
        orderFile = pt.openFile('OrderModel.h5', mode = "w")
        stockPriceFile = pt.openFile('StockPriceModel.h5', mode = "w")
        
        portfolio = portfolioFile.createTable('/', 'portfolio', PortfolioModel)
        position = positionFile.createTable('/', 'position', PositionModel)
        order = orderFile.createTable('/', 'order', OrderModel)
        stockPrice = stockPriceFile.createTable('/', 'stockPrice', StockPriceModel)
    
    def run(self):
        pass
        
    def close(self):
        global portfolioFile, positionFile, orderFile, stockPriceFile
        portfolioFile.close()
        positionFile.close()
        orderFile.close()
        stockPriceFile.close()
        