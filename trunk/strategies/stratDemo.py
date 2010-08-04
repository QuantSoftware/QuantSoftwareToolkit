import random
#THIS FILE IS NOW NOT NEEDED- SHREYAS JOSHI- 1- JUNE- 2010


# This file contains the demo strategies put together for testing purposes.
# note: all the parameters for strategy functions MUST BE THE SAME, otherwise will not work

# one day in unix time
DAY = 86400

def shortStrategy(portfolio,positions,timestamp,stockInfo):
    # written to test shortsells
    # shorts 20 shares a day
    output = []
    for stock in stockInfo.getStocks(startTime = timestamp-DAY,endTime = timestamp):
        order = stockInfo.OutputOrder()
        order.symbol = stock['symbol']
        order.volume = 20
        order.task = 'short'
        order.orderType = 'moc'
        order.duration = DAY * 2
        newOrder = order.getOutput()
        if newOrder != None:
            output.append(newOrder)
    # covers roughly half the owned volume
    for stock in portfolio.currStocks:
        order = stockInfo.OutputOrder()
        order.symbol = stock
        order.volume = -(portfolio.currStocks[stock]/2+1)
        order.task = 'cover'
        order.orderType = 'moo'
        order.closeType = 'fifo'
        order.duration = DAY * 2
        newOrder = order.getOutput()
        if newOrder != None:
            output.append(newOrder)
    return output

def dumbStrategy(portfolio,positions,timestamp,stockInfo):
    # rudimentary strategy to verify price data--built to run on fabricated stock data where volume/price were functions of the timestamp
    # buys an amount based on the timestamp, then sells half of what is owned
    output = []
    for stock in stockInfo.getStocks(startTime = timestamp-DAY,endTime = timestamp):
        order = stockInfo.OutputOrder()
        order.symbol = stock['symbol']
        order.volume = timestamp / DAY / 50
        order.task = 'buy'
        order.orderType = 'moc'
        order.duration = DAY * 2
        newOrder = order.getOutput()
        if newOrder != None:
            output.append(newOrder)
    for stock in portfolio.currStocks:
        order = stockInfo.OutputOrder()
        order.symbol = stock
        order.volume = portfolio.currStocks[stock]/2+1
        order.task = 'sell'
        order.orderType = 'moo'
        order.closeType = 'fifo'
        order.duration = DAY * 2
        newOrder = order.getOutput()
        if newOrder != None:
            output.append(newOrder)
    return output
        
def firstStrategy(portfolio,positions,timestamp,stockInfo):
    '''
    Decides what to do based on current and past stock data.
    The portfolio is a portfolio object that has your currently held stocks (currStocks) and your current cash (currCash)
    The timestamp is the current timestamp that the simulator is running on
    stockInfo is the StrategyData that the strategy can use to find out information about the stocks.  See below.
    '''
    output = []
    #This first for loop goes over all of the stock data to determine which stocks to buy
    for stock in stockInfo.getStocks(startTime = timestamp - DAY,endTime = timestamp):
        # if close is higher than open and close is closer to high than open is to low, buy
        if stock['adj_open'] < stock['adj_close'] and (stock['adj_high'] - stock['adj_close']) > (stock['adj_open'] - stock['adj_close']):
            order = stockInfo.OutputOrder()
            order.symbol = stock['symbol']
            order.volume = 20
            order.task = 'buy'
            order.orderType = 'moc'
            order.duration = DAY * 2
            newOrder = order.getOutput()
            if newOrder != None:
                output.append(newOrder)
            
    #This for loop goes over all of our current stocks to determine which stocks to sell
    for stock in portfolio.currStocks:
        openPrice = stockInfo.getPrices(timestamp - DAY, timestamp,stock,'adj_open')
        closePrice = stockInfo.getPrices(timestamp - DAY, timestamp,stock,'adj_close')
        highPrice = stockInfo.getPrices(timestamp - DAY, timestamp,stock,'adj_high')
        lowPrice = stockInfo.getPrices(timestamp - DAY, timestamp,stock,'adj_low')
        if(len(openPrice) != 0 and len(closePrice) != 0 and len(highPrice) != 0 and len(lowPrice) != 0):
            # if closeprice is closer to low than openprice is to high, sell
            if (closePrice[0]-lowPrice[0]) > (highPrice[0]-openPrice[0]):
                order = stockInfo.OutputOrder()
                order.symbol = stock
                order.volume = portfolio.currStocks[stock]/2+1
                order.task = 'sell'
                order.orderType = 'moo'
                order.closeType = 'fifo'
                order.duration = DAY * 2
                newOrder = order.getOutput()
                if newOrder != None:
                    output.append(newOrder)   
    # return the sell orders and buy orders to the simulator to execute
    return output

def dollarStrategy(portfolio,positions,timestamp,stockInfo):
    '''
    First semi-real strategy (specified by Tucker).
    Buys a stock if yesterday's close price was above $1 and todays is below $1, sells 20 days later no matter what.
    '''
    output = []
    for yesterday in stockInfo.getStocksArray(timestamp - DAY * 2, timestamp - DAY):
        if yesterday['close'] > 1:
            for today in stockInfo.getStocksArray(timestamp-DAY,timestamp,yesterday['symbol']):
                if today['close'] < 1:
                    order = stockInfo.OutputOrder()
                    order.symbol = today['symbol']
                    order.volume = 10000./today['close']
                    order.task = 'buy'
                    order.orderType = 'limit'
                    order.limitPrice = today['close']
                    order.duration = DAY
                    newOrder = order.getOutput()
                    if newOrder != None:
                        output.append(newOrder)  
    for position in positions.getPositions():
        if (position['timestamp'] <= (timestamp - DAY * 20)) and (position['shares'] > 0):
            order = stockInfo.OutputOrder()
            order.symbol = position['symbol']
            order.volume = position['shares']
            order.task = 'sell'
            order.orderType = 'moo'
            order.closeType = 'fifo'
            order.duration = DAY
            newOrder = order.getOutput()
            if newOrder != None:
                output.append(newOrder)  
    return output

def sortBySignal(listOfSymbols, timestamp,stockInfo):
    # helper function for analystStrategy - sorts a list of symbols according to the value of the signal field
    return sorted(listOfSymbols, lambda x: stockInfo.getStocks(timestamp-DAY,timestamp,x)[0]['signal'])

def analystStrategy(portfolio,positions,timestamp,stockInfo):
    # demonstrates how to use an additional field (such as analyst data) to base your transactions on
    # In this case, the additional field is a float from -1.0 to 1.0 which tells how good it is to sell/buy at that time
    
    # This strategy shorts the n most negative stocks, buys the n most positive, sells/covers everything after ten days
    n = 10
    nMostNegative = []
    nMostPositive = []
    output = []
    for stock in stockInfo.getStocks(timestamp - DAY, timestamp):
        if len(nMostNegative) < n:
            # if not n found yet, add to the list
            nMostNegative.append(stock['symbol'])
            nMostNegative = sortBySignal(nMostNegative,timestamp,stockInfo)
        elif stock['signal'] < getStocks(timestamp-DAY,timestamp,nMostNegative[len(nMostNegative)-1])[0]['signal']:
            # if better than something in the n found, add it, resort, and remove the worst
            nMostNegative.append(stock['symbol'])
            nMostNegative = sortBySignal(nMostNegative,timestamp,stockInfo)
            nMostNegative = nMostNegative[:-1]
        if len(nMostPositive) < n:
            # if not n found yet, add to the list
            nMostPositive.append(stock['symbol'])
            nMostPositive = sortBySignal(nMostPositive,timestamp,stockInfo)
        elif stock['signal'] > getStocks(timestamp-DAY,timestamp,nMostPositive[0])[0]['signal']:
            # if better than something in the n found, add it, resort, and remove the worst
            nMostPositive.append(stock['symbol'])
            nMostPositive = sortBySignal(nMostPositive,timestamp,stockInfo)
            nMostPositive = nMostPositive[1:]
    # add everything in the lists to the output
    for symbol in nMostNegative:
        order = stockInfo.OutputOrder()
        order.symbol = symbol
        order.volume = 50
        order.task = 'short'
        order.orderType = 'moo'
        order.duration = DAY
        newOrder = order.getOutput()
        if newOrder != None:
            output.append(newOrder)
    for symbol in nMostPositive:         
        order = stockInfo.OutputOrder()
        order.symbol = symbol
        order.volume = 50
        order.task = 'buy'
        order.orderType = 'moo'
        order.duration = DAY
        newOrder = order.getOutput()
        if newOrder != None:
            output.append(newOrder)
    # sell/cover ten days later
    for position in positions.getPositions():
        if (position['timestamp'] <= (timestamp - DAY * 10)) and (position['shares'] > 0):
            order = stockInfo.OutputOrder()
            order.symbol = position['symbol']
            order.volume = position['shares']
            order.task = 'sell'
            order.orderType = 'moo'
            order.closeType = 'fifo'
            order.duration = DAY
            newOrder = order.getOutput()
            if newOrder != None:
                output.append(newOrder)
        if (position['timestamp'] <= (timestamp - DAY * 10)) and (position['shares'] < 0):
            order = stockInfo.OutputOrder()
            order.symbol = position['symbol']
            order.volume = -position['shares']
            order.task = 'cover'
            order.orderType = 'moo'
            order.closeType = 'fifo'
            order.duration = DAY
            newOrder = order.getOutput()
            if newOrder != None:
                output.append(newOrder)  
    return output
    