import StrategyData, Simulator, tables as pt
from models.PortfolioModel import PortfolioModel
import numpy as np

class Portfolio:

    def __init__(self, cash, stocks):
        '''
        @param cash: int representing the cash on hand
        @param stocks: dictionary representing all of the stocks a user has {}
        '''
        self.currCash = float(cash)
        self.currStocks = stocks
        self.lastNonNanValue= {} #dict
        
    
    def buyTransaction(self, order):
        '''
        @param order: the order (we know is valid at this point) to execute on the portfolio
        @summary: Updates the portfolio after a stock is purchased
        '''
        # Subtract the impact cost - it cost more because you inflated the price buying so much
        # cashChange is NEGATIVE when passed in 
        self.currCash += float(-order['fill/commission'] + (order['fill/cashChange'] * order['fill/quantity']) - order['fill/impactCost'])
        print "Cash adjusted for buy txn is: " + str(self.currCash)
        if order['symbol'] in self.currStocks.keys():
            self.currStocks[order['symbol']] += order['fill/quantity']
        else:
            self.currStocks[order['symbol']] = order['fill/quantity']

        self.lastNonNanValue[order['symbol']]= order['limit_price']
        
    def sellTransaction(self,order):
        '''
        @param order: the order (we know is valid at this point) to execute on the portfolio        
        @summary: Updates the portfolio after a stock is sold
        '''
        # Subtract effect - gain less money
        # cashChange is POSITIVE when passed in 
        self.currCash += float(-order['fill/commission'] + (order['fill/cashChange'] * order['fill/quantity']) - order['fill/impactCost'])
        print "Cash adjusted for sell  txn is: " + str(self.currCash)
        if order['symbol'] in self.currStocks:
            self.currStocks[order['symbol']] -= order['fill/quantity']
            if self.currStocks[order['symbol']] == 0:
                del self.currStocks[order['symbol']]
        else:
            self.currStocks[order['symbol']] = -order['fill/quantity']
        
        self.lastNonNanValue[order['symbol']]= order['limit_price']    
    
    def hasStock(self,symbol,volume):
        '''
        @summary: Returns a boolean of whether or not the appropriate amount of the given stock exist in the portfolio.
        '''
        if not symbol in self.currStocks:
            return False
        if volume < 0:
            return self.currStocks[symbol] <= volume
        return self.currStocks[symbol] >= volume
    
    
    def calcPortfolioValue(self, timestamp, dataAccess):
        '''
        @attention: includes cash
        '''
        DAY= 86400
        
        portfolioValue= float(0.0)
        for stock in self.currStocks:
            stockPrice= dataAccess.getStockDataItem (str(stock), 'adj_close', timestamp - DAY)
            
            if (np.isnan(stockPrice)):
                portfolioValue+= float (self.lastNonNanValue[str(stock)])
            else:
                #value is not nan
                portfolioValue+= float(stockPrice)
                self.lastNonNanValue[str(stock)]= float(stockPrice)
        
        portfolioValue+= float(self.currCash)
        return portfolioValue            
        #calcPortfolioValue done        
        
    def getHeldQty(self, stock):
        if stock in self.currStocks.keys():
            return self.currStocks[stock]
        else:
            return np.NaN
        
    def getListOfStocks(self):
        '''
        @return: A list of all cureently held stocks (in arbitrary order?)
        '''
        return self.currStocks.keys()    
            
    
    def close(self):
        #no tables or HDF5 output
        pass
        