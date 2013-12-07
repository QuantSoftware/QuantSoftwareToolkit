import datetime
import QSTK.qstkutil.qsdateutil
import StringIO
import math
import random

START = datetime.datetime(2000,2,1)
END = datetime.datetime(2012,9,13)
NUMFILES=400

def genfile(fname,dt_start,dt_end):
	datelist = QSTK.qstkutil.qsdateutil.getNYSEdays(dt_start,dt_end)
	#write_to = StringIO.StringIO()
	write_to = open(fname,"w")
	write_to.write("Date,Open,High,Low,Close,Volume,Adj Close\n")
	mean = 20.0+(random.random()*480.0)
	amp =  20.0*random.random()
	period = 10.0+(random.random()*100.0)
	sin_gen = lambda x: (mean+(amp*math.sin(((math.pi*2)/period)*x)))
	print fname,"parameters"
	print "Mean:",mean
	print "Amplitude:",amp
	print "Period:", period
	dllen = len(datelist)
	for t in xrange(dllen):
		date = datelist[(dllen-1)-t]
		val = sin_gen(t)
		line = (date.date().isoformat(),)+((val,)*5)
		write_to.write("%s,%f,%f,%f,%f,1,%f\n"%line)
	#print write_to.getvalue()
	write_to.close()

for i in xrange(NUMFILES):
	genfile("ML4T-%03d.csv"%i,START,END)
#genfile("foo.txt",datetime.datetime(2011,9,13),datetime.datetime(2012,9,13))
