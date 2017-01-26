'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Jan 1, 2011

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains tutorial for backtester and report.

'''


import datetime as dt
from datetime import timedelta
import time as t
import numpy as np
import os
import pandas as pd


def _cache_dates():
    ''' Caches dates '''
    try:
        # filename = os.environ['QS'] + "/qstkutil/NYSE_dates.txt"
        filename = os.path.join(os.path.dirname(__file__), 'NYSE_dates.txt')
    except KeyError:
        print "Please be sure you have NYSE_dates.txt in the qstkutil directory"

    datestxt = np.loadtxt(filename, dtype=str)
    dates = []
    for i in datestxt:
        dates.append(dt.datetime.strptime(i, "%m/%d/%Y"))
    return pd.Series(index=dates, data=dates)

GTS_DATES = _cache_dates()



def getMonthNames():
    return(['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'])

def getYears(funds):
    years=[]
    for date in funds.index:
        if(not(date.year in years)):
            years.append(date.year)
    return(years)

def getMonths(funds,year):
    months=[]
    for date in funds.index:
        if((date.year==year) and not(date.month in months)):
            months.append(date.month)
    return(months)

def getDays(funds,year,month):
    days=[]
    for date in funds.index:
        if((date.year==year) and (date.month==month)):
            days.append(date)
    return(days)

def getDaysBetween(ts_start, ts_end):
    days=[]
    for i in range(0,(ts_end-ts_start).days):
        days.append(ts_start+timedelta(days=1)*i)
    return(days)

def getFirstDay(funds,year,month):
    for date in funds.index:
        if((date.year==year) and (date.month==month)):
            return(date)
    return('ERROR')

def getLastDay(funds,year,month):
    return_date = 'ERROR'
    for date in funds.index:
        if((date.year==year) and (date.month==month)):
            return_date = date
    return(return_date)

def getNextOptionClose(day, trade_days, offset=0):
    #get third friday in month of day
    #get first of month
    year_off=0
    if day.month+offset > 12:
        year_off = 1
        offset = offset - 12
    first = dt.datetime(day.year+year_off, day.month+offset, 1, hour=16)
    #get weekday
    day_num = first.weekday()
    #get first friday (friday - weekday) add 7 if less than 1
    dif = 5 - day_num
    if dif < 1:
        dif = dif+7
    #move to third friday
    dif = dif + 14
    friday = first+dt.timedelta(days=(dif-1))
    #if friday is a holiday, options expire then
    if friday in trade_days:
        month_close = first + dt.timedelta(days=dif)
    else:
        month_close = friday
    #if day is past the day after that
    if month_close < day:
        return_date = getNextOptionClose(day, trade_days, offset=1)
    else:
        return_date = month_close
    return(return_date)

def getLastOptionClose(day, trade_days):
    start = day
    while getNextOptionClose(day, trade_days)>=start:
        day= day - dt.timedelta(days=1)
    return(getNextOptionClose(day, trade_days))


def getNYSEoffset(mark, offset):
    ''' Returns NYSE date offset by number of days '''
    mark = mark.replace(hour=0, minute=0, second=0, microsecond=0)

    i = GTS_DATES.index.searchsorted(mark, side='right')
    # If there is no exact match, take first date in past
    if GTS_DATES[i] != mark:
        i -= 1

    ret = GTS_DATES[i + offset]

    ret = ret.replace(hour=16)

    return ret


def getNYSEdays(startday = dt.datetime(1964,7,5), endday = dt.datetime(2020,12,31),
    timeofday = dt.timedelta(0)):
    """
    @summary: Create a list of timestamps between startday and endday (inclusive)
    that correspond to the days there was trading at the NYSE. This function
    depends on a separately created a file that lists all days since July 4,
    1962 that the NYSE has been open, going forward to 2020 (based
    on the holidays that NYSE recognizes).

    @param startday: First timestamp to consider (inclusive)
    @param endday: Last day to consider (inclusive)
    @return list: of timestamps between startday and endday on which NYSE traded
    @rtype datetime
    """
    start = startday - timeofday
    end = endday - timeofday

    dates = GTS_DATES[start:end]

    ret = [x + timeofday for x in dates]

    return(ret)

def getNextNNYSEdays(startday, days, timeofday):
    """
    @summary: Create a list of timestamps from startday that is days days long
    that correspond to the days there was trading at  NYSE. This function
    depends on the file used in getNYSEdays and assumes the dates within are
    in order.
    @param startday: First timestamp to consider (inclusive)
    @param days: Number of timestamps to return
    @return list: List of timestamps starting at startday on which NYSE traded
    @rtype datetime
    """
    try:
        # filename = os.environ['QS'] + "/qstkutil/NYSE_dates.txt"
        filename = os.path.join(os.path.dirname(__file__), 'NYSE_dates.txt')
    except KeyError:
        print "Please be sure to set the value for QS in config.sh or\n"
        print "in local.sh and then \'source local.sh\'.\n"

    datestxt = np.loadtxt(filename,dtype=str)
    dates=[]
    for i in datestxt:
        if(len(dates)<days):
            if((dt.datetime.strptime(i,"%m/%d/%Y")+timeofday)>=startday):
                dates.append(dt.datetime.strptime(i,"%m/%d/%Y")+timeofday)
    return(dates)

def getPrevNNYSEday(startday, timeofday):
    """
    @summary: This function returns the last valid trading day before the start
    day, or returns the start day if it is a valid trading day. This function
    depends on the file used in getNYSEdays and assumes the dates within are
    in order.
    @param startday: First timestamp to consider (inclusive)
    @param days: Number of timestamps to return
    @return list: List of timestamps starting at startday on which NYSE traded
    @rtype datetime
    """
    try:
        # filename = os.environ['QS'] + "/qstkutil/NYSE_dates.txt"
        filename = os.path.join(os.path.dirname(__file__), 'NYSE_dates.txt')
    except KeyError:
        print "Please be sure to set the value for QS in config.sh or\n"
        print "in local.sh and then \'source local.sh\'.\n"

    datestxt = np.loadtxt(filename,dtype=str)

    #''' Set return to first day '''
    dtReturn = dt.datetime.strptime( datestxt[0],"%m/%d/%Y")+timeofday

    #''' Loop through all but first '''
    for i in datestxt[1:]:
        dtNext = dt.datetime.strptime(i,"%m/%d/%Y")

        #''' If we are > startday, then use previous valid day '''
        if( dtNext > startday ):
            break

        dtReturn = dtNext + timeofday

    return(dtReturn)

def ymd2epoch(year, month, day):
    """
    @summary: Convert YMD info into a unix epoch value.
    @param year: The year
    @param month: The month
    @param day: The day
    @return epoch: number of seconds since epoch
    """
    return(t.mktime(dt.date(year,month,day).timetuple()))

def epoch2date(ts):
    """
    @summary Convert seconds since epoch into date
    @param ts: Seconds since epoch
    @return thedate: A date object
    """
    tm = t.gmtime(ts)
    return(dt.date(tm.tm_year,tm.tm_mon,tm.tm_mday))


def _trade_dates(dt_start, dt_end, s_period):
    '''
    @summary: Generate dates on which we need to trade
    @param c_strat: Strategy config class
    @param dt_start: Start date
    @param dt_end: End date
    '''

    ldt_timestamps = getNYSEdays(dt_start,
                dt_end, dt.timedelta(hours=16) )


    # Use pandas reindex method instead
    # Note, dates are index as well as values, we select based on index
    # but return values since it is a numpy array of datetimes instead of
    # pandas specific.
    ts_dates = pd.TimeSeries(index=ldt_timestamps, data=ldt_timestamps)

    # These are the dates we want
    if s_period[:2] == 'BW':
        # special case for biweekly

        dr_range = pd.DateRange(dt_start, dt_end,
                                timeRule=s_period[1:])
        dr_range = np.asarray(dr_range)
        li_even = np.array(range(len(dr_range)))
        dr_range = dr_range[li_even[li_even % 2 == 0]]
    else:
        dr_range = pd.DateRange(dt_start, dt_end,
                                timeRule=s_period)
        dr_range = np.asarray(dr_range)


    # Warning, we MUST copy the date range, if we modify it it will be returned
    # in it's modified form the next time we use it.
    dr_range = np.copy(dr_range)
    dr_range += pd.DateOffset(hours=16)
    ts_dates = ts_dates.reindex( dr_range, method='bfill' )
    ldt_dates = ts_dates[ts_dates.notnull()].values

    #Make unique
    sdt_unique = set()
    ldt_dates = [x for x in ldt_dates
                 if x not in sdt_unique and not sdt_unique.add(x)]

    return ldt_dates
