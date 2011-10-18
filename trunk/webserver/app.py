import web
import os
import re
import base64
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


urls = ('/login','login',
	'/logout','logout',
	'/','tutorial',
	'/images/(.*)','images')


allowed = (
    ('admin','admin'),
    ('user','user')
)

web.config.debug = False
app = web.application(urls,globals())
session=web.session.Session(app,web.session.DiskStore('sessions'),initializer={'logged_in':False})


def make_text(string):
	symbols=string.split(",");
	tsstart = dt.datetime(2004,1,1)
	tsend = dt.datetime(2009,12,31)
	timeofday=dt.timedelta(hours=16)
	timestamps=du.getNYSEdays(tsstart,tsend,timeofday)
	
	# Get the data from the data store
	dataobj=da.DataAccess('Custom')
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
	return "<center><img src=./images/funds"+string+".png></center>"


render = web.template.render('templates/')

dataobj=da.DataAccess('Custom')
stocksyms=dataobj.get_all_symbols()
print stocksyms

my_form = web.form.Form(
		web.form.Dropdown('drop', stocksyms),
                web.form.Textbox('textfield', class_='textfield'),
                )

class tutorial:
    def GET(self):
	print str(session.get('logged_in',False))
	if session.get('logged_in',False):
		print 'logged_in!'
	        form = my_form()
        	return render.tutorial(form, "Your graph will show up here.")
	else:
		print 'not logged_in'
		return render.login()
        
    def POST(self):
        form = my_form()
        form.validates()
        s = form.value['textfield']
        return make_text(s)


class login:
    def GET(self):
	return render.login()

    def POST(self):
	name=web.input(username="no data")
	pass_code=web.input(password="no info")
	print str(name.username)
	print str(pass_code.password)
	if (str(name.username), str(pass_code.password)) in allowed :
		print 'authed'
		session.logged_in=True
		raise web.seeother('/')
	return '<html>Failed to login. Try to login <a href=./login>again?</a></html>'
	

class logout:
	def GET(self):
		session.logged_in = False
		return '<html>Logged out. Log back <a href=./login>in?</a></html>'

class images:
	def GET(self,name):
		print name
		ext = name.split(".")[-1]
	
		cType = {
			"png" :"images/png"
		}
		
		web.header("Content-Type", cType[ext])
		return open('images/%s'%name,"rb").read()


if __name__ == '__main__':
    app.internalerror = web.debugerror
    app.run()

