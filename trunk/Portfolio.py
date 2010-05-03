import StrategyData, Simulator, tables as pt
from models.PortfolioModel import PortfolioModel

class Portfolio:

    def __init__(self, cash, stocks):
        '''
        cash: int representing the cash on hand
        stocks: dictionary representing all of the stocks a user has {}
        '''
        self.currCash = cash
        self.currStocks = stocks
    
    def buyTransaction(self, order):
        '''
        Updates the portfolio after a stock is purchased
        order: the order (we know is valid at this point) to execute on the portfolio
        '''
        # Subtract the impact cost - it cost more because you inflated the price buying so much
        # cashChange is NEGATIVE when passed in 
        self.currCash += -order['fill/commission'] + (order['fill/cashChange'] * order['fill/quantity']) - order['fill/impactCost']
        if order['symbol'] in self.currStocks.keys():
            self.currStocks[order['symbol']] += order['fill/quantity']
        else:
            self.currStocks[order['symbol']] = order['fill/quantity']
        
    def sellTransaction(self,order):
        '''
        Updates the portfolio after a stock is sold
        order: the order (we know is valid at this point) to execute on the portfolio        
        '''
        # Subtract effect - gain less money
        # cashChange is POSITIVE when passed in 
        self.currCash += -order['fill/commission'] + (order['fill/cashChange'] * order['fill/quantity']) - order['fill/impactCost']
        
        if order['symbol'] in self.currStocks:
            self.currStocks[order['symbol']] -= order['fill/quantity']
            if self.currStocks[order['symbol']] == 0:
                del self.currStocks[order['symbol']]
        else:
            self.currStocks[order['symbol']] = -order['fill/quantity']
    
    def hasStock(self,symbol,volume):
        """
        Returns a boolean of whether or not the appropriate amount of the given stock
        exist in the portfolio.
        """
        if not symbol in self.currStocks:
            return False
        if volume < 0:
            return self.currStocks[symbol] <= volume
        return self.currStocks[symbol] >= volume
    
    def close(self):
        #no tables or HDF5 output
        pass
        