import models.PortfolioModel, models.PositionModel, models.OrderModel, models.StrategyDataModel
import tables as pt
from optparse import OptionParser
import sys, time




class Simulator():
    def __init__(self, cash, stocks, strategy, startTime, endTime, interval, minCom, comPerShare):
        # NOTE: As written currently, strategy is a method
        self.strategy = strategy
        self.startTime = startTime
        self.currTimestamp = startTime
        self.endTime = endTime
        self.interval = interval
        self.minCom = minCom
        self.comPerShare = comPerShare
        
        self.times =  [] # eventual list for timestamps
        
        self.portfolio = Portfolio(cash, stocks)   #portfolioFile.createTable('/', 'portfolio', self.PortfolioModel)
        self.position = Position()   #positionFile.createTable('/', 'position', self.PositionModel)
        self.order = Order()   #orderFile.createTable('/', 'order', self.OrderModel)
        self.strategyData = StrategyData('models/PriceTestData.h5')   #strategyDataFile.createTable('/', 'strategyData', self.strategyDataModel)
    
    def addTimeStamps(self):
        #Not sure how to iterate through all stock data - probably not indexing correctly
        temp = []
        for i in range(len(self.strategyData)): # Read through all stock data
            if self.strategyData[i].timestamp not in temp:
                temp.append(self.strategyData[i].timestamp) # add unique timestamps to list
        return temp
    
    def calcCommission(self, volume):
        return max(minCom,volume * self.comPerShare)
    
    # NOTE : I am somewhat unclear on exactly everything is stored/how to access the data
    def getExecutionTimestamp(self):
        #Ideally, we trade as soon as we can
        idealTime = self.currTimestamp + self.interval
        if idealTime < (self.strategyData.data.when_available): # We don't have the data yet
            idealTime = self.strategyData.data.when_available + self.interval # Wait til available and go at next interval
        return idealTime
    
    def buyStock(self, newOrder):
        '''
        function takes in an instance of OrderDetails, executes the changes to the portfolio and adds the order to the order table
        newOrderDetails: an instance of OrderDetails representing the new order
        Note: The Order should not be added to the order table before calling this function
        '''
        
        #buyTransaction needs to be expanded and put in here instead.
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
        #self.position.append(purchase)         
        #newOrder = self.order.addOrder(self.currTimestamp,newOrderDetails.shares,newOrderDetails.symbol,newOrderDetails.orderType,newOrderDetails.duration,newOrderDetails.closeType,newOrderDetails.limitPrice)
        ts = self.getExecutionTimestamp() #need a function to get the next available time we can trade
            
        if newOrder.order_type == 'moo':
            #market order open
            price = strategyData.getPrice(ts, newOrder.symbol, 'adj_open')
            cost = newOrder.shares * price + self.calcCommission(newOrder.shares)
            if(cost>self.portfolio.currCash):
                #Not enough cash to buy stock
                return None
            #__execute trade__
            #populate fill field in order
            newOrder.fill.timestamp = ts
            newOrder.fill.quantity = newOrder.shares
            newOrder.fill.cashChange = -price
            newOrder.fill.commission = self.calcCommission(newOrder.shares)
            #add trade to portfolio
            self.portfolio.buyTransaction(newOrder)
            #add position
            self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder.order_type == 'moc':
            #market order close
            price = strategyData.getPrice(ts, newOrder.symbol, 'adj_close')
            cost = newOrder.shares * price + self.calcCommission(newOrder.shares)
            if(cost>self.portfolio.currCash):
                #Not enough cash to buy stock
                return None
            #__execute trade__
            #populate fill field in order
            newOrder.fill.timestamp = ts
            newOrder.fill.quantity = newOrder.shares
            newOrder.fill.cashChange = -price
            newOrder.fill.commission = self.calcCommission(newOrder.shares)
            #add trade to portfolio
            self.portfolio.buyTransaction(newOrder)
            #add position
            self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder.order_type == 'limit':
            #limit order
            price = newOrder.limit_price
            cost = newOrder.shares * price + self.calcCommission(newOrder.shares)
            if ((newOrder.limit_price > strategyData.getPrice(ts, newOrder.symbol, 'adj_high')) or ( newOrder.limit_price < strategyData.getPrice(ts, newOrder.symbol, 'adj_low'))):
                #limit price outside of daily range
                return None
            if(cost>self.portfolio.currCash):
                #Not enough cash to buy stock
                return None
            #__execute trade__
            #populate fill field in order
            newOrder.fill.timestamp = ts
            newOrder.fill.quantity = newOrder.shares
            newOrder.fill.cashChange = -price
            newOrder.fill.commission = self.calcCommission(newOrder.shares)
            #add trade to portfolio
            self.portfolio.buyTransaction(newOrder)
            #add position
            self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder.order_type == 'vwap':
            #volume weighted average price
            price = strategyData.getPrice(ts, newOrder.symbol, 'adj_open')
            price += strategyData.getPrice(ts, newOrder.symbol, 'adj_close')
            price += strategyData.getPrice(ts, newOrder.symbol, 'adj_high')
            price += strategyData.getPrice(ts, newOrder.symbol, 'adj_low')
            price = price / 4.
            cost = newOrder.shares * price + self.calcCommission(newOrder.shares)
            if(cost>self.portfolio.currCash):
                #Not enough cash to buy stock
                return None
            #__execute trade__
            #populate fill field in order
            newOrder.fill.timestamp = ts
            newOrder.fill.quantity = newOrder.shares
            newOrder.fill.cashChange = -price
            newOrder.fill.commission = self.calcCommission(newOrder.shares)
            #add trade to portfolio
            self.portfolio.buyTransaction(newOrder) 
            #add position
            self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        else:
            #throw invalid type error
            raise TypeError("Not an existing trade type '%s'." % str(newOrder.order_type))
        return price
    
    def sellStock(self,newOrder):
        """
        Comments 'n stuff go here.
        """
        #sellTransaction needs to be expanded and put here instead.
        #newOrder = self.order.addOrder(self.currTimestamp,newOrderDetails.shares,newOrderDetails.symbol,newOrderDetails.orderType,newOrderDetails.duration,newOrderDetails.closeType,newOrderDetails.limitPrice)
        ts = self.getExecutionTimestamp() #need a function to get the next available time we can trade
            
        if newOrder.order_type == 'moo':
            #market order open
            price = strategyData.getPrice(ts, newOrder.symbol, 'adj_open')
            profit = newOrder.shares * price - self.calcCommission(newOrder.shares)
            if(self.portfolio.hasStock(newOrder.symbol,newOrder.shares)):
                #Not enough shares owned to sell requested amount
                return None
            #__execute trade__
            #populate fill field in order
            newOrder.fill.timestamp = ts
            newOrder.fill.quantity = newOrder.shares
            newOrder.fill.cashChange = profit
            newOrder.fill.commission = self.calcCommission(newOrder.shares)
            #add trade to portfolio
            self.portfolio.sellTransaction(newOrder)
            #remove positions according to lifo/fifo
            
            #self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder.order_type == 'moc':
            #market order close
            price = strategyData.getPrice(ts, newOrder.symbol, 'adj_close')
            profit = newOrder.shares * price - self.calcCommission(newOrder.shares)
            if(self.portfolio.hasStock(newOrder.symbol,newOrder.shares)):
                #Not enough shares owned to sell requested amount
                return None
            #__execute trade__
            #populate fill field in order
            newOrder.fill.timestamp = ts
            newOrder.fill.quantity = newOrder.shares
            newOrder.fill.cashChange = profit
            newOrder.fill.commission = self.calcCommission(newOrder.shares)
            #add trade to portfolio
            self.portfolio.sellTransaction(newOrder)
            #remove positions according to lifo/fifo
            
            #self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder.order_type == 'limit':
            #limit order
            price = newOrder.limit_price
            profit = newOrder.shares * price - self.calcCommission(newOrder.shares)
            if ((newOrder.limit_price > strategyData.getPrice(ts, newOrder.symbol, 'adj_high')) or ( newOrder.limit_price < strategyData.getPrice(ts, newOrder.symbol, 'adj_low'))):
                #limit price outside of daily range
                return None
            if(self.portfolio.hasStock(newOrder.symbol,newOrder.shares)):
                #Not enough shares owned to sell requested amount
                return None
            #__execute trade__
            #populate fill field in order
            newOrder.fill.timestamp = ts
            newOrder.fill.quantity = newOrder.shares
            newOrder.fill.cashChange = profit
            newOrder.fill.commission = self.calcCommission(newOrder.shares)
            #add trade to portfolio
            self.portfolio.sellTransaction(newOrder)
            #remove positions according to lifo/fifo
            
            #self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder.order_type == 'vwap':
            #volume weighted average price
            price = strategyData.getPrice(ts, newOrder.symbol, 'adj_open')
            price += strategyData.getPrice(ts, newOrder.symbol, 'adj_close')
            price += strategyData.getPrice(ts, newOrder.symbol, 'adj_high')
            price += strategyData.getPrice(ts, newOrder.symbol, 'adj_low')
            price = price / 4.
            profit = newOrder.shares * price - self.calcCommission(newOrder.shares)
            if(self.portfolio.hasStock(newOrder.symbol,newOrder.shares)):
                #Not enough shares owned to sell requested amount
                return None
            #__execute trade__
            #populate fill field in order
            newOrder.fill.timestamp = ts
            newOrder.fill.quantity = newOrder.shares
            newOrder.fill.cashChange = profit
            newOrder.fill.commission = self.calcCommission(newOrder.shares)
            #add trade to portfolio
            self.portfolio.sellTransaction(newOrder)
            #remove positions according to lifo/fifo
            
            #self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        else:
            #throw invalid type error
            raise TypeError("Not an existing trade type '%s'." % str(newOrder.order_type))
        return price
            
    def execute(self,commands):
        # commands format: ([(sale details),(sale details),...],[(purchase details),(purchase details),...])
        # sale details: (shares,symbol,orderType,duration,closeType,(optional) limit price)
        # purchase details: (shares,symbol,orderType,duration,closeType,(optional) limit price)
        for sellStock in commands[0]:
            if len(sellStock) == 5:
                sellOrder = OrderDetails(sellStock[0],sellStock[1],sellStock[2],sellStock[3],sellStock[4])
            else:
                sellOrder = OrderDetails(sellStock[0],sellStock[1],sellStock[2],sellStock[3],sellStock[4],sellStock[5])
            newOrder = self.order.addOrder(self.currTimestamp,newOrderDetails.shares,newOrderDetails.symbol,newOrderDetails.orderType,newOrderDetails.duration,newOrderDetails.closeType,newOrderDetails.limitPrice)
            result = self.sellStock(newOrder)
            if noisy:
                if result:
                    print "Succeeded in selling %d shares of %s for %f as %s, with close type %s.  Current timestamp: %d" % (sellStock[0],sellStock[1],result,sellStock[2],sellStock[4],self.currTimestamp)
                else:
                    print "Did not succeed in selling %d shares of %s as %s.  Order valid until %d.  Current timestamp: %d" %(sellStock[0],sellStock[1],sellStock[2],sellStock[3]+self.currTimestamp,self.currTimestamp)
        
        for buyStock in commands[1]:
            if len(buyStock) == 5:
                buyOrder = OrderDetails(buyStock[0],buyStock[1],buyStock[2],buyStock[3],buyStock[4])
            else:
                buyOrder = OrderDetails(buyStock[0],buyStock[1],buyStock[2],buyStock[3],buyStock[4],buyStock[5])
            newOrder = self.order.addOrder(self.currTimestamp,newOrderDetails.shares,newOrderDetails.symbol,newOrderDetails.orderType,newOrderDetails.duration,newOrderDetails.closeType,newOrderDetails.limitPrice)
            result = self.buyStock(newOrder)
            if noisy:
                if result:
                    print "Succeeded in buying %d shares of %s for %f as %s, with close type %s.  Current timestamp: %d" % (buyStock[0],buyStock[1],result,buyStock[2],buyStock[4],self.currTimestamp)
                else:
                    print "Did not succeed in buying %d shares of %s as %s.  Order valid until %d.  Current timestamp: %d" %(buyStock[0],buyStock[1],buyStock[2],buyStock[3]+self.currTimestamp,self.currTimestamp)
        for order in self.orders.iterrow:
            if order.duration + order.timestamp <= self.currTimestamp:
                if order.fill == None:
                    #Have unfilled, valid orders
                    if order['close_type'].upper() == "NONE":
                        #is a buy
                        result = self.buyStock(order)
                        if noisy:
                            if result:
                                print "Succeeded in buying %d shares of %s for %f as %s, with close type %s.  Current timestamp: %d" % (order['shares'], order['symbol'], result, order['order_type'], order['close_type'], self.currTimestamp)
                            else:
                                print "Did not succeed in buying %d shares of %s as %s.  Order valid until %d.  Current timestamp: %d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], self.currTimestamp)
                    else:
                        result = self.sellStock(order)
                        if noisy:
                            if result:
                                print "Succeeded in selling %d shares of %s for %f as %s, with close type %s.  Current timestamp: %d" % (order['shares'], order['symbol'], result, order['order_type'], order['close_type'], self.currTimestamp)
                            else:
                                print "Did not succeed in selling %d shares of %s as %s.  Order valid until %d.  Current timestamp: %d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], self.currTimestamp)
                                
                                  
    def run(self):
        self.currTimestamp = self.startTime
        while self.currTimestamp < self.endTime and self.currTimestamp < time.time():
            self.execute(self.strategy(self.portfolio,self.currTimeStamp,self.strategyData))
            if noisy:
                print "Strategy at %d completed successfully." % self.currTimestamp
            self.currTimestamp += self.timeStep
        if noisy:
            print "Simulation complete."
        self.close()
        
    def close(self):
        self.portfolioFile.close()
        self.positionFile.close()
        self.orderFile.close()
        self.strategyDataFile.close()



cash = 0; comPerShare = 0.0; minCom = 0.; startTime = 0; endTime = 0; timeStep = 0; maxEffect = 0.; decayCycles = 0
noisy = False

def main():
    global cash,comPerShare,minCom,startTime,endTime,timeStep,maxEffect,decayCycles,noisy
    # NOTE: the OptionParser class is currently not necessary, as we can just access sys.argv[1:], but if we
    # want to implement optional arguments, this will make it considerably easier.
    parser = OptionParser()
    
    # parser.parse_args() returns a tuple of (options, args)
    # As of right now, we don't have any options for our program, so we only care about the three arguments:
    # config file, strategy module name, strategy main function name
    args = parser.parse_args()[1]
    
    if len(args) != 3 and len(args) != 2:
        print "FAILURE TO INCLUDE THE CORRECT NUMBER OF ARGUMENTS; TERMINATING INCOMPETENT USER."
        return
    
    configFile = args[0]
    if len(args) == 3:
        stratName = args[2]
    else:
        stratName = "strategyMain"
    #print sys.path
    open(configFile,'r')
    for fileName in ["default.ini",configFile]:
        thisFile = open(fileName,'r')
        for line in thisFile.readlines():
            # Separate the command in the config file from the arguments
            if not ('#' in line):
                line = line.strip().split('=')
                command = line[0].strip().upper()
                if len(line)>1:
                    vals = line[1].upper().split()
                else:
                    vals = []
                # Parse commands, look for correct number of arguments, do rudimentary error checking, apply to simulator as appropriate
                if command == 'CASH':
                    if len(vals) != 1:
                        print "WRONG NUMBER OF ARGUMENTS FOR CASH!!  RAAAAWR!"
                    else:
                        try:
                            cash = float(vals[0])
                        except ValueError:
                            print "ARGUMENT FOR CASH IS NOT A FLOAT!! RAAAWR!"
                
                # Code for handling stocks in a starting portfolio.  Implementation not correct; removing for the time being.
#                elif command == "STOCK":
#                    if len(vals) != 2:
#                        print "WRONG NUMBER OF ARGUMENTS FOR STOCK!!  RAAAAWR!  ALSO, I NEED TO LEARN TO THROW ERRORS!"
#                    else:
#                        try:
#                            stocks.append([vals[0],int(vals[1])])
#                        except:
#                            print "STOCK TAKES IN A STOCK NAME AND AN INT!  AND DON'T YOU FORGET IT!"
                elif command == "COMPERSHARE":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR COMMISSIONS PER SHARE."
                    else:
                        try:
                            comPerShare = float(vals[0])
                        except ValueError:
                            print "COMMISSIONS PER SHARE REQUIRES A FLOAT INPUT"
                elif command == "MINCOM":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR MINIMUM COMMISSION."
                    else:
                        try:
                            minCom = float(vals[0])
                        except ValueError:
                            print "MINIMUM COMMISSIONS REQUIRES A FLOAT INPUT"
                elif command == "STARTTIME":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR START TIME."
                    else:
                        try:
                            startTime = long(vals[0])
                        except ValueError:
                            print "START TIME REQUIRES A LONG INPUT"
                elif command == "ENDTIME":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR END TIME."
                    else:
                        try:
                            endTime = long(vals[0])
                        except ValueError:
                            print "END TIME REQUIRES A LONG INPUT"
                elif command == "TIMESTEP":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR TIME STEP."
                    else:
                        try:
                            timeStep = long(vals[0])
                        except ValueError:
                            print "TIME STEP REQUIRES A LONG INPUT"
                elif command == "MAXMARKETEFFECT":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR MAX MARKET EFFECT."
                    else:
                        try:
                            maxEffect = float(vals[0])
                        except ValueError:
                            print "MAX MARKET EFFECT REQUIRES A FLOAT INPUT"
                elif command == "DECAYCYCLES":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR DECAY CYCLES."
                    else:
                        try:
                            decayCycles = int(vals[0])
                        except ValueError:
                            print "DECAY CYCLES REQUIRES AN INTEGER INPUT"
                elif command == "NOISY":
                    noisy = True
                elif command != '':
                        print "Unrecognized command '%s'.  Note: some commands may not yet be implemented.  E-mail pdohogne3@gatech.edu if a command is missing." % command
    f.close()
    g.close()
    if noisy:
        print "Config file parsed successfully.  Starting simulation."
    
    
    # Add the strategies subdirectory to the system path so Python can find the module
    sys.path.append(sys.path[0] + '/strategies')
    myStrategy = eval("__import__('%s').%s" % (args[1],stratName) )
    
    mySim = Simulator(cash,{}, myStrategy, startTime, endTime, timeStep, minCom, comPerShare)
    # Add the timestamps
    mySim.times = mySim.addTimeStamps()
    mySim.run()

# This ensures the main function runs automatically when the program is run from the command line, but 
# not if the file somehow gets imported from something else.  Nifty, eh?
if __name__ == "__main__":
    main()