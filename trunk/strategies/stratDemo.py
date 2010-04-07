import random


# Rudimentary proof-of-concept strategy; takes in a 'portfolio' that is a two-element list; first is a float
# (cash on hand) and second is a list of stocks, organized as follows:
# [$$$$$, [ [symbol, shares], [symbol, shares], [symbol, shares],...] ]

# Note: actual portfolio will be OO


# This demo strategy prints out the current amount of money in the portfolio and adds a random amount 
# (up to 1000) to it, then prints the stocks and volume owned
def myStrategy(portfolio,positions,timestamp,stockInfo):
    '''
    COMMENTS HERE
    '''
    output = []
    for yesterday in stockInfo.getStocksArray(timestamp - 86400 * 2, timestamp - 86400):
        if yesterday['close'] > 1:
            for today in stockInfo.getStocksArray(timestamp-86400,timestamp,yesterday['symbol']):
                if today['close'] < 1:
                    order = stockInfo.OutputOrder()
                    order.symbol = today['symbol']
                    order.volume = 10000./today['close']
                    order.task = 'buy'
                    order.orderType = 'limit'
                    order.limitPrice = today['close']
                    order.duration = 86400
                    output.append(order.getOuput())
    for position in positions.getPositions():
        if position['timestamp'] <= (timestamp - 86400 * 20):
            order = stockInfo.OutputOrder()
            order.symbol = position['symbol']
            order.volume = position['shares']
            order.task = 'sell'
            order.orderType = 'moo'
            order.closeType = 'fifo'
            order.duration = 86400
            output.append(order.getOuput())
    return output
        