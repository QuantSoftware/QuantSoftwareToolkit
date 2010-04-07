|------------|
|Installation|
|------------|
In order to run the simulator, you will need:
* Python 2.6
* NumPy 1.3.0 installed on your Python 2.6
* PyTables 2.1.2 installed on your Python 2.6

|-------|
|Running|
|-------|
To run the system:
* Create a strategy (sample strategy in the strategies folder)
* Create a config file (or use the default, default.ini)
* Create and upload your data file (specified in the config file)
* Run the simulator passing the command line arguments: <Simulator> <config file> <strategy file> <main strategy function>
To run based on the example code: Simulator config.ini stratDemo myStrategy

|-------------------|
|Creating a Strategy|
|-------------------|
The strategy is composed of 3 parts: the method header with parameters, the strategy logic (including accessing stock data), and the return value (orders to buy and sell)

The Method Header
-----------------
The header of a strategy must have the folowing format:

def nameOfStrategy(portfolio,timestamp,stockInfo):

-You can name your strategy whatever you like (specified as a command line arguement), but the portfolio, timestamp and stockInfo will always be passed in in that order.
-The portfolio is a portfolio object that has your currently held stocks (currStocks) and your current cash (currCash)
-The timestamp is the current timestamp that the simulator is running on
-stockInfo is the StrategyData that the strategy can use to find out information about the stocks.  See below.

The Strategy Logic
------------------
This is the part where your actual strategy logic will go.  You will decide which stocks to buy and sell based on the strategy data in stockInfo.  The stockInfo is an instance of the StrategyData class which is populated with the data from the datafile you passed in through the config.

The StrategyData class (stockInfo) has 3 methods you can use to access stock information:

getStocks(startTime=None, endTime=None, ticker=None, isTable = False):
	Returns a list of dictionaries with each field accessable using its description
	Can be called independently or used as part of the getPrices function
	startTime: checks stocks >= startTime
	endTime: checks stocks <= endTime
	ticker: the ticker/symbol of the stock
	isTable: Using PyTables version (opposed to NumPy array version)

The getStocks method returns a dictionary, so the fields can be accessed using their field names:
    'timestamp', 'symbol', 'adj_high', 'adj_low', 'adj_open', 'adj_close', 'close', 'volume'
	so if you wanted the adj_close of all the stocks returned by getStocks the code would look like this:
	stocksList = stockInfo.getStocks(...)
	for stock in stocksList:
		print stock['adj_close'] #would print the adj_close of all applicable stocks
		
getPrice(timestamp, ticker, description, isTable=False):
	Returns a single price based on the parameters
	timestamp: the exact timestamp of the desired stock data
	ticker: the ticker/symbol of the stock
	description: the field from data that is desired IE. adj_high
	NOTE: If the data is incorrect or invalid, the function will return None  
	isTable: Using PyTables version (opposed to NumPy array version)  
	
The getPrice method returns a single value, if you already know exactly which stock you want:
	stockPrice = stockInfo.getPrice(...)
	print stockPrice #would print something like 43.25
	
getPrices(startTime=None, endTime=None, ticker=None, description=None, isTables=False):
	Returns a list of prices for the given description: [adj_high1, adj_high2, adj_high3...]
	or a tuple if no description is given: [ (adj_high1, adj_low1, adj_open1, adj_close1, close1), (adj_high2, adj_low2...), .... ]
	startTime: checks stocks >= startTime
	endTime: checks stocks <= endTime
	ticker: the ticker/symbol of the stock 
	description: the field from data that is desired IE. adj_high
	isTable: Using PyTables version (opposed to NumPy array version)  

Returns a list of prices if description is specified:
	stockPrices = stockInfo.getPrices(..., description = 'adj_close')
	print stockPrices # would give you a list of prices [43.42,23.11,...]
Returns a tuple of prices if description is blank:
	stockPrices = stockInfo.getPrices(...) #no description specified
	for stock in stockPrices:
		print stock #each stock would look like (43.11,22.34,35.19,24.16,24.16) with the values representing (adj_high, adj_low, adj_open, adj_close, close)
	
The Return Value
----------------
Your strategy must return two lists seperated by a comma (a tuple).  The first list should be the stocks to sell and the second should be the stocks to buy.

sellList: [(st0_volume,st0_symbol,st0_type,st0_lengthValid,st0_closeType,st0_limitPrice), (st1_volume,st1_symbol,st1_type,st1_lengthValid,st1_closeType),...]
where for each stock you want to sell you include the 5 (or 6) values in parenthesis (a tuple)
-volume: the number of stocks to sell	IE: 1000
-symbol: the ticker of the stock to sell	IE: 'KO'
-type: when to execute the trade
	'moo' - sell on market open
	'moc' - sell on market close
	'vwap' - average of high, low, open, close
	'limit' - sell for specified price if price between high and low of day
	'cover' - cover a short sell
-lengthValid: how long to continue attempting order, in seconds	IE: 172800
-closeType: sell longest held stocks first or shortest held stocks first
	'lifo' - last in, first out (shortest held sold)
	'fifo' - first in, first out (longest held sold)
-limitPrice: OPTIONAL, only include a limit price if type is 'limit'

buyList: [(st0_volume,st0_symbol,st0_type,st0_lengthValid,st0_closeType), (st1_volume,st1_symbol,st1_type,st1_lengthValid,st1_closeType),...]
where for each stock you want to sell you include the 4 (or 5) values in parenthesis (a tuple)
-volume: the number of stocks to sell	IE: 1000
-symbol: the ticker of the stock to sell	IE: 'KO'
-type: when to execute the trade
	'moo' - buy on market open
	'moc' - buy on market close
	'vwap' - average of high, low, open, close
	'limit' - buy for specified price if price between high and low of day
	'short' - short sell
-lengthValid: how long to continue attempting order, in seconds	IE: 172800
-closeType: can be specified for the strategy to access when it is time to sell, or can be none
	'none' - Not speicified, strategy will set at sell time
	'lifo' - last in, first out (shortest held sold), strategy must read at time of sale and set closeType to same value if desired
	'fifo' - first in, first out (longest held sold), strategy must read at time of sale and set closeType to same value if desired
	NOTE: This field is not read automatically, since there is no closeType at purchase time. It can be used if you know at purchase time which type you want the sell to execute, or can be 'none' if you do not plan on reading it before specifying the closeType at time of sale
-limitPrice: OPTIONAL, only include a limit price if type is 'limit'

The easiest way to do this is to create both lists before writing your strategy (sellData and buyData in the stratDemo) and append a new order to them each time you calculate one:
buyData.append( (5000,'KO','moc',172800,'none') ) #buy 5000 shares of KO at close, order is valid for 172800 seconds (2 days) 
sellData.append( (5000,'KO','vwap',172800,'fifo') ) #sell 5000 shares of KO at average price over the entire day, order is valid for 172800 seconds (2 days)

Take a look at the example strategy file stratDemo.py for an idea of how to format the strategy.

License
-------
BSD

Other products utilized
-----------------------
PyTables - http://www.pytables.org/
NumPy - http://numpy.scipy.org/

Other Notes
-----------
This is a working and almost fully functional prototype of the OQS backtester.  It is still under active development and more features and bug fixes will be released soon.  If you have any problems or encounter any errors, please