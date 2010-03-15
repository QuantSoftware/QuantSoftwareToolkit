import models.PortfolioModel, tables as pt
import Simulator

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
    
   
    def buyStocks(self, newOrder):
        '''
        function takes in an instance of Order executes the changes to the portfolio and adds the order to the order table
        newOrder: an instance of Order representing the new order
        Note: The Order should not be added to the order table before calling this function
        ''' 
        if newOrder.order_type == 'moo':
            #market order open
            Simulator.order.append(newOrder)
        elif newOrder.order_type == 'moc':
            #market order close
            Simulator.order.append(newOrder)
        elif newOrder.order_type == 'limit':
            #limit order
            Simulator.order.append(newOrder)
        elif newOrder.order_type == 'vwap':
            #volume weighted average price
            Simulator.order.append(newOrder)
        else:
            #throw invalid type error
            pass
    
    def addTransaction(self, cashChange, position):
        '''
        cashChange: the increase or decrease of the portfolio cash value
        position: a pytables row object representing the new position to be added
        '''
        
    def close(self):
        self.portfolioFile.close()