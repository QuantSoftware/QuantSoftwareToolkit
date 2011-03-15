from datetime import timedelta
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
