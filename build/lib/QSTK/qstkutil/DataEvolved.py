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
import numpy
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
        s_filepath = os.path.dirname(os.path.abspath(__file__))
        # Read password from a file (does not support whitespace)
        s_pass = open(os.path.join(s_filepath,'pass.txt')).read().rstrip()
        
        try:
            self.db = MySQLdb.connect("127.0.0.1", "finance", s_pass, "premiumdata")
        except:
            s_filepath = os.path.dirname(os.path.abspath(__file__))
            # Read password from a file (does not support whitespace)
            s_pass = open(os.path.join(s_filepath,'pass2.txt')).read().rstrip()
            self.db = MySQLdb.connect("127.0.0.1", "finance", s_pass, "premiumdata")

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
        columns_tech = []
        columns_fund = []
        results_tech = []
        results_fund = []
        # Check input data
        assert isinstance(ts_list, list)
        assert isinstance(symbol_list, list)
        assert isinstance(data_item, list)

        # Map to new database schema to preserve legacy code
        ds_map = {'open':'tropen',
                  'high':'trhigh',
                  'low':'trlow',
                  'close':'trclose',
                  'actual_close':'close',
                  'adjusted_close':'adjclose'}
        
        #keys for fundamental indicators
        ls_fund_keys = ['sharesout',
                        'latestavailableannual',
                        'latestavailableinterim',
                        'projfiscalyearend',
                        'peproj',
                        'pe',
                        'eps',
                        'dividend',
                        'yield',
                        'pegproj',
                        'p2b',
                        'p2s',
                        'totd2eq',
                        'ebitda',
                        'grossmargin'
                       ]
        
        

        data_item = data_item[:]
        data_fund = []
        li_fund_index = []
        data_tech = []
        li_tech_index = []
        for i, item in enumerate(data_item):
            if item in ls_fund_keys:
                data_fund.append(item)
                li_fund_index.append(i)
            else:
                data_tech.append(item)
                li_tech_index.append(i) 
            
        for i, item in enumerate(data_tech):     
            if item in ds_map.keys():
               data_tech[i] = ds_map[item]       
              
        # Combine Symbols List for Query
        symbol_query_list = ",".join(map(lambda x: "'" + x + "'", symbol_list))

        # Combine Data Fields for Query
        query_select_tech_items = ",".join(data_tech)
        
        query_select_fund_items = ",".join(data_fund)
        
        # Now convert to ID's 
        self.cursor.execute('''select assetid, code from asset 
                               where code in( ''' + symbol_query_list + ''')''')
        # Dictionary linking id's:symbols
        d_id_sym = dict(self.cursor.fetchall())

        ls_ids = d_id_sym.keys()
        s_idlist = ",".join([str(x) for x in ls_ids])
        
        s_query_tech = 'SELECT assetid, date, ' + query_select_tech_items + \
                       ' FROM priceadjusted WHERE assetid in (' + s_idlist + ')' + \
                       ' AND date >= %s AND date <= %s '
        
        s_query_fund = 'SELECT assetid, date, ' + query_select_fund_items + \
                       ' FROM fundamentals WHERE assetid in (' +s_idlist +')' + \
                       ' AND date >= %s AND date <= %s '
        
        if len(query_select_tech_items) !=0:
            try:
                self.cursor.execute(s_query_tech, (ts_list[0].replace(hour=0), ts_list[-1]))
            except:
                print 'Data error, probably using an non-existent symbol'
            
            # Retrieve Results
            results_tech = self.cursor.fetchall()
            # Create Data frames
            for i in range(len(data_tech)):
                columns_tech.append(pandas.DataFrame(index=ts_list, columns=symbol_list))


            # Loop through rows
            dt_time = datetime.time(hour=16)
            for row in results_tech:
                #format of row is (sym, date, item1, item2, ...)
                dt_date = datetime.datetime.combine(row[1], dt_time)
                if dt_date not in columns_tech[i].index:
                    continue
                # Add all columns to respective data-frames
                for i in range(len(data_tech)):
                    columns_tech[i][d_id_sym[row[0]]][dt_date] = row[i+2]
        
        if len(query_select_fund_items)!=0:        
            try:
                self.cursor.execute(s_query_fund, (ts_list[0].replace(hour=0), ts_list[-1]))
            except:
                print 'Data error, probably using an non-existent symbol'
            
            # Retrieve Results
            results_fund = self.cursor.fetchall()
            # Create Data frames
            for i in range(len(data_fund)):
                columns_fund.append(pandas.DataFrame(index=ts_list, columns=symbol_list))


            # Loop through rows
            dt_time = datetime.time(hour=16)
            for row in results_fund:
                #format of row is (sym, date, item1, item2, ...)
                dt_date = datetime.datetime.combine(row[1], dt_time)
                if dt_date not in columns_fund[i].index:
                    continue
                # Add all columns to respective data-frames
                for i in range(len(data_fund)):
                    columns_fund[i][d_id_sym[row[0]]][dt_date] = row[i+2]
        
        columns = [numpy.NaN]*len(data_item)    
        for i,item in enumerate(li_tech_index):
            columns[item]=columns_tech[i]
        for i,item in enumerate(li_fund_index):
            columns[item]=columns_fund[i]
   
        return columns 
  

    def get_dividends(self, ts_list, symbol_list):
        """
        Read dividend data into a DataFrame from SQLite
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        """

        # Combine Symbols List for Query
        symbol_query_list = ",".join(map(lambda x: "'" + x + "'", symbol_list))

        self.cursor.execute("""
        select code, exdate, divamt
        from dividend B, asset A where A.assetid = B.assetid and 
        B.exdate >= %s and B.exdate <= %s and A.code in (
        """ + symbol_query_list + """)""", (ts_list[0].replace(hour=0),
                                             ts_list[-1],))
        
        # Retrieve Results
        results = self.cursor.fetchall()

        # Remove all rows that were not asked for
        results = list(results)

        if len(results) == 0:
            return pandas.DataFrame(columns=symbol_list)
  
        # Create Pandas DataFrame in Expected Format
        current_dict = {}
        symbol_ranges = self._find_ranges_of_symbols(results)
        for symbol, ranges in symbol_ranges.items():
            current_symbol_data = results[ranges[0]:ranges[1] + 1]
        
            current_dict[symbol] = pandas.Series(map(itemgetter(2), 
                                                current_symbol_data),
                 index=map(lambda x: itemgetter(1)(x) + relativedelta(hours=16), 
                                              current_symbol_data))

                    
        # Make DataFrame
        ret = pandas.DataFrame(current_dict, columns=symbol_list)
        return ret.reindex(ts_list)


    def get_list(self, list_name):
        
        if type(list_name) == type('str') or \
           type(list_name) == type(u'unicode'):
            self.cursor.execute("""select symbol from premiumdata.lists
                                   where name=%s;""", (list_name))
        else:
            self.cursor.execute("""select myself.code as symbol from 
                indexconstituent consititue1_, asset myself
                where myself.assetid = consititue1_.assetid and myself.recordstatus=1 and myself.statuscodeid < 100 and 
                consititue1_.indexassetid = %s;""", (str(int(list_name))))

        return sorted([x[0] for x in self.cursor.fetchall()])

    def get_all_symbols(self):
        ''' Returns all symbols '''
        self.cursor.execute('''select distinct code from asset a where  
                               a.statuscodeid<100 and a.recordstatus=1''')
        return sorted([x[0] for x in self.cursor.fetchall()])

    def get_all_lists(self):
        

        self.cursor.execute("""select asset0_.assetid as id, asset0_.issuername as name
            from asset asset0_ where exists 
            (select consititue1_.assetid from indexconstituent consititue1_ 
            where asset0_.assetid=consititue1_.indexassetid) 
            order by asset0_.issuername;""")
        return sorted([x[1] for x in self.cursor.fetchall()])

    def get_last_date(self):
        ''' Returns last day of valid data '''
        self.cursor.execute( ''' select ts from premiumdata.price 
                p,premiumdata.asset a, (select assetid as id,max(date)
                as ts from premiumdata.price group by assetid) s
                where p.assetid = a.assetid and s.id = p.assetid and 
                p.date = s.ts and a.code='SPY';''')
        dt_ret = datetime.datetime.combine(self.cursor.fetchall()[0][0],
                                           datetime.time(16))
        return dt_ret
    
    def get_shares(self, symbol_list):
        ''' Returns list of values corresponding to shares outstanding '''
        
        symbol_query_list = ",".join(map(lambda x: "'" + x + "'", symbol_list))
        self.cursor.execute( ''' SELECT code, sharesoutstanding FROM asset a
                                 where code in (''' + symbol_query_list + ');' )

        return dict(self.cursor.fetchall())
        
         
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
    date3 = datetime.datetime(2012, 9, 29, 16)

    #print db.get_shares(['GOOG', 'AAPL'])

    #print db.get_all_lists()
    #print db.get_all_symbols()

    #print db.get_list('Dow Jones Transportation')
    
    #print db.get_dividends([date1 + datetime.timedelta(days=x) for x in range(100)],
    #                        ["MSFT", "PGF", "GOOG", "A"])

    print db.get_data_hard_read([date1, date2], ["AAPL", "IBM", "GOOG", "A"], ["open","ebitda","close","actual_close","pe"])
