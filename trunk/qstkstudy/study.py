import pandas 
import Events as ev
import datetime as dt
import EventProfiler as ep
symbols = ['BFRE','ATCS','SERF']
#,'GDNEF']
#,'LAST','ATTUF','JBFCF','CYVA','SPF','XPO','EHECF','TEMO','AOLS','CSNT','REMI','GLRP','AIFLY','BEE','DJRT','CHSTF','AICAF']
startday = dt.datetime(2008,1,1)
endday = dt.datetime(2009,12,31)
eventMatrix = ev.findEvents(symbols,startday,endday)
eventProfiler = ep.EventProfiler(eventMatrix,startday,endday)
eventProfiler.study(filename="MyEventStudy.pdf")
