import models.PortfolioModel, models.PositionModel, models.OrderModel, models.StrategyDataModel
import tables as pt
from optparse import OptionParser
import sys, time
import Portfolio, Position, Order, StrategyData


class Simulator():
    def __init__(self, cash, stocks, strategy, startTime, endTime, interval, minCom, comPerShare, isTable, maxEffect, arrayFile, pytablesFile):
        # NOTE: As written currently, strategy is a method
        self.strategy = strategy
        self.startTime = startTime
        self.currTimestamp = startTime
        self.endTime = endTime
        self.interval = interval
        self.minCom = minCom
        self.comPerShare = comPerShare
        self.timeStampIndex = 0
        self.currDataTimeIndex = 0
        self.maxEffect = maxEffect
        self.times =  [] # eventual list for timestamps
        self.isTable = isTable # Need for getting volumes
        
        self.portfolio = Portfolio.Portfolio(cash, stocks)   #portfolioFile.createTable('/', 'portfolio', self.PortfolioModel)
        self.position = Position.Position()   #positionFile.createTable('/', 'position', self.PositionModel)
        self.order = Order.Order()   #orderFile.createTable('/', 'order', self.OrderModel)
        if isTable:
            self.strategyData = StrategyData.StrategyData(pytablesFile,isTable)   #strategyDataFile.createTable('/', 'strategyData', self.strategyDataModel)
        else:
            self.strategyData = StrategyData.StrategyData(arrayFile,isTable) 
    
    def addTimeStamps(self):
        temp = []

        if timersActive:
            print 'Generating valid timestamps'
            cnt = 0
            cycTime = time.time()
        for i in self.strategyData.strategyData.iterrows():
            if i['timestamp'] not in temp:
                temp.append(i['timestamp'])
            if timersActive:
                if(cnt%1000000==0):
                    print '%i rows finished: %i secs elapsed'%(cnt,time.time()-cycTime)
                cnt+=1
        if timersActive:
            print 'all rows added: %i secs elapsed'%(time.time()-cycTime)        
        temp.sort()
        return temp
    
    def calcCommission(self, volume):
        return max(minCom,volume * self.comPerShare)
    
    def getCurrentDataTimestamp(self):
        while self.times[self.currDataTimeIndex+1]<self.currTimestamp:
            self.currDataTimeIndex += 1
        return self.times[self.currDataTimeIndex]
    
    def getExecutionTimestamp(self):
        while self.times[self.timeStampIndex]<self.currTimestamp:
            self.timeStampIndex += 1
        idealTime = self.times[self.timeStampIndex+1]
        return idealTime
        
    def calcEffect(self, maxVol, shares):
        #print "Market Effect: %f" % (float(shares)/maxVol * self.maxEffect)
        return float(shares)/maxVol * self.maxEffect
        
    def getVolumePerDay(self, symbol, timestamp):  
        # Call with startTime = endTime = desired timestamp to get just that timestamp
        #print "VolPerDay timestamp: %d" % timestamp
        stocks = self.strategyData.getStocks(timestamp, timestamp+1, symbol, self.isTable)
        if len(stocks) > 0:
            myStockasDict = stocks[0] #Grab the first dictionary in the list
            return myStockasDict['volume'] # Get the volume
        return None   
            
    def buyStock(self, newOrder):
        '''
        function takes in an instance of OrderDetails, executes the changes to the portfolio and adds the order to the order table
        newOrderDetails: an instance of OrderDetails representing the new order
        Note: The Order should not be added to the order table before calling this function
        '''
        
        #buyTransaction needs to be expanded and put in here instead.
        #purchase = Position(timestamp, self.symbol, quantity, price)
        #self.position.append(purchase)         
        #newOrder = self.order.addOrder(self.currTimestamp,newOrderDetails.shares,newOrderDetails.symbol,newOrderDetails.orderType,newOrderDetails.duration,newOrderDetails.closeType,newOrderDetails.limitPrice)
        ts = self.getCurrentDataTimestamp() #need a function to get the next available time we can trade
        print "sim ts: %d execution timestamp: %d" % (self.currTimestamp, ts)
        maxVol4Day = self.getVolumePerDay(newOrder['symbol'], ts) # Should this be the trading timestamp or the current one?
        if newOrder['order_type'] == 'moo':
            #market order open
            price = strategyData.getPrice(ts, newOrder['symbol'], 'adj_open')
            if price == None:
                if noisy:
                    print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
                return None
            elif maxVol4Day == None:
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost as you buy
                #print "Market effect markup: %f, commission: %f" % ((checkAmount * price * self.calcEffect(maxVol4Day, checkAmount)),self.calcCommission(checkAmount))
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash):
                    #Not enough cash to buy stock
                    return None
                
                if abs(newOrder['shares']) > maxVol4Day:
                    if newOrder['shares'] < 0:
                        newOrder['shares'] = -maxVol4Day
                    else:
                        newOrder['shares'] = maxVol4Day
                    newOrder.update()
                    self.order.order.flush()
                #__execute trade__
                #populate fill field in order
                newOrder['fill/timestamp'] = ts
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'BUY') else -newOrder['shares']
                newOrder['fill/cashChange'] = -price
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                self.portfolio.buyTransaction(newOrder)
                #add position
                self.position.addPosition(ts,newOrder['symbol'],newOrder['fill/quantity'],price)
        elif newOrder['order_type'] == 'moc':
            #market order close
            price = self.strategyData.getPrice(ts, newOrder['symbol'], 'adj_close', isTable = self.isTable)
            if price == None:
                if noisy:
                    print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
                return None
            elif maxVol4Day == None:
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else: 
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost as you buy
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                #print "Market effect markup: %f, commission: %f" % ((checkAmount * price * self.calcEffect(maxVol4Day, checkAmount)),self.calcCommission(checkAmount))
                if(cost>self.portfolio.currCash):
                    #Not enough cash to buy stock
                    return None
                
                if abs(newOrder['shares']) > maxVol4Day:
                    if newOrder['shares'] < 0:
                        newOrder['shares'] = -maxVol4Day
                    else:
                        newOrder['shares'] = maxVol4Day
                    newOrder.update()
                    self.order.order.flush()
                newOrder['fill/timestamp'] = ts
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'BUY') else -newOrder['shares']
                newOrder['fill/cashChange'] = -price
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                #print newOrder
                self.portfolio.buyTransaction(newOrder)
                #add position
                self.position.addPosition(ts,newOrder['symbol'],newOrder['fill/quantity'],price)
        elif newOrder['order_type'] == 'limit':
            #limit order
            price = newOrder['limit_price']
            if price == None:
                if noisy:
                    print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
                return None
            elif maxVol4Day == None:
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                if ((newOrder['limit_price'] > self.strategyData.getPrice(ts, newOrder['symbol'], 'adj_high')) or ( newOrder['limit_price'] < self.strategyData.getPrice(ts, newOrder['symbol'], 'adj_low'))):
                    #limit price outside of daily range
                    return None
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost as you buy
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                #print "Market effect markup: %f, commission: %f" % ((checkAmount * price * self.calcEffect(maxVol4Day, checkAmount)),self.calcCommission(checkAmount))
                if(cost>self.portfolio.currCash):
                    #Not enough cash to buy stock
                    return None
                
                if abs(newOrder['shares']) > maxVol4Day:
                    if newOrder['shares'] < 0:
                        newOrder['shares'] = -maxVol4Day
                    else:
                        newOrder['shares'] = maxVol4Day
                    newOrder.update()
                    self.order.order.flush()
                #__execute trade__
                #populate fill field in order
                newOrder['fill/timestamp'] = ts
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'BUY') else -newOrder['shares']
                newOrder['fill/cashChange'] = -price
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                self.portfolio.buyTransaction(newOrder)
                #add position
                self.position.addPosition(ts,newOrder['symbol'],newOrder['fill/quantity'],price)
        elif newOrder['order_type'] == 'vwap':
            #volume weighted average price
            price = strategyData.getPrice(ts, newOrder['symbol'], 'adj_open')
            if price == None:
                if noisy:
                    print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
                return None
            elif maxVol4Day == None:
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost as you buy
                price += strategyData.getPrice(ts, newOrder['symbol'], 'adj_close')
                price += strategyData.getPrice(ts, newOrder['symbol'], 'adj_high')
                price += strategyData.getPrice(ts, newOrder['symbol'], 'adj_low')
                price = price / 4.
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                #print "Market effect markup: %f, commission: %f" % ((checkAmount * price * self.calcEffect(maxVol4Day, checkAmount)),self.calcCommission(checkAmount))
                if(cost>self.portfolio.currCash):
                    #Not enough cash to buy stock
                    return None
                
                if abs(newOrder['shares']) > maxVol4Day:
                    if newOrder['shares'] < 0:
                        newOrder['shares'] = -maxVol4Day
                    else:
                        newOrder['shares'] = maxVol4Day
                    newOrder.update()
                    self.order.order.flush()
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost the more you buy.
                #__execute trade__
                #populate fill field in order
                newOrder['fill/timestamp'] = ts
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'BUY') else -newOrder['shares']
                newOrder['fill/cashChange'] = -price
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                self.portfolio.buyTransaction(newOrder) 
                #add position
                self.position.addPosition(ts,newOrder['symbol'],newOrder['fill/quantity'],price)
        else:
            #throw invalid type error
            #print type(newOrder)
            raise TypeError("Not an existing trade type '%s'." % str(newOrder['order_type']))
        newOrder.update()
        self.order.order.flush()
        return price
    
    def sellStock(self,newOrder):
        """
        Comments 'n stuff go here.
        """
        #sellTransaction needs to be expanded and put here instead.
        #newOrder = self.order.addOrder(self.currTimestamp,newOrderDetails.shares,newOrderDetails.symbol,newOrderDetails.orderType,newOrderDetails.duration,newOrderDetails.closeType,newOrderDetails.limitPrice)
        ts = self.getCurrentDataTimestamp() #need a function to get the next available time we can trade
        maxVol4Day = self.getVolumePerDay(newOrder['symbol'], ts)    
        if newOrder['order_type'] == 'moo':
            #market order open
            price = self.strategyData.getPrice(ts, newOrder['symbol'], 'adj_open',self.isTable)
            if price == None:
                if noisy:
                    print "Price data unavailable for",ts,newOrder['symbol']
                return None
            elif maxVol4Day == None:
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                # profit = newOrder['shares'] * price - self.calcCommission(newOrder['shares']) # NEW
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                if newOrder['shares'] > 0:
                    if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                else:
                    if not (self.portfolio.hasStock(newOrder['symbol'],-checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash) and (newOrder['shares'] < 0):
                    #Not enough cash to cover stock
                    return None
                #__execute trade__
                #populate fill field in order
                if abs(newOrder['shares']) > maxVol4Day:
                    if newOrder['shares'] < 0:
                        newOrder['shares'] = -maxVol4Day
                    else:
                        newOrder['shares'] = maxVol4Day
                    newOrder.update()
                    self.order.order.flush()
                newOrder['fill/timestamp'] = ts
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares']
                newOrder['fill/cashChange'] = price #NEW
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                self.portfolio.sellTransaction(newOrder)
                #remove positions according to lifo/fifo
                self.position.removePosition(newOrder['symbol'],newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares'],newOrder['close_type'])
                #self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder['order_type'] == 'moc':
            #market order close
            price = strategyData.getPrice(ts, newOrder['symbol'], 'adj_close')
            if price == None:
                if noisy:
                    print "Price data unavailable for",ts,newOrder['symbol']
                return None
            elif maxVol4Day == None:
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']        
                return None
            else:
                # profit = newOrder['shares'] * price - self.calcCommission(newOrder['shares']) # NEW
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                if newOrder['shares'] > 0:
                    if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                else:
                    if not (self.portfolio.hasStock(newOrder['symbol'],-checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash) and (newOrder['shares'] < 0):
                    #Not enough cash to cover stock
                    return None
                #__execute trade__
                #populate fill field in order
                if abs(newOrder['shares']) > maxVol4Day:
                    if newOrder['shares'] < 0:
                        newOrder['shares'] = -maxVol4Day
                    else:
                        newOrder['shares'] = maxVol4Day
                    newOrder.update()
                    self.order.order.flush()
                newOrder['fill/timestamp'] = ts
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares']
                newOrder['fill/cashChange'] = price
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                self.portfolio.sellTransaction(newOrder)
                #remove positions according to lifo/fifo
                self.position.removePosition(newOrder['symbol'],newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares'],newOrder['close_type'])            
                #self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder['order_type'] == 'limit':
            #limit order
            price = newOrder['limit_price']
            if price == None:
                if noisy:
                    print "Price data unavailable for",ts,newOrder['symbol']
                return None
            elif maxVol4Day == None:
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                # profit = newOrder['shares'] * price - self.calcCommission(newOrder['shares']) # NEW
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                if newOrder['shares'] > 0:
                    if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                else:
                    if not (self.portfolio.hasStock(newOrder['symbol'],-checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash) and (newOrder['shares'] < 0):
                    #Not enough cash to cover stock
                    return None
                #__execute trade__
                #populate fill field in order
                if ((newOrder['limit_price'] > strategyData.getPrice(ts, newOrder['symbol'], 'adj_high')) or ( newOrder['limit_price'] < strategyData.getPrice(ts, newOrder['symbol'], 'adj_low'))):
                    #limit price outside of daily range
                    return None
                if abs(newOrder['shares']) > maxVol4Day:
                    if newOrder['shares'] < 0:
                        newOrder['shares'] = -maxVol4Day
                    else:
                        newOrder['shares'] = maxVol4Day
                    newOrder.update()
                    self.order.order.flush()
                
                #profit = newOrder['shares'] * price - self.calcCommission(newOrder['shares'])
                
                #__execute trade__
                #populate fill field in order
                newOrder['fill/timestamp'] = ts
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares']
                newOrder['fill/cashChange'] = price
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                self.portfolio.sellTransaction(newOrder)
                #remove positions according to lifo/fifo
                self.position.removePosition(newOrder['symbol'],newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares'],newOrder['close_type'])
                #self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        elif newOrder.order_type == 'vwap':
            #volume weighted average price
            price = strategyData.getPrice(ts, newOrder['symbol'], 'adj_open')
            if price == None:
                if noisy:
                    print "Price data unavailable for",ts,newOrder['symbol']
                return None
            elif maxVol4Day == None:
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                if newOrder['shares'] > 0:
                    if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                else:
                    if not (self.portfolio.hasStock(newOrder['symbol'],-checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                price += strategyData.getPrice(ts, newOrder['symbol'], 'adj_close')
                price += strategyData.getPrice(ts, newOrder['symbol'], 'adj_high')
                price += strategyData.getPrice(ts, newOrder['symbol'], 'adj_low')
                price = price / 4.
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash) and (newOrder['shares'] < 0):
                    #Not enough cash to cover stock
                    return None
                #__execute trade__
                #populate fill field in order
                if abs(newOrder['shares']) > maxVol4Day:
                    if newOrder['shares'] < 0:
                        newOrder['shares'] = -maxVol4Day
                    else:
                        newOrder['shares'] = maxVol4Day
                    newOrder.update()
                    self.order.order.flush()
                
                #profit = newOrder['shares'] * price - self.calcCommission(newOrder['shares'])
                newOrder['fill/timestamp'] = ts
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares']
                newOrder['fill/cashChange'] = price
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                self.portfolio.sellTransaction(newOrder)
                #remove positions according to lifo/fifo
                self.position.removePosition(newOrder['symbol'],newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares'],newOrder['close_type'])            
                #self.position.addPosition(ts,newOrder.symbol,newOrder.shares,price)
        else:
            #throw invalid type error
            raise TypeError("Not an existing trade type '%s'." % str(newOrder.order_type))
        newOrder.update()
        self.order.order.flush()
        return price
            
    def execute(self):
        count = 0
        for order in self.order.order.iterrows():
            #print 'ORDER:',order
            #print "order time of expiration:", order['duration'] + order['timestamp']
            #print "currTimestamp:", self.currTimestamp
            if (order['timestamp'] < self.currTimestamp):
                if (order['duration'] + order['timestamp']) >= self.currTimestamp:
                    #print order['fill']
                    if order['fill/timestamp'] == 0:
                        #Have unfilled, valid orders
                        if order['task'].upper() == "BUY":
                            #is a buy
                            if self.portfolio.hasStock(order['symbol'],1):
                                if order['shares']>0:
                                    result = self.buyStock(order)
                                    if noisy:
                                        if result:
                                            print "Succeeded in buying %d shares of %s for %.2f as %s, with close type %s. Placed at: %d.  Current timestamp: %d, order #%d" % (order['shares'], order['symbol'], result, order['order_type'], order['close_type'], order['timestamp'], self.currTimestamp, count)
                                        else:
                                            print "Did not succeed in buying %d shares of %s as %s; not enough cash.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
                                else:
                                    if noisy:
                                        print "Did not succeed in buying %d shares of %s as %s; negative values are not valid buy amounts.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
                            elif self.portfolio.hasStock(order['symbol'],-1):
                                if noisy:
                                    print "Did not succeed in buying %d shares of %s as %s; you must cover your shortsell before you can buy.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
                            else:
                                result = self.buyStock(order)
                                if noisy:
                                    if result:
                                        print "Succeeded in buying %d shares of %s for %.2f as %s. Placed at: %d.  Current timestamp: %d, order #%d" % (order['shares'], order['symbol'], result, order['order_type'], order['timestamp'], self.currTimestamp, count)
                                    else:
                                        print "Did not succeed in buying %d shares of %s as %s.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
                        elif order['task'].upper() == "SELL":
                            # is a sell
                            if order['shares']>0:
                                result = self.sellStock(order)
                                if noisy:
                                    if result:
                                        print "Succeeded in selling %d shares of %s for %.2f as %s, with close type %s.  Current timestamp: %d" % (order['shares'], order['symbol'], result, order['order_type'], order['close_type'], self.currTimestamp)
                                    else:
                                        print "Did not succeed in selling %d shares of %s as %s; not enough owned.  Order valid until %d.  Current timestamp: %d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], self.currTimestamp)
                            else:
                                if noisy:
                                    print "Did not succeed in selling %d shares of %s as %s; you cannot sell a non-positive amount.  Order valid until %d.  Current timestamp: %d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], self.currTimestamp)
                        elif order['task'].upper() == "SHORT":
                            #is a short se;;
                            if self.portfolio.hasStock(order['symbol'],-1):
                                if order['stocks']<0:
                                    result = self.buyStock(order)
                                    if noisy:
                                        if result:
                                            print "Succeeded in short selling %d shares of %s for %.2f as %s, with close type %s. Placed at: %d.  Current timestamp: %d, order #%d" % (-order['shares'], order['symbol'], -result, order['order_type'], order['close_type'], order['timestamp'], self.currTimestamp, count)
                                        else:
                                            print "Did not succeed in short selling %d shares of %s as %s; not enough cash???  How do you not have enough cash for a short sell?.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
                                else:
                                    if noisy:
                                        print "Did not succeed in short selling %d shares of %s as %s; negative values are not valid short sell amounts.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(-order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
                            elif self.portfolio.hasStock(order['symbol'],1):
                                if noisy:
                                    print "Did not succeed in short selling %d shares of %s as %s; you cannot short sell a stock you already own.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(-order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
                            else:
                                result = self.buyStock(order)
                                if noisy:
                                    if result:
                                        print "Succeeded in short selling %d shares of %s for %.2f as %s, with close type %s. Placed at: %d.  Current timestamp: %d, order #%d" % (-order['shares'], order['symbol'], result, order['order_type'], order['close_type'], order['timestamp'], self.currTimestamp, count)
                                    else:
                                        print "Did not succeed in short selling %d shares of %s as %s; not enough cash???  How do you not have enough cash for a short sell?.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(-order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
                        elif order['task'].upper() == "COVER":
                            # is a sell
                            if order['stocks']<0:
                                result = self.sellStock(order)
                                if noisy:
                                    if result:
                                        print "Succeeded in covering %d shares of %s for %.2f as %s, with close type %s.  Current timestamp: %d" % (-order['shares'], order['symbol'], result, order['order_type'], order['close_type'], self.currTimestamp)
                                    else:
                                        print "Did not succeed in covering %d shares of %s as %s; not short enough or not enough cash.  Order valid until %d.  Current timestamp: %d" %(-order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], self.currTimestamp)
                            else:
                                if noisy:
                                    print "Did not succeed in covering %d shares of %s as %s; you cannot cover a non-positive amount.  Order valid until %d.  Current timestamp: %d" %(-order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], self.currTimestamp)
                        else:
                            if noisy:
                                print "'%s' is not a valid task.  Order valid until %d.  Current timestamp: %d" % (order['task'].upper(), order['duration'] + order['timestamp'], self.currTimestamp)
            count += 1
        
        
    def addOrders(self,commands,isTable = True):
        # commands format: ([(sale details),(sale details),...],[(purchase details),(purchase details),...])
        # sale details: (shares,symbol,orderType,duration,closeType,(optional) limit price)
        # purchase details: (shares,symbol,orderType,duration,closeType,(optional) limit price)
        
        # need to reverse the signs on volume for short and cover, eliminate the lifo/fifo field for buys and shorts
        if isTable:
            for stock in commands:
                #if len(stock) == 7:
                #print stock
                newOrder = self.order.addOrder(self.getExecutionTimestamp(),stock[0],stock[1],stock[2],stock[3],stock[4],stock[5],stock[6])
                #else:
                #    newOrder = self.order.addOrder(self.getExecutionTimestamp(),stock[0],stock[1],stock[2],stock[3],stock[4],stock[5])            
                newOrder.append()
                self.order.order.flush()
        else:
            for stock in commands:
                self.order.addOrder(self.getExecutionTimestamp(),stock[0],stock[1],stock[2],stock[3],stock[4],stock[5],stock[6])
                
    def run(self):
        if timersActive:
            print "Simulation timer started."
            totalTime = time.time()
            cycTime = time.clock()
        self.currTimestamp = self.startTime
        self.strategyData.currTimestamp = self.currTimestamp
        i=1
        while self.currTimestamp < self.endTime and self.currTimestamp < time.time() and self.currTimestamp < self.strategyData.timestampIndex[len(self.strategyData.timestampIndex)-2]:
            self.execute()
            self.addOrders(self.strategy(self.portfolio,self.position,self.currTimestamp,self.strategyData))
            if timersActive and not noisy:
                print "Strategy at %i took %.4f secs"%(self.currTimestamp,(time.clock()-cycTime))
                i+=1
                cycTime = time.clock()
            if noisy and not timersActive:
                print "\nStrategy at %d completed successfully." % self.currTimestamp
                print "Current portfolio value: %.2f."%(self.portfolio.currCash + self.strategyData.calculatePortValue(self.portfolio.currStocks,self.currTimestamp, self.isTable))
                print "Current stocks: %s.\n\n"%self.portfolio.currStocks
            if noisy and timersActive:
                print "\nStrategy at %i took %.4f secs"%(self.currTimestamp,(time.clock()-cycTime))
                print "Strategy at %d completed successfully." % self.currTimestamp
                print "Current portfolio value: %.2f."%(self.portfolio.currCash + self.strategyData.calculatePortValue(self.portfolio.currStocks,self.currTimestamp, self.isTable))
                print "Current stocks: %s.\n\n"%self.portfolio.currStocks
                i+=1
                cycTime = time.clock()  
            
            self.currTimestamp += self.interval
            self.strategyData.currTimestamp = self.currTimestamp
        if noisy:
            print "Simulation complete."
        if timersActive:
            print "Simulation complete in %i seconds."%(time.time() - totalTime)
        self.portfolio.close()
        self.position.close()
        self.order.close()
        if isTable:
            self.strategyData.close()



cash = 0; comPerShare = 0.0; minCom = 0.; startTime = 0; endTime = 0; timeStep = 0; maxEffect = 0.; decayCycles = 0
noisy = False; timersActive = False; isTable = False; arrayFile = 'datafiles/defaultArrayFile.pk'; pytablesFile = 'datafiles/defaultPytablesFile.h5'
def main():
    global cash,comPerShare,minCom,startTime,endTime,timeStep,maxEffect,decayCycles,noisy,timersActive,isTable,arrayFile,pytablesFile
    # NOTE: the OptionParser class is currently not necessary, as we can just access sys.argv[1:], but if we
    # want to implement optional arguments, this will make it considerably easier.
    parser = OptionParser()
    
    # parser.parse_args() returns a tuple of (options, args)
    # As of right now, we don't have any options for our program, so we only care about the three arguments:
    # config file, strategy module name, strategy main function name
    args = parser.parse_args()[1]
    
    if len(args) != 3 and len(args) != 2:
        print "FAILURE TO INCLUDE THE CORRECT NUMBER OF ARGUMENTS; TERMINATING."
        return
    
    configFile = args[0]
    if len(args) == 3:
        stratName = args[2]
    else:
        stratName = "strategyMain"
    #print sys.path
    open(configFile,'r')
    for fileName in ["configfiles/default.ini",configFile]:
        thisFile = open(fileName,'r')
        for line in thisFile.readlines():
            # Separate the command in the config file from the arguments
            if not ('#' in line):
                line = line.strip().split('=')
                command = line[0].strip().upper()
                if(command == 'ARRAYFILE' or command =='PYTABLESFILE'):
                    if len(line)>1:
                        vals = line[1].split()
                    else:
                        vals = []  
                else:
                    if len(line)>1:
                        vals = line[1].upper().split()
                    else:
                        vals = []  
                # Parse commands, look for correct number of arguments, do rudimentary error checking, apply to simulator as appropriate
                if command == 'CASH':
                    if len(vals) != 1:
                        print "WRONG NUMBER OF ARGUMENTS FOR CASH!"
                    else:
                        try:
                            cash = float(vals[0])
                        except ValueError:
                            print "ARGUMENT FOR CASH IS NOT A FLOAT!"
                
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
                elif command == "DATATYPE":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR DATATYPE."
                    else:
                        if vals[0] == "TABLE":
                            isTable = True
                        elif vals[0] == "ARRAY":
                            isTable = False
                        else:
                            print "%s IS NOT A VALID PARAMETER FOR DATATYPE." % vals[0]  
                elif command == "ARRAYFILE":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR ARRAYFILE."
                    else:
                        try:
                            arrayFile = str(vals[0])
                        except ValueError:
                            print "ARRAYFILE REQUIRES A STRING INPUT"
                elif command == "PYTABLESFILE":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR PYTABLESFILE."
                    else:
                        try:
                            pytablesFile = str(vals[0])
                        except ValueError:
                            print "PYTABLESFILE REQUIRES A STRING INPUT"
                elif command == "NOISY":
                    noisy = True
                elif command == "TIMER":
                    timersActive = True
                elif command != '':
                        print "Unrecognized command '%s'.  Note: some commands may not yet be implemented.  E-mail pdohogne3@gatech.edu if a command is missing." % command
        thisFile.close()
    if noisy:
        print "Config file parsed successfully.  Starting simulation."
    
    
    # Add the strategies subdirectory to the system path so Python can find the module
    sys.path.append(sys.path[0] + '/strategies')
    myStrategy = eval("__import__('%s').%s" % (args[1],stratName) )
    mySim = Simulator(cash,{}, myStrategy, startTime, endTime, timeStep, minCom, comPerShare, isTable, maxEffect, arrayFile, pytablesFile)
    # Add the timestamps
    if isTable:
        mySim.times = mySim.addTimeStamps()
        mySim.strategyData.timestampIndex = mySim.times
    else:
        mySim.times = mySim.strategyData.timestampIndex
    #self.strategyData.populateArray(mySim.times)
    mySim.run()

# This ensures the main function runs automatically when the program is run from the command line, but 
# not if the file somehow gets imported from something else.  Nifty, eh?
if __name__ == "__main__":
    main()