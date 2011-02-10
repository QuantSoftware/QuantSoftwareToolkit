"""
This demo demonstrates how to draw a dynamic mpl (matplotlib) 
plot in a wxPython application.

It allows "live" plotting as well as manual zooming to specific
regions.

Both X and Y axes allow "auto" or "manual" settings. For Y, auto
mode sets the scaling of the graph to see all the data points.
For X, auto mode makes the graph "follow" the data. Set it X min
to manual 0 to always see the whole data from the beginning.

Note: press Enter in the 'manual' text box to make a new value 
affect the plot.

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 31.07.2008
"""
import os
import pprint
import random
import sys
import wx
import cPickle
from numpy import vectorize

from qstkutil import timeutil as tu

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import matplotlib
matplotlib.use('WXAgg')

import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab


class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(55,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)

    def manual_value(self):
	return self.value
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()


class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'R&D Market Backtester'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
                
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)
        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)
	tests=['Single','Multiple']
	self.test=wx.Choice(self.panel,-1)
	self.test.AppendItems(tests)
	self.test.Select(n=0)

        self.strategy = wx.Choice(self.panel, -1)

	path=os.getcwd()
	path+='/strategies'
	list=os.listdir(path)
	self.strategy.AppendItems(list)
	self.strategy.Select(n=1)
	
        self.start = wx.DatePickerCtrl(self.panel, -1, style=wx.DP_DROPDOWN, size=(100,25))
        self.end = wx.DatePickerCtrl(self.panel, -1, style=wx.DP_DROPDOWN, size=(100,25))
        
        self.run_button = wx.Button(self.panel, -1, "Run Strategy")
        self.Bind(wx.EVT_BUTTON, self.on_run_button, self.run_button) 
        
        self.cb_grid = wx.CheckBox(self.panel, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)
        
        self.cb_xlab = wx.CheckBox(self.panel, -1, 
            "Show X labels",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(True)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.run_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
	self.hbox2.Add(self.test,border=5,flag=wx.ALL)
        self.hbox2.Add(self.strategy, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.start, border=5, flag=wx.ALL)
        self.hbox2.Add(self.end, border=5, flag=wx.ALL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW) 
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)       
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('Stock Graph', size=12)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        #
        self.plot_data = self.axes.plot(
            [0], 
            linewidth=1,
            color=(1, 1, 0),
            )[0]
    def date2epoch(self, input):
	inputarr=str(input).split('-')
	return tu.ymd2epoch(int(inputarr[0]), int(inputarr[1]), int(inputarr[2]))
	
    def draw_plot(self):
        """ Redraws the plot
        """
	self.axes.clear()
        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
	if(self.test.GetStringSelection()=='Single'):
		fund_input_file=open('out.pkl',"rb")
		funds=cPickle.load(fund_input_file)
		e2dvect=vectorize(self.date2epoch)
		self.axes.plot(e2dvect(funds.index), funds.values)
		xmin=min(e2dvect(funds.index))
		xmax=max(e2dvect(funds.index))
		ymin=min(funds.values)
		ymax=max(funds.values)
	else:
		fund_input_file=open('out1.pkl',"rb")
		funds=cPickle.load(fund_input_file)
		e2dvect=vectorize(self.date2epoch)
		self.axes.plot(e2dvect(funds.index), funds.values)
		xmin=min(e2dvect(funds.index))
		xmax=max(e2dvect(funds.index))
		ymin=min(funds.values)
		ymax=max(funds.values)
		for i in range(2,10):
			fund_input_file=open('out'+str(i)+'.pkl',"rb")
			funds=cPickle.load(fund_input_file)
			e2dvect=vectorize(self.date2epoch)
			self.axes.plot(e2dvect(funds.index), funds.values)
			if(xmin>min(e2dvect(funds.index))):
				xmin=min(e2dvect(funds.index))
			if(xmax<max(e2dvect(funds.index))):
				xmax=max(e2dvect(funds.index))
			if(ymin>min(funds.values)):
				ymin=min(funds.values)
			if(ymax<max(funds.values)):
				ymax=max(funds.values)
	self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin-100, upper=ymax+100)
        self.canvas.draw()
    
    def on_run_button(self, event):
	sselected = self.start.GetValue()
        smonth = sselected.Month + 1
        sday = sselected.Day
        syear = sselected.Year
        sdate_str = "%02d-%02d-%4d" % (smonth, sday, syear)
	eselected = self.end.GetValue()
        emonth = eselected.Month + 1
        eday = eselected.Day
        eyear = eselected.Year
	if(self.test.GetStringSelection()=='Single'):
	        sdate_str = "%02d-%02d-%4d" % (smonth, sday, syear)
        	edate_str = "%02d-%02d-%4d" % (emonth, eday, eyear)
		print 'python ./strategies/'+self.strategy.GetStringSelection()+' '+sdate_str+' '+edate_str
		os.system('python ./strategies/'+self.strategy.GetStringSelection()+' '+sdate_str+' '+edate_str)
		os.system('python quickSim.py allocations.pkl 1000 out.pkl')
	else:
		for i in range(1,10):
			sday+=1
			eday+=1
			if(sday>28):
				sday=1
			if(eday>28):
				eday=1
			sdate_str = "%02d-%02d-%4d" % (smonth, sday, syear)
        		edate_str = "%02d-%02d-%4d" % (emonth, eday, eyear)
			print 'python ./strategies/'+self.strategy.GetStringSelection()+' '+sdate_str+' '+edate_str
			os.system('python ./strategies/'+self.strategy.GetStringSelection()+' '+sdate_str+' '+edate_str)
			os.system('python quickSim.py allocations.pkl 1000 out'+str(i)+'.pkl')
        self.draw_plot()
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def on_exit(self, event):
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')


if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()
