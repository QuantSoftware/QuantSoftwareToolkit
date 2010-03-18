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
    

    def buyStock(self, newOrder):
        '''
        function takes in an instance of Order executes the changes to the portfolio and adds the order to the order table
        newOrder: an instance of Order representing the new order
        Note: The Order should not be added to the order table before calling this function
        ''' 
        Simulator.order.append(newOrder)
        """    
        '''
        ORDER:
        row['shares'] = shares
        row['symbol'] = symbol
        row['order_type'] = orderType
        row['duration'] = duration
        row['timestamp'] = timestamp
        row['close_type'] = closeType
        '''  
        #purchase = Position(timestamp, self.symbol, quantity, price)
        #Simulator.position.append(purchase)         
        if newOrder.order_type == 'moo':
            #market order open
            ts = Simulator.getAvailableTimestamp() #need a function to get the most recent when_available timestamp from the simulator
            price = StockPrice.getPrice(ts, newOrder.symbol, 'adj_open')
            cost = newOrder.shares * price
            if(cost>self.currCash):
                #Not enough cash to buy stock
                return None
            Simulator.order.append(newOrder)
        elif newOrder.order_type == 'moc':
            #market order close
            ts = Simulator.getAvailableTimestamp() #need a function to get the most recent when_available timestamp from the simulator
            price = StockPrice.getPrice(ts, newOrder.symbol, 'adj_close')
            cost = newOrder.shares * price
            if(cost>self.currCash):
                #Not enough cash to buy stock
                return None
            Simulator.order.append(newOrder)
        elif newOrder.order_type == 'limit':
            #limit order
            ts = Simulator.getAvailableTimestamp() #need a function to get the most recent when_available timestamp from the simulator
            price = StockPrice.getPrice(ts, newOrder.symbol, 'adj_open')
            cost = newOrder.shares * price
            if(cost>self.currCash):
                #Not enough cash to buy stock
                return None            
            Simulator.order.append(newOrder)
        elif newOrder.order_type == 'vwap':
            #volume weighted average price
            ts = Simulator.getAvailableTimestamp() #need a function to get the most recent when_available timestamp from the simulator
            price = StockPrice.getPrice(ts, newOrder.symbol, 'adj_open')
            cost = newOrder.shares * price
            if(cost>self.currCash):
                #Not enough cash to buy stock
                return None            
            Simulator.order.append(newOrder)
        else:
            #throw invalid type error
            pass
        """
    
    def isValidTransaction(self, newOrder, commision, type):
        pass
    
    def addTransaction(self, cashChange, position):
        '''
        cashChange: the increase or decrease of the portfolio cash value
        position: a pytables row object representing the new position to be added
        '''
        pass
    
    def close(self):
        self.portfolioFile.close()