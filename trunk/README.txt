Installation
------------
In order to run the simulator, you will need:
* Python 2.6
* NumPy 1.3.0 installed on your Python 2.6
* PyTables 2.1.2 installed on your Python 2.6

Running
-------
To run the system:
* Create a strategy (sample strategy in the strategies folder)
* Create a config file (or use the default, default.ini)
* Run the simulator passing the command line arguments: <config file> <strategy file> <main strategy function>
To run based on the example code: Simulator config.ini stratDemo myStrategy

Note:  Currently the simulator is running off of randomly generated, artificial stock data.  
If you have stock data formatted using the StrategyDataModel, you can specify the file in the Simulator's init method.
A more formalized approach will be devised for later releases.

Creating a Strategy
-------------------
The header of a strategy must have the folowing format:
def nameOfStrategy(portfolio,timestamp,stockInfo):
-You can name your strategy whatever you like, but the portfolio, timestamp and stockInfo will always be passed in in that order.
-The portfolio is a portfolio object that has your currently held stocks (currStocks) and your current cash (currCash)
-The timestamp is the current timestamp that the simulator is running on
-stockInfo is the StrategyData that the strategy can use to find out information about the stocks.  See below.

Your strategy must return two lists seperated by a comma (a tuple).  The first list should be the stocks to sell and the second should be the stocks to buy.  The format of the lists should be:

sellList: [(st1_volume,st1_symbol,st1_type,st1_lengthValid,st1_closeType,st1_limitPrice), (st2_volume,st2_symbol,st2_type,st2_lengthValid,st2_closeType),...]
where for each stock you want to sell you include the 5 (or 6) values in parenthesis (a tuple)
volume: the number of stocks to sell	IE: 1000
symbol: the ticker of the stock to sell	IE: 'KO'
type: when to execute the trade
	'moo' - sell on market open
	'moc' - sell on market close
	'vwap' - average of high, low, open, close
	'limit' - sell for specified price if price between high and low of day
	'cover' - cover a short sell
lengthValid: how long to continue attempting order, in seconds	IE: 172800
closeType: sell longest held stocks first or shortest held stocks first
	'lifo' - last in, first out (shortest held sold)
	'fifo' - first in, first out (longest held sold)
limitPrice: OPTIONAL, only include a limit price if type is 'limit'

buyList: [(st1_volume,st1_symbol,st1_type,st1_lengthValid,st1_closeType), (st2_volume,st2_symbol,st2_type,st2_lengthValid,st2_closeType),...]
where for each stock you want to sell you include the 4 (or 5) values in parenthesis (a tuple)
volume: the number of stocks to sell	IE: 1000
symbol: the ticker of the stock to sell	IE: 'KO'
type: when to execute the trade
	'moo' - buy on market open
	'moc' - buy on market close
	'vwap' - average of high, low, open, close
	'limit' - buy for specified price if price between high and low of day
	'short' - short sell
lengthValid: how long to continue attempting order, in seconds	IE: 172800
closeType: can be specified for the strategy to access when it is time to sell, or can be none
	'none' - Not speicified, strategy will set at sell time
	'lifo' - last in, first out (shortest held sold), strategy must read at time of sale and set closeType to same value if desired
	'fifo' - first in, first out (longest held sold), strategy must read at time of sale and set closeType to same value if desired
	NOTE: This field is not read automatically, since there is no closeType at purchase time. It can be used if you know at purchase time which type you want the sell to execute, or can be 'none' if you do not plan on reading it before specifying the closeType at time of sale
	
limitPrice: OPTIONAL, only include a limit price if type is 'limit'


StrategyData Class (stockInfo)
------------------------------
The StrategyData class (accessed as stockInfo above) has 3 methods:

getStocks(self, startTime=None, endTime=None, ticker=None, isTable = False):
	Returns a list of dictionaries for accessing stock information.
	Can be called independently or used as part of the getPrices function
	startTime: checks stocks >= startTime
	endTime: checks stocks <= endTime
	ticker: the ticker/symbol of the stock 
	isTable: Using PyTables version (opposed to NumPy array version)
	
getPrice(self, timestamp, ticker, description, isTable=False):
	timestamp: the exact timestamp of the desired stock data
	ticker: the ticker/symbol of the stock
	description: the field from data that is desired IE. adj_high
	isTable: Using PyTables version (opposed to NumPy array version)
	NOTE: If the data is incorrect or invalid, the function will return None  
	
getPrices(self, startTime=None, endTime=None, ticker=None, description=None, isTables=False):
	Returns a list of prices for the given description or a list of dictionaries of information (accessed using field names) if no description is given
	description: the field from data that is desired IE. adj_high
	startTime: checks stocks >= startTime
	endTime: checks stocks <= endTime
	ticker: the ticker/symbol of the stock  
	isTable: Using PyTables version (opposed to NumPy array version)	

Take a look at the example strategy file stratDemo.py for an idea of how to format the strategy.

Accessing Stock Info
--------------------
getStocks and getPrices return information as a list of stocks.  Each stock will have the following fields:
    'timestamp', 'symbol', 'adj_high', 'adj_low', 'adj_open', 'adj_close', 'close', 'volume'
To access the information you need to get a single stock and access a field by using dictionary accessing:
	stock['fieldname']


License
-------
BSD

Other products utilized
-----------------------
PyTables - http://www.pytables.org/
NumPy - http://numpy.scipy.org/

Information
-----------
This is a working and almost fully functional prototype of the OQS backtester.