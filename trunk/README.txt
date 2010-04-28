|-----------------|
|Table of Contents|
|-----------------|
1. Installation
2. Running
3. Creating a Datafile
4. Configuration File
5. Creating a Strategy 
6. License
7. Built Using
8. Other Notes

|------------|
|Installation|
|------------|
In order to run the simulator, you will need:
* Python 2.6
* NumPy 1.3.0 installed on your Python 2.6
* PyTables 2.1.2 installed on your Python 2.6

1) Download and install Python 2.6 from http://www.python.org
2) Download and install NumPy 1.3.0 or newer from http://numpy.scipy.org/
3) Download and install PyTables 2.1.2 or newer from http://www.pytables.org/
	Note: Ensure that NumPy and PyTables are installed to Python26 and not to another version of python
4) Download all of the files from the SVN ( http://www.quantsoftware.org/openquantsoftware/ ) ensuring that the file structure is maintained


|-------|
|Running|
|-------|
To run the system:
* Create a strategy (sample strategies in the strategies folder)
* Create a config file and put it in the configfiles folder (or use config.ini)
* Create and upload your data file to the datafiles folder (path specified in the config file)
* Run the simulator passing the command line arguments: <Simulator> <config file> <strategy file> <main strategy function>
To run based on the example code: simulator.py config.ini stratDemo firstStrategy

|-------------------|
|Creating a Datafile|
|-------------------|
If you are using unix for a simulator data file created in Windows (dos) or visa versa,
and you may need to use a dos to unix (or unix to dos) converter on YourArrayFile.pkl 
to get the file into a format that your system can read
Note: The defaultArrayFile.pkl was created using Windows

Raw Data Format
---------------
To create a datafile for the simulator you will need the following raw data:
1) A folder containing a .txt file for each stock (IE: AAPL.TXT GOOG.TXT ...)
	Note: File would be named TICK.TXT for a stock with ticker 'tick'
2) A text file containing all of the tickers you would like to use in your data file, one ticker per line
	IE: aapl
		goog
		tick
	Note: The ticker from step 2 should match the file name of the stock from step 1

The format of the TICK.TXT file is as follows:
	The first line should list the fields in quotes, seperated by commas
	Each subsequent line should be the data, without quotes, seperated by commas
	
	IE:
	"Name","Date","Open","High","Low","Close","Volume","Close"
	TICK,19821101,3.25,3.38,3.14,3.34,3739176,26.75
	TICK,19821102,3.53,3.69,3.38,3.58,11126160,28.63
	...
	Note: The format for the date is YYYYMMDD

Using csvconveter
-----------------
To create datafiles from your raw data, use the csvconverter that comes with the simulator.

1) Navigate to the csvconverter folder in the simulator
2) Open the csvapi.py file
3) In the main method modify the variables to run on the data you have chosen
	A) stockDataFolder is the folder containing your TICK.TXT files from step 1 in the data formatting section above
	B) stocksToUseFile is the file containing one ticker per line from step 2 in the data formatting section above
	C) startDate is the first day you would like the data for (in YYYYMMDD format)
	D) endDate is the last day you would like data for (in YYYYMMDD format)
	E) isArray specifies if you would like an array file or table file (array is superior if your computer can hold all stock data in memory)
	F) outputFilename specifies the name of the file containing the converted data (default extensions are .pkl for array and .h5 for table)
4) Run the csvapi.py file
5) Your resulting file should be outputted to the same folder the csvapi.py file ran in
6) Move the newly created file to the datafiles folder


|------------------|
|Configuration File|
|------------------|
The configuration file found in the configfiles folder is used to set the parameters of your simulation.  

* You can name your config file anything you would like (other than default.ini) as the file path specified as a command line arguement. 
* Any field that is left out of your config file will be populated using the parameters from default.ini.
* Any line beginning with a # will be ignored by the configuration parser.
* All parameter names are not case sensative

The valid parameters for the config file are:
- ComPerShare: The amount of commission charged per share
- MinCom: The minimum commission charged for a transaction
- StartTime: The time in seconds since 1970 (unix time) that the simulator should begin execution from
- EndTime: The time in seconds since 1970 (unix time) that the simulator should run to
- TimeStep: The amount of time in seconds that should elapse between each simulator execution
- MaxMarketEffect: The maximum percentage your purchase could have on the market
	The MaxMarketEffect is based on the number of shares you purchase in relation to the volume traded during the time interval.  
	If the volume for the day for a stock was 1000 shares, and you purchased 1000 you would incur the full MaxMarketEffect value added to the price
	In the above example if MME = .01 (1%) and you purchase 100% of the volume, you would incur a 1% increase in price, similarly if you purchased 50% you would incur a .5% price increase
	This effect also applies for selling
- DecayCycles: Not currently implemented, will be the number of simulator cycles before your impact on the market is removed
- DataType: The underlying datastructure you would like to use to run the simulator
	array: The preferred run time, will run significantly faster than tables but stores stock information in memory, so some computers with low RAM may not be able to run in this mode
	table: Run using pytables, which are significatly slower than array.  Use only if the array version will not run on your system.
- ArrayFile: The path to the datafile containing your stock information, stored in array format (the .pkl file generated by the csvconverter)
- PytablesFile: The path to the datafile containing your pytables file, currently the csvconverter is unable to generate pytables files, but the feature will be added shortly
- NOISY: Include printouts of simulator status as the simulator runs (includes stocks bought/sold, reason orders don't succeed, portfolio value and currently held stocks)
- TIMER: Include printouts of how long each component of the simulator is taking to run
- MTM: Include printouts for the timestamp and portfolio value in the following format | TS Value |
- cash: The amount of cash to start with in your portfolio when the simulator begins

|-------------------|
|Creating a Strategy|
|-------------------|
The strategy is composed of 3 parts: the method header with parameters, the strategy logic (including accessing stock data), and the return value (orders to buy and sell)

The Method Header
-----------------
The header of a strategy must have the folowing format:

def nameOfStrategy(portfolio,positions,timestamp,stockInfo):

- You can name your strategy whatever you like (when running you will specify which as a command line arguement), but the portfolio, positions, timestamp and stockInfo parameters will always be passed in in that order.

- The portfolio is a portfolio object that has symbol and volume of your currently held stocks (currStocks) and your current cash (currCash)
- The positions are detailed information about your current stock holdings, including when you bought them, how much you paid per stock, etc.
- The timestamp is the current timestamp that the simulator is running on
- stockInfo is the StrategyData that the strategy can use to find out information about the stocks.  See below.

The Strategy Logic
------------------
This is the part where your actual strategy logic will go.  You will decide which stocks to buy and sell based on the strategy data in stockInfo.  The stockInfo is an instance of the StrategyData class which is populated with the data from the datafile you passed in through the config.

The StrategyData class (stockInfo) has 3 methods you can use to access stock information:

getStocks(startTime=None, endTime=None, ticker=None):
        Returns a list of dictionaries that contain all of the valid stock data as keys
        or an empty list if no results are found
        startTime: checks stocks >= startTime
        endTime: checks stocks < endTime (note exclusive)
        ticker: the ticker/symbol of the stock or a list of tickers

	The getStocks method returns a dictionary, so the fields can be accessed using their field names:
		'timestamp', 'symbol', 'adj_high', 'adj_low', 'adj_open', 'adj_close', 'close', 'volume', 'date'
		so if you wanted the adj_close of all the stocks returned by getStocks the code would look like this:
		stocksList = stockInfo.getStocks(...)
		for stock in stocksList:
			print stock['adj_close'] #would print the adj_close of all applicable stocks
		
getPrice(timestamp, ticker, description):
        Returns a single price based on the parameters
        timestamp: the exact timestamp of the desired stock data
        ticker: the ticker/symbol of the stock
        description: the field from data that is desired IE. adj_high
		NOTE: If the data is incorrect or invalid, the function will return None  
	
	The getPrice method returns a single value, if you already know exactly which stock you want:
		stockPrice = stockInfo.getPrice(...)
		print stockPrice #would print something like 43.25
	
getPrices(startTime=None, endTime=None, ticker=None, description=None):
	Returns a list of prices for the given description: [adj_high1, adj_high2, adj_high3...]
	or a tuple if no description is given: [ (adj_high1, adj_low1, adj_open1, adj_close1, close1), (adj_high2, adj_low2...), .... ]
	startTime: checks stocks >= startTime
	endTime: checks stocks < endTime (note exclusive)
	ticker: the ticker/symbol of the stock or a list of tickers
	description: the field from data that is desired IE. adj_high

	Returns a list of prices if description is specified:
		stockPrices = stockInfo.getPrices(..., description = 'adj_close')
		print stockPrices # would give you a list of prices [43.42,23.11,...]
	Returns a tuple of prices if description is blank:
		stockPrices = stockInfo.getPrices(...) #no description specified
		for stock in stockPrices:
			print stock #each stock would look like (43.11,22.34,35.19,24.16,24.16) with the values representing (adj_high, adj_low, adj_open, adj_close, close)
	
The Return Value
----------------
Your strategy must return a list of all of the orders you would like the simulator to place.

The StrategyData class (stockInfo) has a subclass to make adding orders easier.  It will make sure that you have correctly entered all of the information and has a method for giving you the output in the correct format to append to the output list.  You can set the fields in any order
but you must enter all of them before calling the getOutput() method.
	
- task: what type of trade you are doing
	'buy' - buy shares the next day at price specified by type, can't be done if you are currently shorting the stock
	'sell' - sell shares the next day at price specified by type, can't be done if you are currently shorting the stock
	'short' - short sell stocks, can't be done if you currently hold 'buy' shares of same stock
	'cover' - cover a short sale, can't be done if you currently hold 'buy' shares of same stock
- symbol: the ticker of the stock to trade	IE: 'KO'
- volume: the number of shares to trade	IE: 1000
- type: when to execute the trade
	'moo' - trade on market open
	'moc' - trade on market close
	'vwap' - trade at average of high, low, open, close
	'limit' - trade for specified price if price between high and low of day
- duration: how long to continue attempting order, in seconds	IE: 172800
- closeType: only required for sell and cover, sell longest held stocks first or shortest held stocks first
	'lifo' - last in, first out (shortest held sold)
	'fifo' - first in, first out (longest held sold)
- limitPrice: only required if type is 'limit', the price you wish to pay
	Note: A limit order will fail to execute if the limit price is outside of the low to high range of the stock for the day

Once you have filled in all of the fields, you can use the getOutput method to get the order to append to your list.

Note: If you leave out a field and try to use the getOutput method, it will print out what field you are missing and return None

Example:
	order = stockInfo.OutputOrder()
	order.task = 'buy'
	order.symbol = 'AAPL'
	order.volume = 20
	order.orderType = 'moc'
	order.duration = 172800
	#order.closeType = 'lifo' #Not needed for buy
	#order.limitPrice = 10 #Not needed, we are doing standard buy
	newOrder = order.getOutput()
	if newOrder != None:
		output.append(newOrder)    


|-------|
|License|
|-------|
BSD

See LICENSE.TXT

|-----------|
|Built Using|
|-----------|
PyTables - http://www.pytables.org/
NumPy - http://numpy.scipy.org/

|-----------|
|Other Notes|
|-----------|
