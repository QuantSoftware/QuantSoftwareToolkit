import random


# Rudimentary proof-of-concept strategy; takes in a 'portfolio' that is a two-element list; first is a float
# (cash on hand) and second is a list of stocks, organized as follows:
# [$$$$$, [ [symbol, shares], [symbol, shares], [symbol, shares],...] ]

# Note: actual portfolio will be OO


# This demo strategy prints out the current amount of money in the portfolio and adds a random amount 
# (up to 1000) to it, then prints the stocks and volume owned
def myStrategy(portfolio,timestamp,stockInfo):
    '''
    Decides what to do based on current and past stock data.
    Returns a tuple of lists (sellData, buyData) - the infomation needed to execute buy and sell transactions
    The portfolio is a portfolio object that has your currently held stocks (currStocks) and your current cash (currCash)
    The timestamp is the current timestamp that the simulator is running on
    stockInfo is the StrategyData that the strategy can use to find out information about the stocks.  See below.
    '''
    sellData = []
    buyData = []
    #This first for loop goes over all of the stock data to determine which stocks to buy
    for stock in stockInfo.getStocks(startTime = timestamp - 86400,endTime = timestamp):
        if stock['adj_open'] < stock['adj_close'] and (stock['adj_high'] - stock['adj_close']) > (stock['adj_open'] - stock['adj_close']):
            # Format for stock buys (volume,symbol,type,lengthValid,closeType,OPTIONAL: limitPrice)
            buyData.append((stock['volume']+2,stock['symbol'],'moc',172800,'none'))
    #This for loop goes over all of our current stocks to determine which stocks to sell
    for stock in portfolio.currStocks:
        if (stockInfo.getPrices(timestamp - 86400, timestamp,stock,'adj_close')[0]-stockInfo.getPrices(timestamp - 86400, timestamp,stock,'adj_low')[0]) > (stockInfo.getPrices(timestamp - 86400, timestamp,stock,'adj_high')[0]-stockInfo.getPrices(timestamp - 86400, timestamp,stock,'adj_open')[0]):
            # Format for stock sells (volume,symbol,type,lengthValid,closeType,OPTIONAL: limitPrice)
            sellData.append((portfolio.currStocks[stock]/2,stock,'moo',172800,'fifo'))
    # return the sell orders and buy orders to the simulator to execute
    return (sellData,buyData)
    