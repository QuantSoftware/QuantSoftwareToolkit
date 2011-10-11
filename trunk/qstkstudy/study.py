import pandas 
import Events as ev
import datetime as dt
symbols = ['BFRE','ATCS']
startday = dt.datetime(2008,1,1)
endday = dt.datetime(2009,12,31)
eventMatrix = ev.findEvents(symbols,startday,endday)
import EventProfiler as ep
eventProfiler = ep.EventProfiler(eventMatrix,startday,endday)
eventProfiler.study(filename="MyEventStudy.pdf")
