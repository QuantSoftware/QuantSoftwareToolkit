#import optimizers.BollingerOptimizer as Optimizer
import optimizers.BollingerOptimizer as Optimizer
import models.PortfolioModel, models.PositionModel, models.OrderModel, models.StrategyDataModel
import tables as pt, numpy as np
from optparse import OptionParser
import sys, time
import Portfolio, Position, Order, DataAccess as da , StrategyData
import os
import dircache
import numpy as np
#import curveFittingOptimizer
#import optimizers.BollingerOptimizer as Optimizer

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure



class Simulator():
    def __init__(self, cash, stocks, startTime, endTime, interval, minCom, comPerShare, isTable, maxEffect, arrayFile, listOfStocksFile):
        # strategy contains a reference to the strategy method specified in the command line
#        self.strategy = strategy
        # startTime/endTime are the timestamps marking the beginning and end of the time for which the simulation should run
        self.startTime = startTime
        self.currTimestamp = startTime
        self.endTime = endTime
        # interval is the amount of time between iterations of the strategy
        self.interval = interval
        # minCom is the minimum commission per transaction
        self.minCom = minCom
        # comPerShare is the calculated commission per share--if this is greater than the minimum commission, this is what gets used
        self.comPerShare = comPerShare
        # timeStampIndex and currDataTimeIndex are markers to track the current position in the list of timestamps
        self.timeStampIndex = 0
        self.currDataTimeIndex = 0
        # maxEffect is the maximum percentage change in price a single transaction can have on the actual market price
        self.maxEffect = maxEffect
        # times becomes the list of timestamps
        self.times =  []
        # isTable tells the simulator whether to use the table- or array-specific methods
        self.isTable = isTable
        
        #starting portfolio, position, and order initializations
        self.portfolio = Portfolio.Portfolio(cash, stocks)
        self.position = Position.Position()
        self.order = Order.Order(self.isTable)
        #populate the strategyData with the relevant type of data storage
        if isTable:
            
            
#            self.h5f= pt.openFile(pytablesFile, mode = "a") # if mode ='w' is used here then the file gets overwritten!

            listOfPaths=list()
            #listOfPaths.append("C:\\generated data files\\one stock per file\\maintain folder structure\\US_NASDAQ\\")
            #listOfPaths.append("C:\\temp\\")
            #listOfPaths.append("C:\\tempoutput\\")
            listOfPaths.append("/hzr71/research/QSData/tempdata/") #Modification for gekko
            self.listOfStocks= self.getStocks(listOfStocksFile, listOfPaths)
            
            self.dataAccess= da.DataAccess (True, listOfPaths, "/StrategyData", "StrategyData", True, self.listOfStocks, self.startTime, self.endTime)
            self.strategyData = StrategyData.StrategyData("someRandomStringToNotBreakTheCode", self.dataAccess, self.isTable)
            
#        else:
#            self.strategyData = StrategyData.StrategyData(arrayFile,self.isTable) 

    def getStocks(self, pathToFile, listOfPaths):
        
        listOfStocks=list()
        if (os.path.exists(pathToFile)):
           print "Reading in stock names from file..." 
           f= open(pathToFile)
           lines= f.readlines()
           f.close()
           for line1 in lines:
             listOfStocks.append(line1.partition("\n")[0])
             #for done
        else:
            #Path does not exist
            print "Reading in all stock names..."
            fileExtensionToRemove=".h5"   
            
            for path in listOfPaths:
               stocksAtThisPath=list ()
               
               stocksAtThisPath= dircache.listdir(str(path))
               #Next, throw away everything that is not a .h5 And these are our stocks!
               stocksAtThisPath = filter (lambda x:(str(x).find(str(fileExtensionToRemove)) > -1), stocksAtThisPath)
               #Now, we remove the .h5 to get the name of the stock
               stocksAtThisPath = map(lambda x:(x.partition(str(fileExtensionToRemove))[0]),stocksAtThisPath)
               
               for stock in stocksAtThisPath:
                   listOfStocks.append(stock)
        return listOfStocks
    #readStocksFromFile done
    
    
    
    def addTimeStamps(self):
        # generates the list of timestamps
        global timersActive
        temp = []

        if timersActive:
            print 'Generating valid timestamps'
            cnt = 0
            cycTime = time.time()
#        for i in self.strategyData.strategyData.iterrows():
        for ts in self.dataAccess.getTimestampArray():    
            if ts not in temp:
                temp.append(ts)
            if timersActive:
                if(cnt%1000000==0):
                    print '%i rows finished: %i secs elapsed'%(cnt,time.time()-cycTime)
                cnt+=1
        if timersActive:
            print 'all rows added: %i secs elapsed'%(time.time()-cycTime)      
        #Put the list in order, convert it to a NumPy array  
        temp.sort()
        temp = np.array(temp)
        return temp
    
    def calcCommission(self, volume):
        '''
        @summary: returns the commission on a given trade given the volume 
        '''
        return max(minCom,volume * self.comPerShare)
    
    def getCurrentDataTimestamp(self):
        '''
        @summary: returns the timestamp of the most recent data available
        '''
        while self.times[self.currDataTimeIndex+1]<self.currTimestamp:
            self.currDataTimeIndex += 1
        return self.times[self.currDataTimeIndex]
    
    def getExecutionTimestamp(self):
        '''
        @summary: returns the timestamp of the current execution timestamp
        @attention: Orders placed on the last day can not be executed after it..so they will be executed on that day. Possible bug?
        '''
        while self.times[self.timeStampIndex]<self.currTimestamp:
            self.timeStampIndex += 1
        
        if (self.timeStampIndex+1 < len (self.times)):
             idealTime = self.times[self.timeStampIndex+1]
        else:
             idealTime = self.times[self.timeStampIndex] 
        
        return idealTime
        
    def calcEffect(self, maxVol, shares):
        # calculates the effect in the market of a given trade
        return float(shares)/maxVol * self.maxEffect
        
#    def getVolumePerDay(self, symbol, timestamp):
#        '''
#        COMMENT BY SHREYAS JOSHI. THIS FUNCTION IS NOT NECESSARY. 22 JUN 2010. HENCE REMOVING IT.
#        @summary: returns the volume of a given stock for the given day (used in conjunction with calcEffect). Call with startTime = endTime = desired timestamp to get just that timestamp
#        '''  
#
#
##        stocks = self.strategyData.getStocks(timestamp, timestamp+1, symbol)
#        stocks= self.dataAccess.getData(symbol, 'volume', timestamp, timestamp+1) # we need only the volume here
#        if len(stocks) > 0:
#            myStockasDict = stocks[0] #Grab the first dictionary in the list
#            return myStockasDict['volume'] # Get the volume
#        return None   
            
    def buyStock(self, newOrder):
        '''
        @summary: function takes in an instance of OrderDetails, executes the changes to the portfolio and adds the order to the order table
        @param newOrder: an instance of OrderDetails representing the new order
        @warning: The Order should not be added to the order table before calling this function
        '''
        ts = self.getCurrentDataTimestamp()
        maxVol4Day = self.dataAccess.getStockDataItem(newOrder['symbol'], 'volume', ts)#self.getVolumePerDay(newOrder['symbol'], ts)
        if newOrder['order_type'] == 'moo':
            #market order open
#            price = strategyData.getPrice(ts, newOrder['symbol'], 'adj_open')
            price = self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_open', ts) 
            if price == None or np.isnan (price):
                if noisy:
                    print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
                return None
            elif maxVol4Day == None or np.isnan(maxVol4Day):
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                print "Checking cash..."
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost as you buy
                cost = (checkAmount * price[0]['adj_open'] + (checkAmount * price[0]['adj_open'] * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash):
                    #Not enough cash to buy stock
                    print "Not enough cash to buy stock."
                    #print "Apparently not enough cash. I don't believe this. Current cash: " + str (self.portfolio.currCash) + " total cost: "+ str (cost)+ ", cost of one share: "+str (self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_open', ts))
                    
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
#            price = self.strategyData.getPrice(ts, newOrder['symbol'], 'adj_close')
#            price = self.dataAccess.getData(newOrder['symbol'], 'adj_close', ts, ts)[0]['adj_close']
            
            
            price = self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_close', ts)
            if price == None or np.isnan (price):
                if noisy:
                    print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
                return None
            elif maxVol4Day == None or np.isnan(maxVol4Day):
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else: 
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost as you buy
#                cost = (checkAmount  + (checkAmount  * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash):
                    #Not enough cash to buy stock
                    print "Not enough cash. Current cash: " + str (self.portfolio.currCash) + " total cost: "+ str (cost)+ ", cost of one share: "+str (self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_close', ts))
                    
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
                self.portfolio.buyTransaction(newOrder)
                #add position
                self.position.addPosition(ts,newOrder['symbol'],newOrder['fill/quantity'],price)
        elif newOrder['order_type'] == 'limit':
            #limit order
            price = newOrder['limit_price']
            if price == None or np.isnan (price):
                if noisy:
                    print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
                return None
            elif maxVol4Day == None or np.isnan(maxVol4Day):
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
#                if ((newOrder['limit_price'] > self.strategyData.getPrice(ts, newOrder['symbol'], 'adj_high')) or ( newOrder['limit_price'] < self.strategyData.getPrice(ts, newOrder['symbol'], 'adj_low'))):
                if ((newOrder['limit_price'] > self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_high', ts)) or ( newOrder['limit_price'] < self.dataAccess.getData(newOrder['symbol'], 'adj_low', ts))):   
                    #limit price outside of daily range
                    return None
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost as you buy
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
        elif newOrder['order_type'] == 'vwap':
            #volume weighted average price
#            price = strategyData.getPrice(ts, newOrder['symbol'], 'adj_open')
#            price = self.dataAccess.getData(newOrder['symbol'], 'adj_open', ts, ts)[0]['adj_close']
            price = self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_open', ts)
            if price == None or np.isnan (price):
                if noisy:
                    print "Price data unavailable for ts:",ts,'stock:',newOrder['symbol']
                return None
            elif maxVol4Day == None or np.isnan(maxVol4Day):
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                # New is cost the original total price (price * shares) + effect*Total Price
                # Basically, you raise the cost as you buy
                price += self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_close', ts)#[0]['adj_close'] #strategyData.getPrice(ts, newOrder['symbol'], 'adj_close')
                price += self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_high', ts)#[0]['adj_high'] #strategyData.getPrice(ts, newOrder['symbol'], 'adj_high')
                price += self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_low', ts)#[0]['adj_low'] #strategyData.getPrice(ts, newOrder['symbol'], 'adj_low')
                price = price / 4.
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
            raise TypeError("Not an existing trade type '%s'." % str(newOrder['order_type']))
        newOrder.update()
        self.order.order.flush()
        return price
    
    def sellStock(self,newOrder):
        '''
        @summary: function takes in an instance of OrderDetails, executes the changes to the portfolio and adds the order to the order table
        @param newOrder: an instance of OrderDetails representing the new order
        @warning: The Order should not be added to the order table before calling this function
        '''
        ts = self.getCurrentDataTimestamp() #need a function to get the next available time we can trade
        maxVol4Day = self.dataAccess.getStockDataItem(newOrder['symbol'], 'volume', ts)#self.getVolumePerDay(newOrder['symbol'], ts)    
        if newOrder['order_type'] == 'moo':
            #market order open
            price = self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_open', ts)#[0]['adj_open'] #self.strategyData.getPrice(ts, newOrder['symbol'], 'adj_open')
            if price == None or np.isnan (price):
                if noisy:
                    print "Price data unavailable for",ts,newOrder['symbol']
                return None
            elif maxVol4Day == None or np.isnan(maxVol4Day):
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                if newOrder['task'].upper() == 'SELL':
                    if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        print "Not enough shares owned to sell the requested amount"
                        return None
                else:
                    if not (self.portfolio.hasStock(newOrder['symbol'],-checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        print "Not enough shares owned to sell the requested amount"
                        return None
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash) and (newOrder['shares'] < 0):
                    #Not enough cash to cover stock
                    print "Not enough cash to cover stock"
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
        elif newOrder['order_type'] == 'moc':
            #market order close
            price = self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_close', ts)#[0]['adj_close'] #strategyData.getPrice(ts, newOrder['symbol'], 'adj_close')
            if price == None or np.isnan (price):
                if noisy:
                    print "Price data unavailable for",ts,newOrder['symbol']
                return None
            elif maxVol4Day == None or np.isnan(maxVol4Day):
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']        
                return None
            else:
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                if newOrder['shares'] > 0:
                    if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        print "Not enough shares owned to sell the requested amount"
                        return None
                else:
                    if not (self.portfolio.hasStock(newOrder['symbol'],-checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        print "Not enough shares owned to sell the requested amount"
                        return None
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash) and (newOrder['shares'] < 0):
                    #Not enough cash to cover stock
                    print "Not enough cash to cover stock"
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
        elif newOrder['order_type'] == 'limit':
            #limit order
            price = newOrder['limit_price']
            if price == None or np.isnan (price):
                if noisy:
                    print "Price data unavailable for",ts,newOrder['symbol']
                return None
            elif maxVol4Day == None or np.isnan(maxVol4Day):
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                if newOrder['shares'] > 0:
                    if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        print "Not enough shares owned to sell the requested amount"
                        return None
                else:
                    if not (self.portfolio.hasStock(newOrder['symbol'],-checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        return None
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash) and (newOrder['shares'] < 0):
                    #Not enough cash to cover stock
                    print "Not enough cash to cover stock"
                    return None
                #__execute trade__
                #populate fill field in order
#                if ((newOrder['limit_price'] > strategyData.getPrice(ts, newOrder['symbol'], 'adj_high')) or ( newOrder['limit_price'] < strategyData.getPrice(ts, newOrder['symbol'], 'adj_low'))):
                if ((newOrder['limit_price'] > self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_high', ts)) or ( newOrder['limit_price'] < self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_low', ts))):    
                    #limit price outside of daily range
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
                newOrder['fill/quantity'] = newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares']
                newOrder['fill/cashChange'] = price
                newOrder['fill/commission'] = self.calcCommission(newOrder['shares'])
                newOrder['fill/impactCost'] = newOrder['shares'] * price * self.calcEffect(maxVol4Day, newOrder['shares']) # This is the CHANGE in the total cost - what effect the volume has
                #add trade to portfolio
                self.portfolio.sellTransaction(newOrder)
                #remove positions according to lifo/fifo
                self.position.removePosition(newOrder['symbol'],newOrder['shares'] if (newOrder['task'].upper() == 'SELL') else -newOrder['shares'],newOrder['close_type'])
        elif newOrder.order_type == 'vwap':
            #volume weighted average price
            price = self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_open', ts)#[0]['adj_open'] #strategyData.getPrice(ts, newOrder['symbol'], 'adj_open')
            if price == None or np.isnan (price):
                if noisy:
                    print "Price data unavailable for",ts,newOrder['symbol']
                return None
            elif maxVol4Day == None or np.isnan(maxVol4Day):
                if noisy:
                    print "Volume Data Not Available for ts:", ts, 'stock:', newOrder['symbol']
                return None
            else:
                checkAmount = min(abs(newOrder['shares']),maxVol4Day)
                if newOrder['shares'] > 0:
                    if not (self.portfolio.hasStock(newOrder['symbol'],checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        print "Not enough shares owned to sell the requested amount"
                        return None
                else:
                    if not (self.portfolio.hasStock(newOrder['symbol'],-checkAmount)): # NEW
                        #Not enough shares owned to sell requested amount
                        print "Not enough shares owned to sell the requested amount"
                        return None
                price += self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_close', ts)#[0]['adj_close'] #strategyData.getPrice(ts, newOrder['symbol'], 'adj_close')
                price += self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_high', ts)#[0]['adj_high'] #strategyData.getPrice(ts, newOrder['symbol'], 'adj_high')
                price += self.dataAccess.getStockDataItem(newOrder['symbol'], 'adj_low', ts)#[0]['adj_low'] #strategyData.getPrice(ts, newOrder['symbol'], 'adj_low')
                price = price / 4.
                cost = (checkAmount * price + (checkAmount * price * self.calcEffect(maxVol4Day, checkAmount))) + self.calcCommission(checkAmount)
                if(cost>self.portfolio.currCash) and (newOrder['shares'] < 0):
                    #Not enough cash to cover stock
                    print "Not enough cash to cover stock"
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
        else:
            #throw invalid type error
            raise TypeError("Not an existing trade type '%s'." % str(newOrder.order_type))
        newOrder.update()
        self.order.order.flush()
        return price
            
    def execute(self):
        '''
        @summary: This function iterates through the orders and attempts to execute all the ones that are still valid and unfilled
        '''
        count = 0
        for order in self.order.getOrders():
            if (order['timestamp'] < self.currTimestamp):
                if (order['duration'] + order['timestamp']) >= self.currTimestamp:
                    if order['fill/timestamp'] == 0:
                        #Have unfilled, valid orders
                        if order['task'].upper() == "BUY":
                            #is a buy
                            if self.portfolio.hasStock(order['symbol'],1):
                                if order['shares']>0:
                                    result = self.buyStock(order)
                                    if noisy:
                                        if result is not None:
                                            print "Succeeded in buying %d shares of %s for %.2f as %s, with close type %s. Placed at: %d.  Current timestamp: %d, order #%d" % (order['shares'], order['symbol'], result, order['order_type'], order['close_type'], order['timestamp'], self.currTimestamp, count)
                                        #else:
                                            #print "THIS IS MOST LIKELY WRONG- Did not succeed in buying %d shares of %s as %s; not enough cash.  Order valid until %d. Placed at: %d.  Current timestamp: %d, order #%d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], order['timestamp'], self.currTimestamp, count)
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
                                    #else:
                                        #print "Did not succeed in selling %d shares of %s as %s; not enough owned.  Order valid until %d.  Current timestamp: %d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], self.currTimestamp)
                            else:
                                if noisy:
                                    print "Did not succeed in selling %d shares of %s as %s; you cannot sell a non-positive amount.  Order valid until %d.  Current timestamp: %d" %(order['shares'], order['symbol'], order['order_type'], order['duration'] + order['timestamp'], self.currTimestamp)
                        elif order['task'].upper() == "SHORT":
                            #is a short sell
                            if self.portfolio.hasStock(order['symbol'],-1):
                                if order['shares']>0:
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
                            # is a cover
                            if order['shares']>0:
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
        
        
    def addOrders(self,commands):
        '''
        @summary: takes in commands (return value of strategy), parses it, and adds it in the correct format to the order data storage
        '''
        if self.isTable:
            for stock in commands:
                newOrder = self.order.addOrder(self.getExecutionTimestamp(),stock[0],stock[1],stock[2],stock[3],stock[4],stock[5],stock[6])
                newOrder.append()
                self.order.order.flush()
        else:
            for stock in commands:
                self.order.addOrder(self.getExecutionTimestamp(),stock[0],stock[1],stock[2],stock[3],stock[4],stock[5],stock[6])
                
    def run(self):
        '''
        @summary: Run the simulation
        '''
        
        optimizer= Optimizer.Optimizer(self.listOfStocks)
        #optimizer= curveFittingOptimizer.Optimizer(self.listOfStocks)
        timestamps= list(self.dataAccess.getTimestampArray())
        portfolioValList= list()
      
        ctr=0
        while (timestamps[ctr]< self.startTime):
            ctr+=1
            #while loop done
            
               
        self.currTimestamp = timestamps[ctr] #self.startTime
        
        ctr2= ctr
        
        while (timestamps[ctr2]< self.endTime):
            ctr2+=1
            if (ctr2>= len(timestamps)):
                break
            
            #while loop done
            
        if (ctr2>= len (timestamps)):
            self.endTime= timestamps[ctr2-1]
        else:
            self.endTime= timestamps[ctr2]    
        
        if timersActive:
            print "Simulation timer started at "+ str(self.currTimestamp)
            totalTime = time.time()
            cycTime = time.clock()
            
#        self.strategyData.currTimestamp = self.currTimestamp
        i=1
        while self.currTimestamp < self.endTime and self.currTimestamp < time.time(): # and self.currTimestamp < self.strategyData.timestampIndex[len(self.strategyData.timestampIndex)-2]: ************POSSIBLE BUG***** JUST TRYING OUT
            # While not yet reached the end timestamp AND not yet caught up to present AND not yet reached the end of the data
            # execute the existing orders, then run the strategy and add the new orders
            
            
            
            beforeExec=time.clock()
            self.execute()
            afterExec= time.clock()
#            self.addOrders(self.strategy(self.portfolio,self.position,self.currTimestamp,self.strategyData))
#            self.addOrders(optimizer.execute(self.portfolio,self.position,self.currTimestamp,self.strategyData))
            beforeAddOrders= time.clock()
            self.addOrders(optimizer.execute(self.portfolio,self.position,self.currTimestamp,self.strategyData, self.dataAccess))
            afterAddOrders= time.clock()
            
            if noisy or timersActive:
                print '' #newline                
            if mtm:
                #portValue = self.portfolio.currCash + self.strategyData.calculatePortValue(self.portfolio.currStocks,self.currTimestamp)
                portValue= float (0.0)
                print "| %i %.2f |"%(self.currTimestamp,portValue) + "  Value from portfolio class: " +  str (self.portfolio.calcPortfolioValue(self.currTimestamp, self.dataAccess))
            if timersActive and not noisy:
                print "Strategy at %i took %.4f secs"%(self.currTimestamp,(time.clock()-cycTime))
                i+=1
                cycTime = time.clock()
            if noisy and not timersActive:
                portValue = (self.portfolio.calcPortfolioValue(self.currTimestamp, self.dataAccess)) #self.portfolio.currCash + self.strategyData.calculatePortValue(self.portfolio.currStocks,self.currTimestamp)
                portfolioValList.append(portValue)
                
                print "Strategy at %d completed successfully." % self.currTimestamp
                print "Current cash: " + str(self.portfolio.currCash)
                print "Current stocks: %s."%self.portfolio.currStocks
                print "Current portfolio value: "+ str(portValue)+"\n\n"
                #print "Current portfolio value: %.2f.\n\n"%(portValue)
            if noisy and timersActive:
                portValue =  float (self.portfolio.calcPortfolioValue(self.currTimestamp, self.dataAccess)) #self.portfolio.currCash + self.strategyData.calculatePortValue(self.portfolio.currStocks,self.currTimestamp)
                portfolioValList.append(portValue)
                
                print "Strategy at %i took %.4f secs"%(self.currTimestamp,(time.clock()-cycTime))
                print "Exec function took: " + str(afterExec - beforeExec)
                print "Time for addorders: " + str(afterAddOrders - beforeAddOrders)
                
                print "Strategy at %d completed successfully." % self.currTimestamp
                #print "Current cash: %.2f."%(self.portfolio.currCash)
                print "Current cash: " + str(self.portfolio.currCash)
                print "Current stocks: %s."%self.portfolio.currStocks
                #print "Current portfolio value: %.2f.\n\n"%(portValue)
                print "Current portfolio value: "+ str(portValue)+"\n\n"
                i+=1
                cycTime = time.clock() 

 
                        
            #self.currTimestamp += self.interval   -- Unfortunately this does not work becuase of daylight saving time complications
            ctr+=1
            self.currTimestamp= timestamps[ctr] 
            #self.strategyData.currTimestamp = self.currTimestamp
        if noisy:
            print "Simulation complete."
        if timersActive:
            print "Simulation complete in %i seconds."%(time.time() - totalTime)
        
        self.portfolio.close()
        self.position.close()
        self.order.close()
        #self.strategyData.close()
        
        
        #plotting the portfolio value
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.plot (portfolioValList)
        ax.set_title('Portfolio value')
        ax.grid(True)
        ax.set_xlabel('time')
        ax.set_ylabel('$')
        canvas.print_figure('portfolio')
        
        
        
        #def run ends

      
cash = 0; comPerShare = 0.0; minCom = 0.; startTime = 0; endTime = 0; timeStep = 0; maxEffect = 0.; decayCycles = 0
noisy = False; timersActive = False; mtm = False; isTable = False; arrayFile = 'datafiles/defaultArrayFile.pk'; listOfStocksFile="someRandomString"
def main():
    global cash,comPerShare,minCom,startTime,endTime,timeStep,maxEffect,decayCycles,noisy,timersActive,mtm,isTable,arrayFile,listOfStocksFile
    # NOTE: the OptionParser class is currently not necessary, as we can just access sys.argv[1:], but if we
    # want to implement optional arguments, this will make it considerably easier.
    parser = OptionParser()
    
    # parser.parse_args() returns a tuple of (options, args)
    # As of right now, we don't have any options for our program, so we only care about the three arguments:
    # config file, strategy module name, strategy main function name
    args = parser.parse_args()[1]
    
#    if len(args) != 3 and len(args) != 2:
#        print "FAILURE TO INCLUDE THE CORRECT NUMBER OF ARGUMENTS; TERMINATING."
#        return
    if len(args) != 1:
        print "FAILURE TO INCLUDE THE CORRECT NUMBER OF ARGUMENTS; TERMINATING."
        return


    configFile = 'configfiles/'+args[0]
#    if len(args) == 3:
#        stratName = args[2]
#    else:
#        stratName = "strategyMain"
    if noisy:
        print "About to parse configuration files.  Any invalid fields found in the user-specified file will use the relevant value from the default file instead."
    for fileName in ["configfiles/default.ini",configFile]:
        if noisy:
            print "Parsing %s now..." % filename[12:]
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
                elif command == "MTM":
                    mtm = True
                elif command == "LISTOFSTOCKSFILE":
                    listOfStocksFile= str (vals[0])
                    if not (os.path.exists(listOfStocksFile)):
                       print "File containing list of stocks does not exist. Will read in all files at specified paths."
#                       raise ValueError
                   
                elif command != '':
                        print "Unrecognized command '%s'." % command
        thisFile.close()
    if noisy:
        print "Config files finished parsing.  Starting simulation."
    
    
    # Add the strategies subdirectory to the system path so Python can find the module
    sys.path.append(sys.path[0] + '/strategies')
#    myStrategy = eval("__import__('%s').%s" % (args[1],stratName) )
    mySim = Simulator(cash,{}, startTime, endTime, timeStep, minCom, comPerShare, isTable, maxEffect, arrayFile, listOfStocksFile)
    # Add the timestamps
    if isTable:
        mySim.times = mySim.addTimeStamps()
        #mySim.strategyData.timestampIndex = mySim.times
    else:
        pass
        #mySim.times = mySim.strategyData.timestampIndex
    mySim.run()

# This ensures the main function runs automatically when the program is run from the command line, but 
# not if the file somehow gets imported from something else.  Nifty, eh?
if __name__ == "__main__":
    main()