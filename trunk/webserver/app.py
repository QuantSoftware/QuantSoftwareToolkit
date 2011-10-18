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
import xmlrpclib


# qstk imports
from qstkutil import DataAccess as da
from qstkutil import dateutil as du
from quicksim import quickSim as qs


serv=xmlrpclib.ServerProxy('http://127.0.0.1:8000')

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

render = web.template.render('templates/')

dataobj=da.DataAccess('Norgate')
stocksyms=['AAPL','GOOG']
print stocksyms

my_form = web.form.Form(
		web.form.Textbox('drop', description='Stock Input:'),
                web.form.Hidden('textfield', class_='textfield'),
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
	llMinRisk, llBalanced, llMaxReturns, binPng =serv.getChart(s.split(','))
	fout=open('./images/out.png','wb')
	fout.write(binPng.data)
	i=0
	table="<table style='border:1px solid black; border-collapse:collapse;'><th>Stock</th><th>Minimized Risk</th><th>Balanced</th><th>Maximized Risk</th></tr>"
	for x in s.split(','):
		table+="<tr><td>"+x+"</td><td>"+str(llMinRisk[i])+"</td><td>"+str(llBalanced[i])+"</td><td>"+str(llMaxReturns[i])+"</td></tr>"
		i+=1
	table+="</table>"
        return "<img width='100%' height='40%' src='/images/out.png'></img><br/><br/>"+table


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

