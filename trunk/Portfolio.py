import Simulator

class Portfolio:

    def __init__(self, cash, stocks):
        '''
        cash: int representing the cash on hand
        stocks: dictionary representing all of the stocks a user has {}
        '''
        self.currCash = cash
        self.currStocks = stocks
    
   
    def buyStocks(self, newOrder):
        '''
        function takes in an instance of OrderModel executes the changes to the portfolio and adds the order to the order table
        newOrder: an instance of OrderModel representing the new order
        Note: The OrderModel should not be added to the order table before calling this function
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
        