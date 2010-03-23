import random


# Rudimentary proof-of-concept strategy; takes in a 'portfolio' that is a two-element list; first is a float
# (cash on hand) and second is a list of stocks, organized as follows:
# [$$$$$, [ [symbol, shares], [symbol, shares], [symbol, shares],...] ]

# Note: actual portfolio will be OO


# This demo strategy prints out the current amount of money in the portfolio and adds a random amount 
# (up to 1000) to it, then prints the stocks and volume owned
def myStrategy(portfolio,timestamp,stockInfo):
    sellData = []
    buyData = []
    for stock in stockInfo.getStocks(startTime = timestamp - 86400,endTime = timestamp):
        if stock['data/adj_open'] < stock['data/adj_close'] and (stock['data/adj_high'] - stock['data/adj_close']) > (stock['data/adj_open'] - stock['data/adj_close']):
            buyData.append((stock['data/volume']/2,stock['symbol'],'moc',172800,'none'))
    for stock in portfolio.currStocks:
        if (stockInfo.getPrices(timestamp - 86400, timestamp,stock,'adj_close')[0]-stockInfo.getPrices(timestamp - 86400, timestamp,stock,'adj_low')[0]) > (stockInfo.getPrices(timestamp - 86400, timestamp,stock,'adj_high')[0]-stockInfo.getPrices(timestamp - 86400, timestamp,stock,'adj_open')[0]):
            sellData.append((portfolio.currStocks[stock]/2,stock,'moo',172800,'fifo'))
    return (sellData,buyData)
    