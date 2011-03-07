'''
Created on Sep 22, 2010

@author: Tucker Balch
@contact: tucker@cc.@gatech.edu
'''

__version__ = "$Revision: 156 $"

import time as t
import datetime as dt

def ymd2epoch(year, month, day):
	return(t.mktime(dt.date(year,month,day).timetuple()))

def epoch2date(ts):
	tm = t.gmtime(ts)
	return(dt.date(tm.tm_year,tm.tm_mon,tm.tm_mday))
