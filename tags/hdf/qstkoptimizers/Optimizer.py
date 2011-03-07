'''
Created on May 28, 2010

@author: Shreyas Joshi
@contact: shreyasj@gatech.edu
'''

import DataAccess as da
import tables as pt
import math
import numpy as np

class Optimizer(object):
    '''
    @summary: The optimizer class is supposed to get the alpha values and data on the current portfolio to make a decision on what trades to make.
    
    '''

# one day in unix time
    

    def __init__(self, listOfStocks):
        '''
        Constructor
        '''
#        self.alphah5f= pt.openFile("randomAlpha.h5", mode = "a") # if mode ='w' is used here then the file gets overwritten!
        self.listOfLoosingStocks=list()
        self.noOfDaysStockHasBeenLoosingValue=list()
        
        self.listOfStocks= list(listOfStocks)
        self.DAY = 86400
        staticDataItemsList= list()
        staticDataItemsList.append("blah")
        dataItemsList= list()
        dataItemsList.append("alphaValue")
        self.minCom= 5.00
        self.ComPerShare = 0.01
#        self.alphaData= da.DataAccess(False,"randomAlpha.h5","/alphaData", "alphaData", True, listOfStocks, None, dataItemsList)
    #def __init__ ends
        
    def strategyOne (self, portfolio,positions,timestamp,stockInfo, dataAccess):
     output=[]
     adjOpenData= dataAccess.getMatrix (self.listOfStocks, "adj_open", timestamp- 2*self.DAY, timestamp- self.DAY)
     
     if adjOpenData is not None:
         #choose the biggest loser
         ctr=0
         currentBiggestLoss= - float("infinity")
         currentBiggestLoserIndex=-1
         while (ctr<len(self.listOfStocks)):
#             print "adjOpenData shape: " + str(adjOpenData.shape) + ", ctr: " + str(ctr) + ", len(self.listOfStocks): " + str(len(self.listOfStocks))
             if (adjOpenData[0][ctr] > adjOpenData[1][ctr]):
                 #Which means the stock lost value
                 if ((adjOpenData[0][ctr] - adjOpenData[1][ctr])/adjOpenData[0][ctr] > currentBiggestLoss): #biggest % loss
                     currentBiggestLoss= (adjOpenData[0][ctr] - adjOpenData[1][ctr])
                     currentBiggestLoserIndex= ctr
             ctr+=1
             #While loop done
         #Now  we have the stock which lost the most value. We buy it and also put in a sell order for 2 days later
         
         if (currentBiggestLoserIndex != -1):
             order= stockInfo.OutputOrder()
             order.symbol= self.listOfStocks[currentBiggestLoserIndex]
             order.volume= 10
             order.task= 'buy'
             order.orderType = 'moc'
             order.duration = self.DAY
             
             newOrder = order.getOutput()
             
             if newOrder != None:
                output.append(newOrder)
             else:
                 print "ERROR! ERROR! ERROR!"
             #if (currentBiggestLoserIndex != -1): ends
         #if adjOpenData is not None: ends
     else:
         print "adjOpenData is None!"
         #else ends    
     #Now to decide which stocks to sell
     currentPositions= positions.getPositions()
     for stock in portfolio.currStocks:
         for pos in currentPositions:
          if (str(pos['symbol'])== str(stock)):   
           if ((pos['timestamp'] )< timestamp - 2*self.DAY):
               temp=  dataAccess.getStockDataItem(pos['symbol'], 'adj_close', timestamp)
               if not (np.isnan(temp)):
                if ((pos['purchase_price'] + (pos['shares']*self.ComPerShare))< temp):
                 order= stockInfo.OutputOrder()
                 order.symbol= stock
                 order.volume= pos['shares']
                 order.task= 'sell'
                 order.orderType = 'moc'
                 order.closeType = 'fifo'
                 order.duration = self.DAY
                 newOrder = order.getOutput()
                 
                 if newOrder != None:
                   output.append(newOrder)
                 else:
                   print "ERROR! ERROR! ERROR!"
        #for pos in currentPositions: ends         
     return output  
        
    def strategyTwo (self, portfolio,positions,timestamp,stockInfo, dataAccess):
        #Here we track all the stocks that continuously loose value- then buy them when they stop loosing value. Then hold them until they keep
        #gaining value. Then sell them
        
        
        output=[]
        
        #adjOpenData= dataAccess.getMatrix (self.listOfStocks, "adj_open", timestamp- 2*self.DAY, timestamp- self.DAY)
        
        adjOpenData= dataAccess.getMatrixFromTS (self.listOfStocks, "adj_open", timestamp, -1)
        
#        print "list of loosing stocks: "+ str (self.listOfLoosingStocks)
#        print "current positions: " + str(positions.getPositions())
#        print "no of days: " + str (self.noOfDaysStockHasBeenLoosingValue)
        
        if (adjOpenData is not None):
            ctr=0
            while (ctr< len(self.listOfStocks)):
                if (adjOpenData[0][ctr] > adjOpenData[1][ctr]):
                    
                    try:
                        index2= self.listOfLoosingStocks.index(self.listOfStocks[ctr])
                        self.noOfDaysStockHasBeenLoosingValue[index2]+=1
                    except:
                        #stock not found in the list
                        self.listOfLoosingStocks.append(self.listOfStocks[ctr])
                        self.noOfDaysStockHasBeenLoosingValue.append(1)
                
                    currentPositions= positions.getPositions()        
                    for pos in currentPositions:
                        try:
                            index2= self.listOfLoosingStocks.index(pos['symbol']) #if it isn't in this list then we don't have to sell it
                            if (self.noOfDaysStockHasBeenLoosingValue[index2] > 2):
                                # we have this stock and it lost value twice
                                # Ergo- we sell
                                #sell
                                #if ((pos['purchase_price'] + (pos['shares']*self.ComPerShare))< temp): #rig it to make money
                                  print str(pos['symbol'])+" finally lost value for "+ str(self.noOfDaysStockHasBeenLoosingValue[index2])+" days. Selling it"
                                  order= stockInfo.OutputOrder()
                                  order.symbol= pos['symbol']
                                  order.volume= pos['shares']
                                  order.task= 'sell'
                                  order.orderType = 'moc'
                                  order.closeType = 'fifo'
                                  order.duration = self.DAY

                                  newOrder = order.getOutput()
                                  if newOrder != None:
                                    output.append(newOrder)
                                  else:
                                    print "ERROR! ERROR! ERROR!"
                        except ValueError:
                            pass #index not found 
                    #for pos in currentPositions
                             
                else:
                    #this stock did not loose value
                    
                    #Check if had been loosing value
                    #print str(self.listOfStocks[ctr])+ " gained value"
                    
                    try:
                      index1= self.listOfLoosingStocks.index(self.listOfStocks[ctr])
                      if (self.noOfDaysStockHasBeenLoosingValue[index1]>3):
                          
                            #print "This stock has been loosing value for atleast 3 days"
                            
                            order= stockInfo.OutputOrder()
                            order.symbol= self.listOfStocks[ctr]
                            order.volume= min(10* self.noOfDaysStockHasBeenLoosingValue[index1], 100)
                            order.task= 'buy'
                            order.orderType = 'moc'
                            order.closeType = 'fifo'
                            order.duration = self.DAY
                            newOrder = order.getOutput()
                            if newOrder != None:
                                 output.append(newOrder)
                            else:
                                 print "ERROR! ERROR! ERROR!"
            
                          #The stock was loosing value for <=3 days  but now gained value- so off with the head
                      self.listOfLoosingStocks.pop(index1)
                      self.noOfDaysStockHasBeenLoosingValue.pop(index1)                                  

                    except ValueError:
                        pass
                    
                    
#                    try:
#                        index1= self.listOfLoosingStocks.index(self.listOfStocks[ctr])
#                        
#                        print str(self.listOfStocks[ctr])+" lost value for "+ str(self.noOfDaysStockHasBeenLoosingValue[index]+ "..and then gained..")
#                        #Stock found
#                        #if it had lost value for more than 2 days then buy!
#                        if (self.noOfDaysStockHasBeenLoosingValue[index1]>3):
#                            #buy
#                            order= stockInfo.OutputOrder()
#                            order.symbol= self.listOfStocks[ctr]
#                            order.volume= max(10* self.noOfDaysStockHasBeenLoosingValue[index1], 100)
#                            order.task= 'buy'
#                            order.orderType = 'moc'
#                            order.closeType = 'fifo'
#                            order.duration = self.DAY
#                            newOrder = order.getOutput()
#                            if newOrder != None:
#                                 output.append(newOrder)
#                            else:
#                                 print "ERROR! ERROR! ERROR!"
#                        else:
#                            #it was loosing value- but for less than 2 days. So we just remove this entry...
#                            self.listOfLoosingStocks.pop(index1)
#                            self.noOfDaysStockHasBeenLoosingValue.pop(index1)
#                    except:
#                        #Not found- this stock had not lost value
#                        print "could not find index! Possibly a bug"
                ctr+=1
                #while loop ends..hopefully!
        
            
        
        
        
        return output
        #strategyTwo ends
    
    
    
    def execute (self, portfolio,positions,timestamp,stockInfo, dataAccess):
     '''
     @param portfolio: The portfolio object that has symbol and value of currently held stocks.
     @param positions: Detailed info about current stock holdings.
     @param timestamp: Current simulator time stamp
     @param stockInfo: Not used anymore for dataAccess.
     @param dataAccess: a dataAccess object that will henceforth be used to access all data
     '''
     
     output=[]
     #output =  self.strategyOne(portfolio, positions, timestamp, stockInfo, dataAccess)
     output =  self.strategyTwo(portfolio, positions, timestamp, stockInfo, dataAccess)
        #for pos in currentPositions: ends         
     #print "The outout is: " + str(output)
     
     return output           
                       
                 
             
         
         
    
    
    
    
#    
#     #Right now this is stratDemo firstStrategy
#     output = []
#    #This first for loop goes over all of the stock data to determine which stocks to buy
#     for stock in dataAccess.getListOfStocks(): #stockInfo.getStocks(startTime = timestamp - self.DAY,endTime = timestamp):
#        # if close is higher than open and close is closer to high than open is to low, buy
#        
##        print "In Optimizer"
##        print "     timestamp asked for is: " + str(timestamp - self.DAY, timestamp)
##        print "self.DAY: " + str(self.DAY)
#        adj_open= dataAccess.getStockDataList(stock, 'adj_open', timestamp - self.DAY, timestamp)
#        adj_close= dataAccess.getStockDataList(stock, 'adj_close', timestamp - self.DAY, timestamp)
#        adj_high= dataAccess.getStockDataList(stock, 'adj_high', timestamp - self.DAY, timestamp)
##        alphaValue= self.alphaData.getStockDataList (stock, 'alphaValue', timestamp - self.DAY, timestamp)
#        
#        if (adj_open.size > 0):
#            #if alphaValue <= 0.5 and adj_open < adj_close and (adj_high - adj_close) > (adj_open - adj_close): #highly possible bug here?
#         if adj_open < adj_close and (adj_high - adj_close) > (adj_open - adj_close): #highly possible bug here?
#            order = stockInfo.OutputOrder()
#            order.symbol = stock #stock['symbol']
#            order.volume = 20 
#            order.task = 'buy'
#            order.orderType = 'moc'
#            order.duration = self.DAY * 2
#            newOrder = order.getOutput()
#            if newOrder != None:
#                output.append(newOrder)
#            
#    #This for loop goes over all of our current stocks to determine which stocks to sell
#     for stock in portfolio.currStocks:
#        openPrice = list(dataAccess.getStockDataList(stock, 'adj_open',timestamp - self.DAY, timestamp))#dataAccess.getDataList(stock, 'adj_open',timestamp - self.DAY, timestamp)#stockInfo.getPrices(timestamp - self.DAY, timestamp,stock,'adj_open')
#        closePrice = list(dataAccess.getStockDataList(stock, 'adj_close',timestamp - self.DAY, timestamp))#dataAccess.getDataList(stock, 'adj_close',timestamp - self.DAY, timestamp) #stockInfo.getPrices(timestamp - self.DAY, timestamp,stock,'adj_close')
#        highPrice =  list(dataAccess.getStockDataList(stock, 'adj_high',timestamp - self.DAY, timestamp))#dataAccess.getDataList(stock, 'adj_high',timestamp - self.DAY, timestamp) #stockInfo.getPrices(timestamp - self.DAY, timestamp,stock,'adj_high')
#        lowPrice = list(dataAccess.getStockDataList(stock, 'adj_low',timestamp - self.DAY, timestamp))#dataAccess.getDataList(stock, 'adj_low',timestamp - self.DAY, timestamp) #stockInfo.getPrices(timestamp - self.DAY, timestamp,stock,'adj_low')
#        if(len(openPrice) != 0 and len(closePrice) != 0 and len(highPrice) != 0 and len(lowPrice) != 0):
#            # if closeprice is closer to low than openprice is to high, sell
#            if (closePrice[0]-lowPrice[0]) > (highPrice[0]-openPrice[0]):
#                order = stockInfo.OutputOrder()
#                order.symbol = stock
#                order.volume = portfolio.currStocks[stock]/2+1
#                order.task = 'sell'
#                order.orderType = 'moo'
#                order.closeType = 'fifo'
#                order.duration = self.DAY * 2
#                newOrder = order.getOutput()
#                if newOrder != None:
#                    output.append(newOrder)   
#    # return the sell orders and buy orders to the simulator to execute
#     return output     
         
     #return orders    
     #def execute ends