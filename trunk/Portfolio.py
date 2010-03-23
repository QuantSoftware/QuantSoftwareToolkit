import models.PortfolioModel, StockPrice, Simulator, tables as pt

'''
Based on the model:
PortfolioModel:
    cash = pt.Int32Col()
    positions = Position.PositionModel()
'''
class Portfolio:

    def __init__(self, cash, stocks):
        '''
        cash: int representing the cash on hand
        stocks: dictionary representing all of the stocks a user has {}
        '''
        self.portfolioFile = pt.openFile('PortfolioModel.h5', mode = "w")
        self.portfolio = portfolioFile.createTable('/', 'portfolio', PortfolioModel)
        self.currCash = cash
        self.currStocks = stocks
    
    
    def buyTransaction(self, order):
        '''
        order: the order (we know is valid at this point) to execute on the portfolio
        '''
        self.currCash -= order['fill']['commission'] + order['fill']['price'] * order['fill']['quantity']
        if order['symbol'] in self.currStocks.keys():
            self.currStocks[order['symbol']] += order['fill']['quantity']
        else:
            self.currStocks[order['symbol']] = order['fill']['quantity']
        
    def sellTransaction(self,order):
        '''
        see buyTransaction for now
        
        '''
        self.currCash += -order['fill']['commission'] + order['fill']['price'] * order['fill']['quantity']
        if order['symbol'] in self.currStocks:
            self.currStocks[order['symbol']] -= order['fill']['quantity']
            if self.currStocks[order['symbol']] == 0:
                del self.currStocks[order['symbol']]
        else:
            self.currStocks[order['symbol']] = -order['fill']['quantity']
    
    def hasStock(self,symbol,volume):
        """
        Returns a boolean of whether or not the appropriate amount of the given stock
        exist in the portfolio.
        """
        if not order['symbol'] in self.currStocks:
            return False
        return self.currStocks[order['symbol']] >= volume
    
    def close(self):
        self.portfolioFile.close()