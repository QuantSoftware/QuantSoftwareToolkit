'''
Created on Aug 2, 2010

@author: sjoshi42
'''


'''
Created on Jul 27, 2010

@author: Shreyas Joshi
@summary: This module reads in the alpha values generated based on the bollinger bands. It then outputs orders accordingly.
'''
import DataAccess
import numpy
class Optimizer(object):
    
    def __init__(self, listOfStocks):
        self.listOfStocks= listOfStocks
        self.DAY=86400
        dataItemsList=list()
        dataItemsList.append("alphaValue")
        self.alphaData= DataAccess.DataAccess(False, "AAPLonlybollingerBandsAlphaVals.h5", "/alphaData", "alphaData", True, listOfStocks, None, None, None, dataItemsList)
        print "Timestamps are: " 
        for ts in self.alphaData.timestamps:
            print ts
        #__init__ done
        
        
    def execute(self, portfolio,positions,timestamp,stockInfo, dataAccess):
        
        output=[]
        for stock in self.listOfStocks:
            alphaVal= self.alphaData.getStockDataItem(stock, "alphaValue", timestamp)
            
            
            print "alphaVal: "+ str (alphaVal)+ ", stock: "+ str(stock)+", ts: " + str(timestamp)
            
            if not (numpy.isnan(alphaVal)):
                #alphaVal is not Nan
                if (alphaVal > 0.9):
                    #buy
                    order= stockInfo.OutputOrder()
                    order.symbol= stock
                    order.volume= 100 #min(int(500*alphaVal), 100)
                    order.task= 'buy'
                    order.orderType = 'moc'
                    order.closeType = 'fifo'
                    order.duration = self.DAY
                    newOrder = order.getOutput()
                    if newOrder != None:
                         output.append(newOrder)
                    else:
                         print "ERROR! ERROR! ERROR!"                    
                else:
                    pass
                    #print "alhpaVal for "+str(stock)+" is: " + str(alphaVal)
            else:
                pass
                #print "alphaVal is nan"
            
            #for stock in self.listOfStocks done
                     
        for stock in portfolio.getListOfStocks():
            alphaVal= self.alphaData.getStockDataItem(stock, "alphaValue", timestamp)
            if not (numpy.isnan(alphaVal)):
                if (alphaVal < -0.6):
                    order= stockInfo.OutputOrder()
                    order.symbol= stock
                    order.volume=  max( (int (portfolio.getHeldQty(stock) /4)) , 1)
                    order.task= 'sell'
                    order.orderType = 'moc'
                    order.closeType = 'fifo'
                    order.duration = self.DAY
                    newOrder = order.getOutput()
                    if newOrder != None:
                        output.append(newOrder)
                    else:
                        print "ERROR! ERROR! ERROR!"
        return output                
                                            
                
        
    
