import web
import os

from pylab import *
from pandas import *
import matplotlib.pyplot as plt
import time as t
import cPickle
import datetime as dt

# qstk imports
from qstkutil import DataAccess as da
from qstkutil import dateutil as du
from quicksim import quickSim as qs

def make_text(string):
	symbols=string.split(",");
	tsstart = dt.datetime(2004,1,1)
	tsend = dt.datetime(2009,12,31)
	timeofday=dt.timedelta(hours=16)
	timestamps=du.getNYSEdays(tsstart,tsend,timeofday)
	
	# Get the data from the data store
	dataobj=da.DataAccess('Norgate')
	historic = dataobj.get_data(timestamps,symbols,"close")
	
	# create alloc
	alloc_vals=.8/(len(historic.values[0,:])-1)*ones((1,len(historic.values[0,:])))
	alloc=DataMatrix(index=[historic.index[0]], data=alloc_vals, columns=symbols)
	for date in range(0, len(historic.index)):
	        if(historic.index[date].day==1):
	                alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=alloc_vals, columns=symbols))
	alloc[symbols[0]] = .1
	alloc['_CASH'] = .1
	
	#output to pickle file
	output=open("allocations.pkl","wb")
	cPickle.dump(alloc, output)
	
	#test allocation with quicksim
	funds=qs.quickSim(alloc,historic,1000)
	#output to pickle file
	output2=open("funds2.pkl","wb")
	cPickle.dump(funds, output2)
	
	#plot funds
	plt.clf()
	plt.plot(funds.index,funds.values)
	plt.ylabel('Fund Value')
	plt.xlabel('Date')
	plt.draw()
	savefig("./images/funds"+string+".png", format='png')
	return "<img src=funds"+string+".png>"

urls = ('/(.*)','tutorial')
render = web.template.render('templates/')

app = web.application(urls, globals())

my_form = web.form.Form(
                web.form.Textbox('', class_='textfield', id='textfield'),
                )

class tutorial:
    def GET(self,name):
	print name
	ext = name.split(".")[-1]

	cType = {
		"png" :"images/png"
	}
	
	if name in os.listdir('images'):
		web.header("Content-Type", cType[ext])
		return open('images/%s'%name,"rb").read()
	else:
	        form = my_form()
        	return render.tutorial(form, "Your text goes here.")
        
    def POST(self,name):
        form = my_form()
        form.validates()
        s = form.value['textfield']
        return make_text(s)

if __name__ == '__main__':
    app.run()

