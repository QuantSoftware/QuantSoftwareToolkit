import qstkutil.DataAccess as da
import qstkutil.dateutil as du
import datetime as dt

dataobj = da.DataAccess('Norgate')
delistSymbols = set(dataobj.get_symbols_in_sublist('/US/Delisted Securities'))
allSymbols = set(dataobj.get_all_symbols()) #by default Alive symbols only
aliveSymbols = list(allSymbols - delistSymbols) # set difference is smart

startday = dt.datetime(2008,1,1)
endday = dt.datetime(2009,12,31)
timeofday=dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday,endday,timeofday)

#Actual Close Prices of aliveSymbols and allSymbols
aliveSymbsclose = dataobj.get_data(timestamps, aliveSymbols, 'actual_close')
allSymbsclose = dataobj.get_data(timestamps, allSymbols, 'actual_close')

file = open('aliveSymbols2','w')
for symbol in aliveSymbols:
	belowdollar = len(aliveSymbsclose[symbol][aliveSymbsclose[symbol]<1.0])
	if belowdollar and (len(aliveSymbsclose[symbol]) > belowdollar):
		file.write(str(symbol)+'\n')
file.close()

file = open('allSymbols2','w')
for symbol in allSymbols:
        belowdollar =  len(allSymbsclose[symbol][allSymbsclose[symbol]<1.0])
        if belowdollar and (len(allSymbsclose[symbol]) > belowdollar):
                file.write(str(symbol)+'\n')
file.close()
