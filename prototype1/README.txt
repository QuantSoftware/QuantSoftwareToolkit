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