#
# Example use of the event profiler
#
import Events as ev
import datetime as dt
import EventProfiler as ep
symbols = open('symbol-set1.txt','r').read().splitlines()
startday = dt.datetime(2008,1,1)
endday = dt.datetime(2009,12,31)
eventMatrix = ev.findEvents(symbols,startday,endday)
eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=20,lookforward_days=20)
eventProfiler.study(filename="MyEventStudySet1.pdf")

symbols = open('symbol-set2.txt','r').read().splitlines()
eventMatrix = ev.findEvents(symbols,startday,endday)
eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=20,lookforward_days=20)
eventProfiler.study(filename="MyEventStudySet2.pdf")
