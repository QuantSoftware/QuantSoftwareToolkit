'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on May 14, 2012

@author: Jeffrey Portman
@contact: chromox@gmail.com
@summary: <summary>
'''

import os
import time
import pandas
import pickle
import sqlite3
import datetime
import MySQLdb
from operator import itemgetter
from dateutil.relativedelta import relativedelta

B_NEW = True


class DriverInterface(object):
    '''
    DriverInterface is the data access interface that all driver classes must adhear to.
    '''
    def get_data(self, ts_list, symbol_list, data_item, verbose=False,
                    include_delisted=False):
        raise NotImplementedError("Selected Driver has not implmented get_data.")

    def get_all_symbols(self):
        raise NotImplementedError("Selected Driver has not implmented get_all_symbols.")

    def get_list(self, list_name):
        raise NotImplementedError("Selected Driver has not implmented get_list.")

    def get_all_lists(self):
        raise NotImplementedError("Selected Driver has not implmented get_all_lists.")


class _SQLite(DriverInterface):
    """
    Driver class for SQLite
    """

    def __init__(self):

        try:
            self.sqldbfile = os.environ['QSDB']
        except KeyError:
            raise RuntimeError("Database environment variable not set.")

        self._connect()

    def _connect(self):
        self.connection = sqlite3.connect(self.sqldbfile,
                            detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.connection.cursor()

    def get_data(self, ts_list, symbol_list, data_item,
                    verbose=False, include_delisted=False):
        if _ScratchCache.try_cache:
            return _ScratchCache.try_cache(ts_list, symbol_list, data_item,
                        verbose, include_delisted, self.get_data_hard_read, "SQLite")
        else:
            return self.get_data_hard_read(ts_list, symbol_list, data_item,
                        verbose, include_delisted)

    def get_data_hard_read(self, ts_list, symbol_list, data_item, verbose=False, include_delisted=False):
        """
        Read data into a DataFrame from SQLite
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.  May be a list, in which case a list of DataFrame is returned.
        @param include_delisted: If true, delisted securities will be included.
        @note: If a symbol is not found all the values in the column for that stock will be NaN. Execution then
        continues as usual. No errors are raised at the moment.
        """
        columns = []
        results = []

        # Check input data
        assert isinstance(ts_list, list)
        assert isinstance(symbol_list, list)
        assert isinstance(data_item, list)

        # Combine Symbols List for Query
        symbol_query_list = ",".join(map(lambda x: "'" + x + "'", symbol_list))

        # Combine Data Fields for Query
        data_item = map(lambda x: "B." + x, data_item)
        query_select_items = ",".join(data_item)
        
        if B_NEW == False:
            # Build Query - Inherently Unsafe!
            self.cursor.execute("""
                    SELECT A.symbol,B.timestamp,""" + query_select_items + """
                    FROM tblEquity A JOIN tblPriceVolumeHistory B ON A.ID = B.tblEquity_ID
                    WHERE B.timestamp >= (?) AND B.timestamp <= (?) AND A.symbol IN (%s)
                    ORDER BY A.symbol ASC
                """ % symbol_query_list, (ts_list[0], ts_list[-1],))
        else:
            self.cursor.execute("""
            select A.code as symbol, B.date,"""+ query_select_items + 
            """ from price B, asset A where A.assetid = B.assetid and 
            B.date >= (?) and B.date <= (?) 
            and A.code in (%s);""" % symbol_query_list, (ts_list[0], ts_list[-1],))

        # Retrieve Results
        results = self.cursor.fetchall()
        if len(results) == 0:
            for current_column in range(len(data_item)):
                columns.append( pandas.DataFrame(columns=symbol_list) )
                return columns


        # Remove all rows that were not asked for
        for i, row in enumerate(results):
            if row[1] not in ts_list:
                del results[i]

        # Create Pandas DataFrame in Expected Format
        current_dict = {}
        symbol_ranges = self._find_ranges_of_symbols(results)
        for current_column in range(len(data_item)):
            for symbol, ranges in symbol_ranges.items():
                current_symbol_data = results[ranges[0]:ranges[1] + 1]
                current_dict[symbol] = pandas.Series(
                                        map(itemgetter(current_column + 2), current_symbol_data),
                                        index=map(itemgetter(1), current_symbol_data))
            # Make DataFrame
            columns.append(pandas.DataFrame(current_dict, columns=symbol_list))
            current_dict = {}

        return columns

    def get_list(self, list_name):
        self.cursor.execute("""SELECT A.Symbol
                    FROM tblEquity A JOIN tblListDetail C ON A.ID = C.tblEquity_ID
                    JOIN tblListHeader B ON B.ID = C.tblListHeader_ID
                    WHERE B.ListName = ?
        """, (list_name,))
        return self.cursor.fetchall()

    def get_all_symbols(self):
        self.cursor.execute("SELECT DISTINCT symbol FROM tblEquity")
        return self.cursor.fetchall()

    def get_all_lists(self):
        self.cursor.execute("SELECT ListName FROM tblListHeader")
        return self.cursor.fetchall()

    def _find_ranges_of_symbols(self, results):
        ''' Finds range of current symbols in results list '''
        symbol_dict = {}
        current_symbol = results[0][0]
        start = 0

        for i, row in enumerate(results):
            if row[0] != current_symbol:
                symbol_dict[current_symbol] = (start, i - 1)
                start = i
                current_symbol = row[0]
        
        #handle last symbol
        symbol_dict[current_symbol] = (start, i)

        return symbol_dict


class _MySQL(DriverInterface):
    """
    Driver class for SQLite
    """

    def __init__(self):
        self._connect()
    
    def __del__(self):
        self.db.close()
            
    def _connect(self):
        if B_NEW:
            self.db = MySQLdb.connect("localhost", "finance", "cduwh2PXnL", "premiumdata")
        else:
            self.db = MySQLdb.connect("localhost", "finance", "cduwh2PXnL", "HistoricalEquityData")

        self.cursor = self.db.cursor()

    def get_data(self, ts_list, symbol_list, data_item,
                    verbose=False, include_delisted=False):
        if _ScratchCache.try_cache:
            return _ScratchCache.try_cache(ts_list, symbol_list, data_item,
                        verbose, include_delisted, self.get_data_hard_read, "MySQL")
        else:
            return self.get_data_hard_read(ts_list, symbol_list, data_item,
                        verbose, include_delisted)

    def get_data_hard_read(self, ts_list, symbol_list, data_item, verbose=False, include_delisted=False):
        """
        Read data into a DataFrame from SQLite
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.  May be a list, in which case a list of DataFrame is returned.
        @param include_delisted: If true, delisted securities will be included.
        @note: If a symbol is not found all the values in the column for that stock will be NaN. Execution then
        continues as usual. No errors are raised at the moment.
        """
        columns = []
        results = []

        # Check input data
        assert isinstance(ts_list, list)
        assert isinstance(symbol_list, list)
        assert isinstance(data_item, list)

        if B_NEW:
            
            # Map to new database schema to preserve legacy code
            ds_map = {'open':'tropen',
                      'high':'trhigh',
                      'low':'trlow',
                      'close':'trclose',
                      'actual_close':'close',
                      'volume':'volume',
                      'adjusted_close':'adjclose'}

            data_item = map(lambda(x): ds_map[x], data_item)
        
        
        print data_item


        # Combine Symbols List for Query
        symbol_query_list = ",".join(map(lambda x: "'" + x + "'", symbol_list))

        # Combine Data Fields for Query
        data_item = map(lambda x: "B." + x, data_item)
        query_select_items = ",".join(data_item)

        if B_NEW == False:
            # Build Query - Inherently Unsafe!
            self.cursor.execute("""
                SELECT A.symbol,B.timestamp,""" + query_select_items + """
                FROM tblEquity A JOIN tblPriceVolumeHistory B ON 
                A.ID = B.tblEquity_ID
                WHERE B.timestamp >= %s AND B.timestamp <= %s AND A.symbol 
                IN (""" + symbol_query_list + """) ORDER BY A.symbol ASC
                """, (ts_list[0], ts_list[-1],))
        else:

            self.cursor.execute("""
            select A.code as symbol, B.date,""" + query_select_items + """
            from price B, asset A where A.assetid = B.assetid and 
            B.date >= %s and B.date <= %s and A.code in (
            """ + symbol_query_list + """)""", (ts_list[0], ts_list[-1],))


        # Retrieve Results
        results = self.cursor.fetchall()

        # Remove all rows that were not asked for
        results = list(results)

        if len(results) == 0:
            for current_column in range(len(data_item)):
                columns.append( pandas.DataFrame(columns=symbol_list) )
                return columns

        for i, row in enumerate(results):
            if B_NEW:
                if row[1] + relativedelta(hours=16) not in ts_list:
                    del results[i]
            else:
                if row[1] not in ts_list:
                    del results[i]

        # Create Pandas DataFrame in Expected Format
        current_dict = {}
        symbol_ranges = self._find_ranges_of_symbols(results)
        for current_column in range(len(data_item)):
            for symbol, ranges in symbol_ranges.items():
                current_symbol_data = results[ranges[0]:ranges[1] + 1]
                
                if B_NEW:
                    current_dict[symbol] = pandas.Series(
                      map(itemgetter(current_column + 2), current_symbol_data),
                    index=map(lambda x: itemgetter(1)(x) + relativedelta(hours=16), 
                                                      current_symbol_data))
                else:
                    current_dict[symbol] = pandas.Series(
                      map(itemgetter(current_column + 2), current_symbol_data),
                    index=map(itemgetter(1), current_symbol_data))
                    
            # Make DataFrame
            columns.append(pandas.DataFrame(current_dict, columns=symbol_list))
            current_dict = {}
                

        return columns

    def get_list(self, list_name):
        
        if B_NEW:
            if type(list_name) == type('str') or \
               type(list_name) == type(u'unicode'):
                self.cursor.execute("""select myself.code as symbol from 
                    indexconstituent consititue1_, asset belongsTo, asset myself
                    where belongsTo.assetid=consititue1_.indexassetid and 
                    myself.assetid = consititue1_.assetid
                    and belongsTo.issuerName = %s;""", (list_name))
            else:
                self.cursor.execute("""select myself.code as symbol from 
                    indexconstituent consititue1_, asset myself
                    where myself.assetid = consititue1_.assetid and 
                    consititue1_.indexassetid = %s;""", (str(int(list_name))))
        else:
            self.cursor.execute("""SELECT DISTINCT A.Symbol
                        FROM tblEquity A JOIN tblListDetail C ON A.ID = C.tblEquity_ID
                        JOIN tblListHeader B ON B.ID = C.tblListHeader_ID
                        WHERE B.list_name = %s
            """, (list_name,))
        return sorted([x[0] for x in self.cursor.fetchall()])

    def get_all_symbols(self):
        self.cursor.execute("SELECT DISTINCT symbol FROM tblEquity")
        return sorted([x[0] for x in self.cursor.fetchall()])

    def get_all_lists(self):
        
        if B_NEW:
            self.cursor.execute("""select asset0_.assetid as id, asset0_.issuername as name
                from asset asset0_ where exists 
                (select consititue1_.assetid from indexconstituent consititue1_ 
                where asset0_.assetid=consititue1_.indexassetid) 
                order by asset0_.issuername;""")
            return sorted([x[1] for x in self.cursor.fetchall()])
        else:
            self.cursor.execute("SELECT list_name FROM tblListHeader")
            return sorted([x[0] for x in self.cursor.fetchall()])

    def _find_ranges_of_symbols(self, results):
        ''' Finds range of current symbols in results list '''
        symbol_dict = {}
        current_symbol = results[0][0]
        start = 0

        for i, row in enumerate(results):
            if row[0] != current_symbol:
                symbol_dict[current_symbol] = (start, i - 1)
                start = i
                current_symbol = row[0]
        
        #handle last symbol
        symbol_dict[current_symbol] = (start, i)

        return symbol_dict


class _ScratchCache(object):
    @staticmethod
    def try_cache(ts_list, symbol_list, data_item, verbose=False,
                include_delisted=False, cache_miss_function=None, source=None):
        '''
        Read data into a DataFrame, but check to see if it is in a cache first.
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.  May be a list, in which case a list of DataFrame is returned.
        @param include_delisted: If true, delisted securities will be included.
        @note: If a symbol is not found then a message is printed. All the values in the column for that stock will be NaN. Execution then
        continues as usual. No errors are raised at the moment.
        '''

        # Construct hash -- filename where data may be already
        #
        # The idea here is to create a filename from the arguments provided.
        # We then check to see if the filename exists already, meaning that
        # the data has already been created and we can just read that file.

        # Create the hash for the symbols
        hashsyms = 0
        for i in symbol_list:
            hashsyms = (hashsyms + hash(i)) % 10000000

        # Create the hash for the timestamps
        hashts = 0

        # print "test point 1: " + str(len(ts_list))
        for i in ts_list:
            hashts = (hashts + hash(i)) % 10000000
        hashstr = 'qstk-' + str(source) + '-' + str(abs(hashsyms)) + '-' + str(abs(hashts)) \
            + '-' + str(hash(str(data_item)))
        if B_NEW == False:
            hashstr += '-old'

        # get the directory for scratch files from environment
        try:
            scratchdir = os.environ['QSSCRATCH']
        except KeyError:
            #self.rootdir = "/hzr71/research/QSData"
            raise KeyError("Please be sure to set the value for QSSCRATCH in config.sh or local.sh")

        # final complete filename
        cachefilename = scratchdir + '/' + hashstr + '.pkl'
        if verbose:
            print "cachefilename is:" + cachefilename

        # now eather read the pkl file, or do a hardread
        readfile = False  # indicate that we have not yet read the file

        #check if the cachestall variable is defined.

    #   catchstall=os.environ['CACHESTALLTIME']
        try:
            catchstall = datetime.timedelta(hours=int(os.environ['CACHESTALLTIME']))
        except:
            catchstall = datetime.timedelta(hours=12)

        # Check if the file is older than the cachestalltime
        if os.path.exists(cachefilename):
            if((datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(cachefilename))) < catchstall):
                if verbose:
                    print "cache hit"
                try:
                    cachefile = open(cachefilename, "rb")
                    start = time.time()  # start timer
                    retval = pickle.load(cachefile)
                    elapsed = time.time() - start  # end timer
                    readfile = True  # remember success
                    cachefile.close()
                except IOError:
                    if verbose:
                        print "error reading cache: " + cachefilename
                        print "recovering..."
                except EOFError:
                    if verbose:
                        print "error reading cache: " + cachefilename
                        print "recovering..."
        if (readfile != True):
            if verbose:
                print "cache miss"
                print "beginning hardread"
                start = time.time()  # start timer
                print "data_item(s): " + str(data_item)
                print "symbols to read: " + str(symbol_list)
            retval = cache_miss_function(ts_list,
                symbol_list, data_item, verbose, include_delisted)
            if verbose:
                elapsed = time.time() - start  # end timer
                print "end hardread"
                print "saving to cache"
            try:
                cachefile = open(cachefilename, "wb")
                pickle.dump(retval, cachefile, -1)
                os.chmod(cachefilename, 0666)
            except IOError:
                print "error writing cache: " + cachefilename
            if verbose:
                print "end saving to cache"
                print "reading took " + str(elapsed) + " seconds"
        return retval


class DataAccess(object):
    """
    Factory class that returns the requested data source driver
    """
    drivers = {'sqlite': _SQLite, 'mysql': _MySQL}

    def __new__(self, driver):
        if not DataAccess.drivers[driver]:
            raise NotImplementedError("DataAccess Driver: " + driver +
                                      " not available or implmented.")
        return DataAccess.drivers[driver]()


if __name__ == "__main__":
    db = DataAccess('mysql')

    date1 = datetime.datetime(2012, 2, 27, 16)
    date2 = datetime.datetime(2012, 2, 29, 16)

    print db.get_all_lists()
    print db.get_all_symbols()

    print db.get_list("S&P 1500 SubInd Industrial Machinery")

    print db.get_data([date1, date2], ["AAPL", "IBM", "GOOG", "A"], ["open", "close"])
