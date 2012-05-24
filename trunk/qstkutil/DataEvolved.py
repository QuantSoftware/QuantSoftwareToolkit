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
import pandas
import sqlite3
import datetime
import inspect
from operator import itemgetter


"""

Driver classes must overload the used driver interfaces methods

"""


class DriverInterface(object):
    def get_data(self, ts_list, symbol_list, data_item, verbose=False, bIncDelist=False):
        raise NotImplementedError("Selected Driver has not implmented get_data.")

    def get_all_symbols(self):
        raise NotImplementedError("Selected Driver has not implmented get_all_symbols.")

    def get_list(self, list_name):
        raise NotImplementedError("Selected Driver has not implmented get_list.")

    def get_all_lists(self):
        raise NotImplementedError("Selected Driver has not implmented get_all_lists.")

"""

SQLite driver >
    Need interface from above
    IsDataBaseSetup
    setupDatabase

"""


class _SQLite(DriverInterface):

    data_item_mapping = {'open': 'OpenPrice', 'high': 'AdjustedHiPrice',
                        'low': 'AdjustedLowPrice', 'close': 'AdjustedClosePrice',
                        'volume': 'Volume', 'actual close': 'ActualClosePrice'}

    def __init__(self):

        #try:
        #    self.sqldbfile = os.environ['QSDB']
        #except KeyError:
        #    raise RuntimeError("Database environment variable not set.")

        self.sqldbfile = "/Users/Jeffrey/Downloads/QSDB"

        self._connect()
        if not self.is_database_setup():
            self.init_database()

    def _connect(self):
        self.connection = sqlite3.connect(self.sqldbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.connection.cursor()

    def is_database_setup(self):
        return True

    def get_data(self, ts_list, symbol_list, data_item, verbose=False, bIncDelist=False):
        columns = []
        results = []

        # Check input data
        assert isinstance(ts_list, list)
        assert isinstance(symbol_list, list)
        assert isinstance(data_item, list)

        # Combine Symbols List for Query
        symbol_query_list = ",".join(map(lambda x: "'" + x + "'", symbol_list))

        # Combine Data Fields for Query
        data_item[:] = map(lambda x: _SQLite.data_item_mapping[x], data_item)
        data_item[:] = map(lambda x: "B." + x, data_item)
        query_select_items = ",".join(data_item)

        # Build Query - Inherently Unsafe!
        self.cursor.execute("""
                SELECT A.Symbol,B.TradingDateTime,""" + query_select_items + """
                FROM tblEquity A JOIN tblPriceVolumeHistory B ON A.ID = B.tblEquity_ID
                WHERE B.TradingDateTime >= (?) AND B.TradingDateTime <= (?) AND A.Symbol IN (%s)
                ORDER BY A.Symbol ASC
            """ % symbol_query_list, (ts_list[0], ts_list[-1],))

        # Retrieve Results
        results = self.cursor.fetchall()

        # Remove all rows that were not asked for
        for i, row in enumerate(results):
            if row[1] not in ts_list:
                del results[i]

        # Create Pandas DataFrame in Expected Format
        currentDict = {}
        for currentColumn in range(len(data_item)):
            for symbol in symbol_list:
                current_symbol_data = self._slice_results_by_symbol(symbol, results)
                currentDict[symbol] = pandas.Series(
                                        map(itemgetter(currentColumn + 2), current_symbol_data),
                                        index=map(itemgetter(1), current_symbol_data))
            # Make DataFrame
            columns.append(pandas.DataFrame(currentDict, columns=symbol_list))

        return columns

    def get_list(self, name):
        self.cursor.execute("""SELECT A.Symbol
                    FROM tblEquity A JOIN tblListDetail C ON A.ID = C.tblEquity_ID
                    JOIN tblListHeader B ON B.ID = C.tblListHeader_ID
                    WHERE B.ListName = ?
        """, (name,))
        return self.cursor.fetchall()

    def get_all_symbols(self):
        self.cursor.execute("SELECT DISTINCT symbol FROM tblEquity")
        return self.cursor.fetchall()

    def get_all_lists(self):
        self.cursor.execute("SELECT ListName FROM tblListHeader")
        return self.cursor.fetchall()

    def _slice_results_by_symbol(self, symbol, results):
        found = False
        for i, row in enumerate(results):
            if row[0] == symbol and found is False:
                first = i
                found = True
            if found is True:
                if i == (len(results) - 1):  # Check if we are at the end of the list
                    return results[first:i + 1]
                elif row[0] == symbol:
                    continue
                else:
                    return results[first:i]
        return None


class _Norgate(DriverInterface):

    def __init__(self):
        try:
            self.rootdir = os.environ['QSDATA']
        except KeyError:
            raise KeyError("Please be sure to set the value for QSDATA in config.sh or local.sh")

        self.folderList = list()
        self.folderSubList = list()
        self.fileExtensionToRemove = ".pkl"

        self.midPath = "/Processed/Norgate/Stocks/"
        self.folderSubList.append("/US/AMEX/")
        self.folderSubList.append("/US/NASDAQ/")
        self.folderSubList.append("/US/NYSE/")
        self.folderSubList.append("/US/NYSE Arca/")
        self.folderSubList.append("/US/OTC/")
        self.folderSubList.append("/US/Delisted Securities/")
        self.folderSubList.append("/US/Indices/")

        for i in self.folderSubList:
            self.folderList.append(self.rootdir + self.midPath + i)


class _Compustat(DriverInterface):

    def __init__(self):
        pass


class DataAccess(object):
    drivers = {'sqlite': _SQLite}

    def __new__(self, driver):
        print "Creating new DataAccess Module."
        if not DataAccess.drivers[driver]:
            raise NotImplementedError("DataAccess Driver: " + driver +
                                      " not available or implmented.")
        return DataAccess.drivers[driver]()


d = DataAccess('sqlite')

date1 = datetime.datetime(2012, 2, 27, 16)
date2 = datetime.datetime(2012, 2, 29, 16)

#print d.get_all_lists()
#print d.get_all_symbols()

print d.get_list("S&P 1500 SubInd Industrial Machinery")

print d.get_data([date1, date2], ["AAPL", "IBM", "GOOG"], ["open", "close"])
