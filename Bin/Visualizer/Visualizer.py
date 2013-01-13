'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on April, 20, 2012

@author: Sourabh Bajaj
@contact: sourabhbajaj90@gmail.com
@summary: Visualizer Main Code

'''
import sys
import numpy as np
import math 
import os
import dircache

import AccessData as AD
import pickle
from PyQt4 import QtGui, QtCore, Qt
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


# SLIDER range variable for all the range slider. Increasing this will increase precision
SLIDER_RANGE=100
LOOKBACK_DAYS=20


# Range Slider Class, to implement the custom range slider.
class RangeSlider(QtGui.QSlider):
    """ A slider for ranges.
    
        This class provides a dual-slider for ranges, where there is a defined
        maximum and minimum, as is a normal slider, but instead of having a
        single slider value, there are 2 slider values.
        
        This class emits the same signals as the QSlider base class, with the 
        exception of valueChanged
    """
    def __init__(self, *args):
        super(RangeSlider, self).__init__(*args)
        
        self._low = self.minimum()
        self._high = self.maximum()
        
        self.pressed_control = QtGui.QStyle.SC_None
        self.hover_control = QtGui.QStyle.SC_None
        self.click_offset = 0
        
        # 0 for the low, 1 for the high, -1 for both
        self.active_slider = 0

    def low(self):
        return self._low

    def setLow(self, low):
        self._low = low
        self.update()

    def high(self):
        return self._high

    def setHigh(self, high):
        self._high = high
        self.update()
        
        
    def paintEvent(self, event):
        # based on http://qt.gitorious.org/qt/qt/blobs/master/src/gui/widgets/qslider.cpp

        painter = QtGui.QPainter(self)
        style = QtGui.QApplication.style() 
        
        for i, value in enumerate([self._low, self._high]):
            opt = QtGui.QStyleOptionSlider()
            self.initStyleOption(opt)

            # Only draw the groove for the first slider so it doesn't get drawn
            # on top of the existing ones every time
            if i == 0:
                opt.subControls = QtGui.QStyle.SC_SliderHandle#QtGui.QStyle.SC_SliderGroove | QtGui.QStyle.SC_SliderHandle
            else:
                opt.subControls = QtGui.QStyle.SC_SliderHandle

            if self.tickPosition() != self.NoTicks:
                opt.subControls |= QtGui.QStyle.SC_SliderTickmarks

            if self.pressed_control:
                opt.activeSubControls = self.pressed_control
                opt.state |= QtGui.QStyle.State_Sunken
            else:
                opt.activeSubControls = self.hover_control

            opt.sliderPosition = value
            opt.sliderValue = value                                  
            style.drawComplexControl(QtGui.QStyle.CC_Slider, opt, painter, self)
            
        
    def mousePressEvent(self, event):
        event.accept()
        
        style = QtGui.QApplication.style()
        button = event.button()
        
        # In a normal slider control, when the user clicks on a point in the 
        # slider's total range, but not on the slider part of the control the
        # control would jump the slider value to where the user clicked.
        # For this control, clicks which are not direct hits will slide both
        # slider parts
                
        if button:
            opt = QtGui.QStyleOptionSlider()
            self.initStyleOption(opt)

            self.active_slider = -1
            
            for i, value in enumerate([self._low, self._high]):
                opt.sliderPosition = value                
                hit = style.hitTestComplexControl(style.CC_Slider, opt, event.pos(), self)
                if hit == style.SC_SliderHandle:
                    self.active_slider = i
                    self.pressed_control = hit
                    
                    self.triggerAction(self.SliderMove)
                    self.setRepeatAction(self.SliderNoAction)
                    self.setSliderDown(True)
                    break

            if self.active_slider < 0:
                self.pressed_control = QtGui.QStyle.SC_SliderHandle
                self.click_offset = self.__pixelPosToRangeValue(self.__pick(event.pos()))
                self.triggerAction(self.SliderMove)
                self.setRepeatAction(self.SliderNoAction)
        else:
            event.ignore()
                                
    def mouseMoveEvent(self, event):
        if self.pressed_control != QtGui.QStyle.SC_SliderHandle:
            event.ignore()
            return
        
        event.accept()
        new_pos = self.__pixelPosToRangeValue(self.__pick(event.pos()))
        opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(opt)
        
        if self.active_slider < 0:
            offset = new_pos - self.click_offset
            self._high += offset
            self._low += offset
            if self._low < self.minimum():
                diff = self.minimum() - self._low
                self._low += diff
                self._high += diff
            if self._high > self.maximum():
                diff = self.maximum() - self._high
                self._low += diff
                self._high += diff            
        elif self.active_slider == 0:
            if new_pos >= self._high:
                new_pos = self._high - 1
            self._low = new_pos
        else:
            if new_pos <= self._low:
                new_pos = self._low + 1
            self._high = new_pos

        self.click_offset = new_pos

        self.update()

        self.emit(QtCore.SIGNAL('sliderMoved'), self._low, self._high)
            
    def __pick(self, pt):
        if self.orientation() == QtCore.Qt.Horizontal:
            return pt.x()
        else:
            return pt.y()
           
    def __pixelPosToRangeValue(self, pos):
        opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(opt)
        style = QtGui.QApplication.style()
        
        gr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderGroove, self)
        sr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderHandle, self)
        
        if self.orientation() == QtCore.Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1
            
        return style.sliderValueFromPosition(self.minimum(), self.maximum(),
                                             pos-slider_min, slider_max-slider_min,
                                             opt.upsideDown)


###########################
##  Visualizer Class     ##
###########################

# Main class that contains the Visualizer Qt and all functions
class Visualizer(QtGui.QMainWindow):
    
	def __init__(self):
		super(Visualizer, self).__init__()
		# Initialization is a 3 phase process : Loading Data, Declaring Variables and Creating the GUI
		self.LoadData()
		self.Reset()
		self.create_main_frame()
		self.ResetFunc()
        
	def create_main_frame(self):
		# Setting Up the Main Frame of the GUI

		self.main_frame = QtGui.QWidget()
		self.statusBar().showMessage('Loading')

		# Declaring the matplotlib canvas for plotting graphs
		self.dpi=100
		self.fig = Figure((6.0, 5.5), dpi=self.dpi)
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.main_frame)
		self.ax = self.fig.gca(projection='3d')

		self.fig2 = Figure((6.0, 6.0), dpi=self.dpi*2)
		self.canvas2 = FigureCanvas(self.fig2)
		self.ax2 = self.fig2.gca(projection='3d')
		self.datetext2 = self.ax2.text2D(0, 1, 'Date : ', transform=self.ax2.transAxes)

		self.datetext = self.ax.text2D(0, 1, 'Date : ', transform=self.ax.transAxes)
		
		# Declaring the Texts in the GUI, fonts and Spacers to control the size of sliders	
		self.FactorLable=QtGui.QLabel('Factors', self)
		self.font = QtGui.QFont("Times", 16, QtGui.QFont.Bold, True)
		self.font1 = QtGui.QFont("Times", 12)
		self.font2 = QtGui.QFont("Times", 14, QtGui.QFont.Bold, True)
		self.font3 = QtGui.QFont("Times", 20, QtGui.QFont.Bold, True)
		self.VisLable = QtGui.QLabel('QuantViz', self)
		self.SpacerItem1 = Qt.QSpacerItem(450,0,Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Expanding)		
		self.SpacerItem2 = Qt.QSpacerItem(300,0,Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Expanding)	
		self.SpacerItem3 = Qt.QSpacerItem(300,0,Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Expanding)	
		self.SpacerItem4 = Qt.QSpacerItem(1,500,Qt.QSizePolicy.Fixed)	
		self.VisLable.setFont(self.font3)
		self.FactorLable.setFont(self.font)


########### Region for declaring the varibles associated with X Axis ########################

		self.XLable=QtGui.QLabel('X', self)
		self.XLable.setFont(self.font2)

		self.XCombo = QtGui.QComboBox(self)
		self.XCombo.activated[str].connect(self.XComboActivated)

		self.XMinTag=QtGui.QLabel('Min :', self)
		self.XMaxTag=QtGui.QLabel('Max :', self)
		self.XLimitTag=QtGui.QLabel('Scale:', self)
		self.XSliceTag=QtGui.QLabel('Slice :', self)

		self.XMinLable=QtGui.QLabel(str(self.XMin), self)
		self.XMinLable.setFont(self.font1)
		
		self.XRange=RangeSlider(Qt.Qt.Horizontal)
		self.XRangeSlice=RangeSlider(Qt.Qt.Horizontal)

		self.XMaxLable=QtGui.QLabel(str(self.XMax), self)
		self.XMaxLable.setFont(self.font1)
		
		self.XMin_Box= QtGui.QLineEdit()	
		self.XMax_Box= QtGui.QLineEdit()	
		self.XMinSlice_Box= QtGui.QLineEdit()	
		self.XMaxSlice_Box= QtGui.QLineEdit()

		self.XMin_Box.setMaxLength(4)
		self.XMax_Box.setMaxLength(4)
		self.XMinSlice_Box.setMaxLength(4)	
		self.XMaxSlice_Box.setMaxLength(4)
		
		self.XMin_Box.setFixedSize(50,27)
		self.XMax_Box.setFixedSize(50,27)
		self.XMinSlice_Box.setFixedSize(50,27)	
		self.XMaxSlice_Box.setFixedSize(50,27)

		self.connect(self.XMin_Box, QtCore.SIGNAL('editingFinished()'), self.XMin_BoxInput)
		self.connect(self.XMax_Box, QtCore.SIGNAL('editingFinished()'), self.XMax_BoxInput)
		self.connect(self.XMinSlice_Box, QtCore.SIGNAL('editingFinished()'), self.XMinSlice_BoxInput)
		self.connect(self.XMaxSlice_Box, QtCore.SIGNAL('editingFinished()'), self.XMaxSlice_BoxInput)

############# GUI Box - Related to X ###################

		Xhbox1 = QtGui.QHBoxLayout()
        
		for w in [ self.XLable, self.XCombo]:
			Xhbox1.addWidget(w)
			Xhbox1.setAlignment(w, QtCore.Qt.AlignVCenter)
		Xhbox1.addStretch(1)

		Xhbox2 = QtGui.QHBoxLayout()
        
		for w in [self.XMinTag, self.XMinLable]:
			Xhbox2.addWidget(w)
			Xhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)
		Xhbox2.addStretch(1)
		for w in [self.XMaxTag, self.XMaxLable]:
			Xhbox2.addWidget(w)
			Xhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Xhbox3 = QtGui.QHBoxLayout()
        
		for w in [  self.XLimitTag ,self.XMin_Box, self.XRange, self.XMax_Box]:
			Xhbox3.addWidget(w)
			Xhbox3.setAlignment(w, QtCore.Qt.AlignVCenter)

		Xhbox4 = QtGui.QHBoxLayout()
        
		for w in [  self.XSliceTag, self.XMinSlice_Box, self.XRangeSlice, self.XMaxSlice_Box]:
			Xhbox4.addWidget(w)
			Xhbox4.setAlignment(w, QtCore.Qt.AlignVCenter)

		Xvbox1 = QtGui.QVBoxLayout()
		Xvbox1.addLayout(Xhbox1)
		Xvbox1.addLayout(Xhbox2)
		Xvbox1.addLayout(Xhbox3)
		Xvbox1.addLayout(Xhbox4)

########### Region for declaring the varibles associated with Y Axis ########################

		self.YLable=QtGui.QLabel('Y', self)
		self.YLable.setFont(self.font2)

		self.YCombo = QtGui.QComboBox(self)
		self.YCombo.activated[str].connect(self.YComboActivated)

		self.YMinTag=QtGui.QLabel('Min :', self)
		self.YMaxTag=QtGui.QLabel('Max :', self)
		self.YLimitTag=QtGui.QLabel('Scale:', self)
		self.YSliceTag=QtGui.QLabel('Slice :', self)

		self.YMinLable=QtGui.QLabel(str(self.YMin), self)
		self.YMinLable.setFont(self.font1)
		
		self.YRange=RangeSlider(Qt.Qt.Horizontal)
		self.YRangeSlice=RangeSlider(Qt.Qt.Horizontal)

		self.YMaxLable=QtGui.QLabel(str(self.YMax), self)
		self.YMaxLable.setFont(self.font1)
		
		self.YMin_Box= QtGui.QLineEdit()	
		self.YMax_Box= QtGui.QLineEdit()	
		self.YMinSlice_Box= QtGui.QLineEdit()	
		self.YMaxSlice_Box= QtGui.QLineEdit()

		self.YMin_Box.setMaxLength(4)
		self.YMax_Box.setMaxLength(4)
		self.YMinSlice_Box.setMaxLength(4)	
		self.YMaxSlice_Box.setMaxLength(4)
		
		self.YMin_Box.setFixedSize(50,27)
		self.YMax_Box.setFixedSize(50,27)
		self.YMinSlice_Box.setFixedSize(50,27)	
		self.YMaxSlice_Box.setFixedSize(50,27)

		self.connect(self.YMin_Box, QtCore.SIGNAL('editingFinished()'), self.YMin_BoxInput)
		self.connect(self.YMax_Box, QtCore.SIGNAL('editingFinished()'), self.YMax_BoxInput)
		self.connect(self.YMinSlice_Box, QtCore.SIGNAL('editingFinished()'), self.YMinSlice_BoxInput)
		self.connect(self.YMaxSlice_Box, QtCore.SIGNAL('editingFinished()'), self.YMaxSlice_BoxInput)

############# GUI Box - Related to Y ###################

		Yhbox1 = QtGui.QHBoxLayout()
        
		for w in [ self.YLable, self.YCombo]:
			Yhbox1.addWidget(w)
			Yhbox1.setAlignment(w, QtCore.Qt.AlignVCenter)
		Yhbox1.addStretch(1)

		Yhbox2 = QtGui.QHBoxLayout()
        
		for w in [self.YMinTag, self.YMinLable]:
			Yhbox2.addWidget(w)
			Yhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)
		Yhbox2.addStretch(1)
		for w in [self.YMaxTag, self.YMaxLable]:
			Yhbox2.addWidget(w)
			Yhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Yhbox3 = QtGui.QHBoxLayout()
        
		for w in [ self.YLimitTag, self.YMin_Box, self.YRange, self.YMax_Box]:
			Yhbox3.addWidget(w)
			Yhbox3.setAlignment(w, QtCore.Qt.AlignVCenter)

		Yhbox4 = QtGui.QHBoxLayout()
        
		for w in [  self.YSliceTag,self.YMinSlice_Box, self.YRangeSlice, self.YMaxSlice_Box]:
			Yhbox4.addWidget(w)
			Yhbox4.setAlignment(w, QtCore.Qt.AlignVCenter)

		Yvbox1 = QtGui.QVBoxLayout()
		Yvbox1.addLayout(Yhbox1)
		Yvbox1.addLayout(Yhbox2)
		Yvbox1.addLayout(Yhbox3)
		Yvbox1.addLayout(Yhbox4)

########### Region for declaring the varibles associated with Z Axis ########################

		self.ZLable=QtGui.QLabel('Z', self)
		self.ZLable.setFont(self.font2)		
	
		self.ZCombo = QtGui.QComboBox(self)
		self.ZCombo.activated[str].connect(self.ZComboActivated)
	
		self.ZMinTag=QtGui.QLabel('Min :', self)
		self.ZMaxTag=QtGui.QLabel('Max :', self)
		self.ZLimitTag=QtGui.QLabel('Scale:', self)
		self.ZSliceTag=QtGui.QLabel('Slice :', self)

		self.ZMinLable=QtGui.QLabel(str(self.ZMin), self)
		self.ZMinLable.setFont(self.font1)
		
		self.ZRange=RangeSlider(Qt.Qt.Horizontal)
		self.ZRangeSlice=RangeSlider(Qt.Qt.Horizontal)

		self.ZMaxLable=QtGui.QLabel(str(self.ZMax), self)
		self.ZMaxLable.setFont(self.font1)
		
		self.ZMin_Box= QtGui.QLineEdit()	
		self.ZMax_Box= QtGui.QLineEdit()	
		self.ZMinSlice_Box= QtGui.QLineEdit()	
		self.ZMaxSlice_Box= QtGui.QLineEdit()

		self.ZMin_Box.setMaxLength(4)
		self.ZMax_Box.setMaxLength(4)
		self.ZMinSlice_Box.setMaxLength(4)	
		self.ZMaxSlice_Box.setMaxLength(4)
		
		self.ZMin_Box.setFixedSize(50,27)
		self.ZMax_Box.setFixedSize(50,27)
		self.ZMinSlice_Box.setFixedSize(50,27)	
		self.ZMaxSlice_Box.setFixedSize(50,27)

		self.connect(self.ZMin_Box, QtCore.SIGNAL('editingFinished()'), self.ZMin_BoxInput)
		self.connect(self.ZMax_Box, QtCore.SIGNAL('editingFinished()'), self.ZMax_BoxInput)
		self.connect(self.ZMinSlice_Box, QtCore.SIGNAL('editingFinished()'), self.ZMinSlice_BoxInput)
		self.connect(self.ZMaxSlice_Box, QtCore.SIGNAL('editingFinished()'), self.ZMaxSlice_BoxInput)

############# GUI Box - Related to Z ###################

		Zhbox1 = QtGui.QHBoxLayout()
        
		for w in [ self.ZLable, self.ZCombo]:
			Zhbox1.addWidget(w)
			Zhbox1.setAlignment(w, QtCore.Qt.AlignVCenter)
		Zhbox1.addStretch(1)

		Zhbox2 = QtGui.QHBoxLayout()
        
		for w in [self.ZMinTag, self.ZMinLable]:
			Zhbox2.addWidget(w)
			Zhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)
		Zhbox2.addStretch(1)
		for w in [self.ZMaxTag, self.ZMaxLable]:
			Zhbox2.addWidget(w)
			Zhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Zhbox3 = QtGui.QHBoxLayout()
        
		for w in [ self.ZLimitTag ,self.ZMin_Box, self.ZRange, self.ZMax_Box]:
			Zhbox3.addWidget(w)
			Zhbox3.setAlignment(w, QtCore.Qt.AlignVCenter)

		Zhbox4 = QtGui.QHBoxLayout()
        
		for w in [  self.ZSliceTag,self.ZMinSlice_Box, self.ZRangeSlice, self.ZMaxSlice_Box]:
			Zhbox4.addWidget(w)
			Zhbox4.setAlignment(w, QtCore.Qt.AlignVCenter)

		Zvbox1 = QtGui.QVBoxLayout()
		Zvbox1.addLayout(Zhbox1)
		Zvbox1.addLayout(Zhbox2)
		Zvbox1.addLayout(Zhbox3)
		Zvbox1.addLayout(Zhbox4)

########### Region for declaring the varibles associated with Size ########################

		self.SizeLable=QtGui.QLabel('Size   ', self)
		self.SizeLable.setFont(self.font2)

		self.SizeCombo = QtGui.QComboBox(self)
		self.SizeCombo.activated[str].connect(self.SComboActivated)

		self.SMinTag=QtGui.QLabel('Min :', self)
		self.SMaxTag=QtGui.QLabel('Max :', self)
		self.SLimitTag=QtGui.QLabel('Scale:', self)
		self.SSliceTag=QtGui.QLabel('Slice :', self)

		self.SMinLable=QtGui.QLabel(str(self.SMin), self)
		self.SMinLable.setFont(self.font1)
		
		self.SRange=RangeSlider(Qt.Qt.Horizontal)
		self.SRangeSlice=RangeSlider(Qt.Qt.Horizontal)

		self.SMaxLable=QtGui.QLabel(str(self.SMax), self)
		self.SMaxLable.setFont(self.font1)

		self.SMin_Box= QtGui.QLineEdit()	
		self.SMax_Box= QtGui.QLineEdit()	
		self.SMin_Box.setMaxLength(4)
		self.SMax_Box.setMaxLength(4)
		self.SMin_Box.setFixedSize(50,27)
		self.SMax_Box.setFixedSize(50,27)

		self.connect(self.SMin_Box, QtCore.SIGNAL('editingFinished()'), self.SMin_BoxInput)
		self.connect(self.SMax_Box, QtCore.SIGNAL('editingFinished()'), self.SMax_BoxInput)

		self.SMinSlice_Box= QtGui.QLineEdit()	
		self.SMaxSlice_Box= QtGui.QLineEdit()
		self.SMinSlice_Box.setMaxLength(4)	
		self.SMaxSlice_Box.setMaxLength(4)
		self.SMinSlice_Box.setFixedSize(50,27)	
		self.SMaxSlice_Box.setFixedSize(50,27)

		self.connect(self.SMinSlice_Box, QtCore.SIGNAL('editingFinished()'), self.SMinSlice_BoxInput)
		self.connect(self.SMaxSlice_Box, QtCore.SIGNAL('editingFinished()'), self.SMaxSlice_BoxInput)

############# GUI Box - Related to Size ###################

		Shbox1 = QtGui.QHBoxLayout()

		for w in [  self.SizeLable, self.SizeCombo]:
			Shbox1.addWidget(w)
			Shbox1.setAlignment(w, QtCore.Qt.AlignVCenter)
		
		Shbox1.addStretch(1)

		Shbox2 = QtGui.QHBoxLayout()
        
		for w in [self.SMinTag, self.SMinLable]:
			Shbox2.addWidget(w)
			Shbox2.setAlignment(w, QtCore.Qt.AlignVCenter)
		Shbox2.addStretch(1)
		for w in [self.SMaxTag, self.SMaxLable]:
			Shbox2.addWidget(w)
			Shbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Shbox3 = QtGui.QHBoxLayout()
        
		for w in [ self.SLimitTag ,self.SMin_Box, self.SRange, self.SMax_Box]:
			Shbox3.addWidget(w)
			Shbox3.setAlignment(w, QtCore.Qt.AlignVCenter)

		Shbox4 = QtGui.QHBoxLayout()
        
		for w in [  self.SSliceTag, self.SMinSlice_Box, self.SRangeSlice, self.SMaxSlice_Box]:
			Shbox4.addWidget(w)
			Shbox4.setAlignment(w, QtCore.Qt.AlignVCenter)

		Svbox1 = QtGui.QVBoxLayout()
		Svbox1.addLayout(Shbox1)
		Svbox1.addLayout(Shbox2)
		Svbox1.addLayout(Shbox3)
		Svbox1.addLayout(Shbox4)

########### Region for declaring the varibles associated with Color ########################

		self.ColorLable=QtGui.QLabel('Color', self)
		self.ColorLable.setFont(self.font2)

		self.ColorCombo = QtGui.QComboBox(self)
		self.ColorCombo.activated[str].connect(self.CComboActivated)

		self.CMinTag=QtGui.QLabel('Min :', self)
		self.CMaxTag=QtGui.QLabel('Max :', self)
		self.CLimitTag=QtGui.QLabel('Scale:', self)
		self.CSliceTag=QtGui.QLabel('Slice :', self)

		self.CMinLable=QtGui.QLabel(str(self.CMin), self)
		self.CMinLable.setFont(self.font1)
		
		self.CRange=RangeSlider(Qt.Qt.Horizontal)
		self.CRangeSlice=RangeSlider(Qt.Qt.Horizontal)

		self.CMaxLable=QtGui.QLabel(str(self.CMax), self)
		self.CMaxLable.setFont(self.font1)

		self.CMin_Box= QtGui.QLineEdit()	
		self.CMax_Box= QtGui.QLineEdit()	
		self.CMin_Box.setMaxLength(4)
		self.CMax_Box.setMaxLength(4)
		self.CMin_Box.setFixedSize(50,27)
		self.CMax_Box.setFixedSize(50,27)

		self.connect(self.CMin_Box, QtCore.SIGNAL('editingFinished()'), self.CMin_BoxInput)
		self.connect(self.CMax_Box, QtCore.SIGNAL('editingFinished()'), self.CMax_BoxInput)

		self.CMinSlice_Box= QtGui.QLineEdit()	
		self.CMaxSlice_Box= QtGui.QLineEdit()
		self.CMinSlice_Box.setMaxLength(4)	
		self.CMaxSlice_Box.setMaxLength(4)
		self.CMinSlice_Box.setFixedSize(50,27)	
		self.CMaxSlice_Box.setFixedSize(50,27)

		self.connect(self.CMinSlice_Box, QtCore.SIGNAL('editingFinished()'), self.CMinSlice_BoxInput)
		self.connect(self.CMaxSlice_Box, QtCore.SIGNAL('editingFinished()'), self.CMaxSlice_BoxInput)


############# GUI Box - Related to Color ###################

		Chbox1 = QtGui.QHBoxLayout()

		for w in [self.ColorLable, self.ColorCombo]:
			Chbox1.addWidget(w)
			Chbox1.setAlignment(w, QtCore.Qt.AlignVCenter)

		Chbox1.addStretch(1)
		Chbox2 = QtGui.QHBoxLayout()
        
		for w in [self.CMinTag, self.CMinLable]:
			Chbox2.addWidget(w)
			Chbox2.setAlignment(w, QtCore.Qt.AlignVCenter)
		Chbox2.addStretch(2)
		for w in [self.CMaxTag, self.CMaxLable]:
			Chbox2.addWidget(w)
			Chbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Chbox3 = QtGui.QHBoxLayout()
        
		for w in [ self.CLimitTag ,self.CMin_Box, self.CRange, self.CMax_Box]:
			Chbox3.addWidget(w)
			Chbox3.setAlignment(w, QtCore.Qt.AlignVCenter)

		Chbox4 = QtGui.QHBoxLayout()
        
		for w in [  self.CSliceTag, self.CMinSlice_Box, self.CRangeSlice, self.CMaxSlice_Box]:
			Chbox4.addWidget(w)
			Chbox4.setAlignment(w, QtCore.Qt.AlignVCenter)

		Cvbox1 = QtGui.QVBoxLayout()
		Cvbox1.addLayout(Chbox1)
		Cvbox1.addLayout(Chbox2)
		Cvbox1.addLayout(Chbox3)
		Cvbox1.addLayout(Chbox4)

############# GUI Lines - All horizontal and Vertical lines are declared here ###################

		self.Frame1= QtGui.QFrame()
		self.Frame1.setFrameShape(4)

		self.Frame2= QtGui.QFrame()
		self.Frame2.setFrameShape(4)

		self.Frame3= QtGui.QFrame()
		self.Frame3.setFrameShape(4)

		self.Frame4= QtGui.QFrame()
		self.Frame4.setFrameShape(4)

		self.Frame5= QtGui.QFrame()
		self.Frame5.setFrameShape(4)

		self.Frame6= QtGui.QFrame()
		self.Frame6.setFrameShape(4)

		self.Frame7= QtGui.QFrame()
		self.Frame7.setFrameShape(4)

		self.Frame8= QtGui.QFrame()
		self.Frame8.setFrameShape(4)

		self.VFrame= QtGui.QFrame()
		self.VFrame.setFrameShape(5)

		self.VFrame1= QtGui.QFrame()
		self.VFrame1.setFrameShape(5)

############# Region to declare variables related to Date ###################

		self.DLable=QtGui.QLabel('Time ', self)
		self.DLable.setFont(self.font2)

		self.DateLable=QtGui.QLabel(self.dayofplot.date().isoformat(), self)
		self.DateLable.setFont(self.font1)

		self.DateMinLable=QtGui.QLabel(self.startday.date().isoformat(), self)
		self.DateMinLable.setFont(self.font1)

		self.DateSlider= QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.DateSlider.setRange(0,len(self.timestamps)-1)
		self.DateSlider.valueChanged.connect(self.DateActivated)

		self.DateMaxLable=QtGui.QLabel(self.endday.date().isoformat(), self)
		self.DateMaxLable.setFont(self.font1)

############# GUI Box - Related to Date ###################
		
		Datehbox1 = QtGui.QHBoxLayout()
		Datehbox1.addWidget(self.DLable)
		Datehbox1.addWidget(self.DateLable)
		Datehbox1.addStretch(1)

		Datehbox2 = QtGui.QHBoxLayout()
        
		for w in [  self.DateMinLable, self.DateSlider, self.DateMaxLable]:
			Datehbox2.addWidget(w)
			Datehbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Datevbox1 = QtGui.QVBoxLayout()
		Datevbox1.addLayout(Datehbox1)
		Datevbox1.addLayout(Datehbox2)

		Datehbox3 = QtGui.QHBoxLayout()
		Datehbox3.addLayout(Datevbox1)
		Datehbox3.addWidget(self.VFrame1)	

############# Region for declaring all the Checkboxes for GUI ###################

		self.TextCheck = QtGui.QCheckBox('Show Label', self)
		self.Day5Check = QtGui.QCheckBox(str(LOOKBACK_DAYS)+' Days', self)
		self.SizeCheck = QtGui.QCheckBox('Fix Size', self)
		self.ColorCheck = QtGui.QCheckBox('Fix Color', self)
		self.MovieCheck = QtGui.QCheckBox('Smooth for Movie', self)

		Checkhbox1 = QtGui.QVBoxLayout()
		Checkhbox1.addWidget(self.TextCheck)
		Checkhbox1.addWidget(self.Day5Check)
		Checkhbox1.addWidget(self.SizeCheck)
		Checkhbox1.addWidget(self.ColorCheck)
		Checkhbox1.addWidget(self.MovieCheck)

############# Region for Declaring all the buttons in the GUI ###################

		self.UpdateButton =QtGui.QPushButton('Plot',self)
		self.UpdateButton.setToolTip('Update the plot')
		self.UpdateButton.resize(self.UpdateButton.sizeHint())
		self.UpdateButton.clicked.connect(self.PlotCanvas)

		self.SaveButton =QtGui.QPushButton('Save Plot',self)
		self.SaveButton.setToolTip('Save the plot')
		self.SaveButton.resize(self.SaveButton.sizeHint())
		self.SaveButton.clicked.connect(self.save_plot)

		self.MovieButton =QtGui.QPushButton('Movie',self)
		self.MovieButton.setToolTip('Make a movie over time')
		self.MovieButton.resize(self.MovieButton.sizeHint())
		self.MovieButton.clicked.connect(self.make_movie)

		self.AboutButton =QtGui.QPushButton('About',self)
		self.AboutButton.setToolTip('About the Visualizer')
		self.AboutButton.resize(self.AboutButton.sizeHint())
		self.AboutButton.clicked.connect(self.on_about)

		self.DataButton =QtGui.QPushButton('Change Data',self)
		self.DataButton.setToolTip('Load new Data')
		self.DataButton.resize(self.DataButton.sizeHint())
		self.DataButton.clicked.connect(self.ChangeDataset)

		self.ResetButton =QtGui.QPushButton('Reset',self)
		self.ResetButton.setToolTip('Reset Settings')
		self.ResetButton.resize(self.ResetButton.sizeHint())
		self.ResetButton.clicked.connect(self.ResetSettings)

		self.ExitButton =QtGui.QPushButton('Exit',self)
		self.ExitButton.setToolTip('Exit')
		self.ExitButton.resize(self.ExitButton.sizeHint())
		self.ExitButton.clicked.connect(QtGui.qApp.quit)

		self.SaveSettingsButton =QtGui.QPushButton('Save Settings',self)
		self.SaveSettingsButton.setToolTip('Save Settings')
		self.SaveSettingsButton.resize(self.SaveSettingsButton.sizeHint())
		self.SaveSettingsButton.clicked.connect(self.SaveSettings)

		self.LoadSettingsButton =QtGui.QPushButton('Load Settings',self)
		self.LoadSettingsButton.setToolTip('Load Settings')
		self.LoadSettingsButton.resize(self.LoadSettingsButton.sizeHint())
		self.LoadSettingsButton.clicked.connect(self.LoadSettings)

############# GUI Box - Related to Button Bar on the top ###################

		Buttonbox = QtGui.QHBoxLayout()
		Buttonbox.addLayout(Checkhbox1)
		Buttonbox.addWidget(self.UpdateButton)

		Buttonbox2 = QtGui.QHBoxLayout()
		Buttonbox2.addWidget(self.ExitButton)
		Buttonbox2.addWidget(self.AboutButton)
		Buttonbox2.addWidget(self.SaveButton)		
		Buttonbox2.addWidget(self.MovieButton)
		Buttonbox2.addWidget(self.DataButton)
		Buttonbox2.addWidget(self.ResetButton)
		Buttonbox2.addWidget(self.SaveSettingsButton)
		Buttonbox2.addWidget(self.LoadSettingsButton)
		Buttonbox2.addStretch()


############# Layout settings in the GUI - Arrangement of Everything ###################

		Vbox1 = QtGui.QVBoxLayout()
		Vbox1.addWidget(self.VisLable)
		Vbox1.addWidget(self.canvas)
		Vbox1.addWidget(self.Frame7)
		Vbox1.addLayout(Datehbox3)
		Vbox1.addItem(self.SpacerItem1)
		Vbox1.addStretch(1)

		Vbox2= QtGui.QVBoxLayout()
		Vbox2.addWidget(self.Frame1)
		Vbox2.addLayout(Xvbox1)
		Vbox2.addWidget(self.Frame2)
		Vbox2.addLayout(Yvbox1)
		Vbox2.addWidget(self.Frame3)
		Vbox2.addLayout(Zvbox1)
		Vbox2.addStretch(1)
		Vbox2.addItem(self.SpacerItem2)

		Vbox3 = QtGui.QVBoxLayout()
		Vbox3.addWidget(self.Frame4)
		Vbox3.addLayout(Svbox1)
		Vbox3.addWidget(self.Frame5)
		Vbox3.addLayout(Cvbox1)
		Vbox3.addWidget(self.Frame6)
		Vbox3.addLayout(Buttonbox)
		Vbox3.addStretch(1)
		Vbox3.addItem(self.SpacerItem3)

		HBox1 = QtGui.QHBoxLayout()
		HBox1.addLayout(Vbox2)
		HBox1.addWidget(self.VFrame)
		HBox1.addLayout(Vbox3)

		Vbox4 = QtGui.QVBoxLayout()
		Vbox4.addStretch(1)
		Vbox4.addWidget(self.FactorLable)
		Vbox4.addLayout(HBox1)
		Vbox4.addStretch(1)

		HBox2= QtGui.QHBoxLayout()
		HBox2.addLayout(Vbox1)
		HBox2.addLayout(Vbox4)
		HBox2.addItem(self.SpacerItem4)
		HBox2.addStretch(1)

		FinalBox = QtGui.QVBoxLayout()
		FinalBox.addLayout(Buttonbox2)
		FinalBox.addLayout(HBox2)
		FinalBox.addStretch(1)

		self.setWindowTitle('QuantViz')
		self.setWindowIcon(QtGui.QIcon('V.png'))
		self.main_frame.setLayout(FinalBox)
		self.setCentralWidget(self.main_frame)
		self.statusBar().showMessage('Ready')

		'''
		All functions of the class start here.
		'''

############### Function to Load Data from the Dataset ####################

	def LoadData(self):
		fname = str(QtGui.QFileDialog.getExistingDirectory(None, 'Data Directory', os.environ['QS']+'/Tools/Visualizer/Data/', options=QtGui.QFileDialog.DontUseNativeDialog))
		fname= fname+'/'
		(self.PandasObject, self.featureslist, self.symbols, self.timestamps, self.dMinFeat, self.dMaxFeat, self.startday, self.endday) = AD.GetData(fname)

############### Function to Reset all the variables ####################

	def Reset(self):
		self.scatterpts=[]
		self.textpts=[]
		self.scatterpts2=[]
		self.textpts2=[]
		self.Xfeature=self.featureslist[0]
		self.Yfeature=self.featureslist[0]
		self.Zfeature=self.featureslist[0]
		self.Sfeature=self.featureslist[0]
		self.Cfeature=self.featureslist[0]
		self.XMin=0.0
		self.XMax=1.0
		self.XLow=self.XMin
		self.XHigh=self.XMax
		self.XLowSlice=self.XMin
		self.XHighSlice=self.XMax
		self.YMin=0.0
		self.YMax=1.0
		self.YLow=self.YMin
		self.YHigh=self.YMax
		self.YLowSlice=self.YMin
		self.YHighSlice=self.YMax
		self.ZMin=0.0
		self.ZMax=1.0
		self.ZLow=self.ZMin
		self.ZHigh=self.ZMax
		self.ZLowSlice=self.ZMin
		self.ZHighSlice=self.ZMax
		self.SMin=0.0
		self.SMax=1.0
		self.SLow=self.SMin
		self.SHigh=self.SMax
		self.SLowSlice=self.SMin
		self.SHighSlice=self.SMax
		self.CMin=0.0
		self.CMax=1.0
		self.CLow=self.CMin
		self.CHigh=self.CMax
		self.CLowSlice=self.CMin
		self.CHighSlice=self.CMax
		self.dayofplot=self.timestamps[0]

############### Function to Reset all the GUI sliders and Labels ####################

	def ResetFunc(self):
		self.FeatureComboBox(self.XCombo)
		self.XInitRangeSlider(self.XRange)		
		self.XInitRangeSliderSlice(self.XRangeSlice)
		self.XMaxLable.setText(str(self.XMax))
		self.XMinLable.setText(str(self.XMin))
		self.XMin_Box.setText(str(self.XLow))
		self.XMax_Box.setText(str(self.XHigh))
		self.XMinSlice_Box.setText(str(self.XLowSlice))	
		self.XMaxSlice_Box.setText(str(self.XHighSlice))

		self.FeatureComboBox(self.YCombo)
		self.YInitRangeSlider(self.YRange)
		self.YInitRangeSliderSlice(self.YRangeSlice)
		self.YMaxLable.setText(str(self.YMax))
		self.YMinLable.setText(str(self.YMin))
		self.YMin_Box.setText(str(self.YLow))
		self.YMax_Box.setText(str(self.YHigh))
		self.YMinSlice_Box.setText(str(self.YLowSlice))	
		self.YMaxSlice_Box.setText(str(self.YHighSlice))

		self.FeatureComboBox(self.ZCombo)
		self.ZInitRangeSlider(self.ZRange)
		self.ZInitRangeSliderSlice(self.ZRangeSlice)
		self.ZMaxLable.setText(str(self.ZMax))
		self.ZMinLable.setText(str(self.ZMin))
		self.ZMin_Box.setText(str(self.ZLow))
		self.ZMax_Box.setText(str(self.ZHigh))
		self.ZMinSlice_Box.setText(str(self.ZLowSlice))	
		self.ZMaxSlice_Box.setText(str(self.ZHighSlice))

		self.FeatureComboBox(self.SizeCombo)
		self.SInitRangeSlider(self.SRange)
		self.SInitRangeSliderSlice(self.SRangeSlice)
		self.SMaxLable.setText(str(self.SMax))
		self.SMinLable.setText(str(self.SMin))
		self.SMin_Box.setText(str(self.SLow))
		self.SMax_Box.setText(str(self.SHigh))
		self.SMinSlice_Box.setText(str(self.SLowSlice))	
		self.SMaxSlice_Box.setText(str(self.SHighSlice))

		self.FeatureComboBox(self.ColorCombo)
		self.CInitRangeSlider(self.CRange)
		self.CInitRangeSliderSlice(self.CRangeSlice)
		self.CMaxLable.setText(str(self.CMax))
		self.CMinLable.setText(str(self.CMin))
		self.CMin_Box.setText(str(self.CLow))
		self.CMax_Box.setText(str(self.CHigh))
		self.CMinSlice_Box.setText(str(self.CLowSlice))	
		self.CMaxSlice_Box.setText(str(self.CHighSlice))

		self.DateLable.setText(self.dayofplot.date().isoformat())
		self.DateSlider.setSliderPosition(self.timestamps.index(self.dayofplot))

############### Function to Load Data a new Dataset ####################

	def ChangeDataset(self):
		self.ClearCanvas()
		self.LoadData()
		self.Reset()
		self.ResetFunc()
		self.statusBar().showMessage('Loading data set complete')

############### Function to Reset Dataset ####################

	def ResetSettings(self):
		self.ClearCanvas()
		self.Reset()
		self.ResetFunc()
		self.statusBar().showMessage('Reset Complete')

############### Function to Save current Settings ####################

	def SaveSettings(self):
		fname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save file', os.environ['QS']+'/Tools/Visualizer/Settings/settings.pkl', options=QtGui.QFileDialog.DontUseNativeDialog))
		if fname=='':
			return
		SettingArray=(self.Xfeature,self.Yfeature,self.Zfeature,self.Sfeature,self.Cfeature, self.XMin,self.XMax,self.XLow,self.XHigh,self.XLowSlice,self.XHighSlice,self.YMin,self.YMax,self.YLow,self.YHigh, self.YLowSlice,self.YHighSlice,self.ZMin,self.ZMax,self.ZLow,self.ZHigh,self.ZLowSlice,self.ZHighSlice,self.SMin, self.SMax,self.SLow,self.SHigh,self.SLowSlice,self.SHighSlice,self.CMin,self.CMax,self.CLow,self.CHigh, self.CLowSlice,self.CHighSlice,self.dayofplot)
		
		pickle.dump(SettingArray,open(fname, 'wb' ),-1)
		self.statusBar().showMessage('Saved Settings')

############### Function to Load Settings previously stored ####################

	def LoadSettings(self):
		fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', os.environ['QS']+'/Tools/Visualizer/Settings/', options=QtGui.QFileDialog.DontUseNativeDialog))
		if fname=='':
			return
		(self.Xfeature,self.Yfeature,self.Zfeature,self.Sfeature,self.Cfeature,self.XMin, self.XMax,self.XLow,self.XHigh,self.XLowSlice,self.XHighSlice,self.YMin,self.YMax,self.YLow,self.YHigh,self.YLowSlice,self.YHighSlice, self.ZMin,self.ZMax,self.ZLow,self.ZHigh,self.ZLowSlice,self.ZHighSlice,self.SMin,self.SMax,self.SLow,self.SHigh,self.SLowSlice, self.SHighSlice,self.CMin,self.CMax,self.CLow,self.CHigh,self.CLowSlice,self.CHighSlice,self.dayofplot)=pickle.load(open( fname, 'rb' ))

		self.XCombo.setCurrentIndex(self.XCombo.findText(self.Xfeature))
		self.XMaxLable.setText(str(self.XMax))
		self.XMinLable.setText(str(self.XMin))
		self.XMin_Box.setText(str(self.XLow))
		self.XMax_Box.setText(str(self.XHigh))
		self.XMinSlice_Box.setText(str(self.XLowSlice))	
		self.XMaxSlice_Box.setText(str(self.XHighSlice))

		self.YCombo.setCurrentIndex(self.YCombo.findText(self.Yfeature))
		self.YMaxLable.setText(str(self.YMax))
		self.YMinLable.setText(str(self.YMin))
		self.YMin_Box.setText(str(self.YLow))
		self.YMax_Box.setText(str(self.YHigh))
		self.YMinSlice_Box.setText(str(self.YLowSlice))	
		self.YMaxSlice_Box.setText(str(self.YHighSlice))

		self.ZCombo.setCurrentIndex(self.ZCombo.findText(self.Zfeature))
		self.ZMaxLable.setText(str(self.ZMax))
		self.ZMinLable.setText(str(self.ZMin))
		self.ZMin_Box.setText(str(self.ZLow))
		self.ZMax_Box.setText(str(self.ZHigh))
		self.ZMinSlice_Box.setText(str(self.ZLowSlice))	
		self.ZMaxSlice_Box.setText(str(self.ZHighSlice))

		self.SizeCombo.setCurrentIndex(self.SizeCombo.findText(self.Sfeature))
		self.SMaxLable.setText(str(self.SMax))
		self.SMinLable.setText(str(self.SMin))
		self.SMin_Box.setText(str(self.SLow))
		self.SMax_Box.setText(str(self.SHigh))
		self.SMinSlice_Box.setText(str(self.SLowSlice))	
		self.SMaxSlice_Box.setText(str(self.SHighSlice))

		self.ColorCombo.setCurrentIndex(self.ColorCombo.findText(self.Cfeature))
		self.CMaxLable.setText(str(self.CMax))
		self.CMinLable.setText(str(self.CMin))
		self.CMin_Box.setText(str(self.CLow))
		self.CMax_Box.setText(str(self.CHigh))
		self.CMinSlice_Box.setText(str(self.CLowSlice))	
		self.CMaxSlice_Box.setText(str(self.CHighSlice))

		self.DateLable.setText(self.dayofplot.date().isoformat())
		self.DateSlider.setSliderPosition(self.timestamps.index(self.dayofplot))
		self.ClearCanvas()
		self.statusBar().showMessage('Loaded Settings')

############### Function for add Features to the Boxes ####################

	def FeatureComboBox(self, combo):
		combo.clear()
		for feat in self.featureslist:
			combo.addItem(feat)
        
############### Function to Check validity of the input into the textbox of sliders ####################

	def correctInput(self, valueEntered, Min, Max, boundcase):
		low = math.floor(((valueEntered- Min)*SLIDER_RANGE)/(Max-Min))
		high= low+1
		lowval = (low*(Max-Min))/SLIDER_RANGE+Min
		highval = (high*(Max-Min))/SLIDER_RANGE+Min
		stepsize = highval - lowval
		if boundcase=='f':
			if (highval-valueEntered)<0.2*stepsize: return high
			else: return low
		if boundcase=='c':
			if (valueEntered-lowval)<0.2*stepsize: return low
			else: return high
		else: return low

############### Region for Functions associated with X Axis ####################

	def XComboActivated(self,text):
		self.Xfeature=text
		self.XMax=self.dMaxFeat[str(self.Xfeature)]
		self.XMin=self.dMinFeat[str(self.Xfeature)]
		self.XMinLable.setText(str(round(self.XMin,1)))
		self.XMaxLable.setText(str(round(self.XMax,1)))
		self.XChangeValues(self.XRange.low(), self.XRange.high())
		self.XChangeValuesSlice(self.XRangeSlice.low(), self.XRangeSlice.high())

	def XChangeValues(self, low, high):
		self.XLow=(low*(self.XMax-self.XMin))/SLIDER_RANGE+self.XMin
		self.XHigh=(high*(self.XMax-self.XMin))/SLIDER_RANGE+self.XMin
		self.XMin_Box.setText(str(round(self.XLow,2)))
		self.XMax_Box.setText(str(round(self.XHigh,2)))

	def XChangeValuesSlice(self, low, high):
		self.XLowSlice=(low*(self.XMax-self.XMin))/SLIDER_RANGE+self.XMin
		self.XHighSlice=(high*(self.XMax-self.XMin))/SLIDER_RANGE+self.XMin	
		self.XMinSlice_Box.setText(str(self.XLowSlice))
		self.XMaxSlice_Box.setText(str(self.XHighSlice))
		
	def XInitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.XChangeValues)

	def XInitRangeSliderSlice(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.XChangeValuesSlice)

	def XMin_BoxInput(self):
		valueEntered=float(self.XMin_Box.text())
		if valueEntered>self.XHigh or valueEntered<self.XMin:
			self.XMin_Box.setText(str(self.XLow))
			return
		slide = self.correctInput(valueEntered, self.XMin, self.XMax, 'f')
		self.XRange.setLow(slide)
		self.XChangeValues(slide, self.XRange.high())

	def XMinSlice_BoxInput(self):
		valueEntered=float(self.XMinSlice_Box.text())
		if valueEntered>self.XHighSlice or valueEntered<self.XMin:
			self.XMinSlice_Box.setText(str(self.XLowSlice))
			return
		slide = self.correctInput(valueEntered, self.XMin, self.XMax, 'f')
		self.XRangeSlice.setLow(slide)
		self.XChangeValuesSlice(slide, self.XRangeSlice.high())

	def XMax_BoxInput(self):
		valueEntered=float(self.XMax_Box.text())
		if valueEntered<self.XLow or valueEntered>self.XMax:
			self.XMax_Box.setText(str(self.XHigh))
			return
		slide = self.correctInput(valueEntered, self.XMin, self.XMax, 'c')
		self.XRange.setHigh(slide)
		self.XChangeValues(self.XRange.low(),slide)

	def XMaxSlice_BoxInput(self):
		valueEntered=float(self.XMaxSlice_Box.text())
		if valueEntered<self.XLowSlice or valueEntered>self.XMax:
			self.XMaxSlice_Box.setText(str(self.XHighSlice))
			return
		slide = self.correctInput(valueEntered, self.XMin, self.XMax, 'c')
		self.XRangeSlice.setHigh(slide)
		self.XChangeValuesSlice(self.XRangeSlice.low(), slide)

############### Region for Functions associated with Y Axis ####################

	def YComboActivated(self,text):
		self.Yfeature=text
		self.YMax=self.dMaxFeat[str(self.Yfeature)]
		self.YMin=self.dMinFeat[str(self.Yfeature)]
		self.YMinLable.setText(str(round(self.YMin,1)))
		self.YMaxLable.setText(str(round(self.YMax,1)))
		self.YChangeValues(self.YRange.low(), self.YRange.high())
		self.YChangeValuesSlice(self.YRangeSlice.low(), self.YRangeSlice.high())

	def YChangeValues(self, low, high):
		self.YLow=(low*(self.YMax-self.YMin))/SLIDER_RANGE+self.YMin
		self.YHigh=(high*(self.YMax-self.YMin))/SLIDER_RANGE+self.YMin
		self.YMin_Box.setText(str(round(self.YLow,2)))
		self.YMax_Box.setText(str(round(self.YHigh,2)))	

	def YChangeValuesSlice(self, low, high):
		self.YLowSlice=(low*(self.YMax-self.YMin))/SLIDER_RANGE+self.YMin
		self.YHighSlice=(high*(self.YMax-self.YMin))/SLIDER_RANGE+self.YMin		
		self.YMinSlice_Box.setText(str(self.YLowSlice))
		self.YMaxSlice_Box.setText(str(self.YHighSlice))

	def YInitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.YChangeValues)

	def YInitRangeSliderSlice(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.YChangeValuesSlice)

	def YMin_BoxInput(self):
		valueEntered=float(self.YMin_Box.text())
		if valueEntered>self.YHigh or valueEntered<self.YMin:
			self.YMin_Box.setText(str(self.YLow))
			return
		slide = self.correctInput(valueEntered, self.YMin, self.YMax, 'f')
		self.YRange.setLow(slide)
		self.YChangeValues(slide, self.YRange.high())

	def YMinSlice_BoxInput(self):
		valueEntered=float(self.YMinSlice_Box.text())
		if valueEntered>self.YHighSlice or valueEntered<self.YMin:
			self.YMinSlice_Box.setText(str(self.YLowSlice))
			return
		slide = self.correctInput(valueEntered, self.YMin, self.YMax, 'f')
		self.YRangeSlice.setLow(slide)
		self.YChangeValuesSlice(slide, self.YRangeSlice.high())

	def YMax_BoxInput(self):
		valueEntered=float(self.YMax_Box.text())
		if valueEntered<self.YLow or valueEntered>self.YMax:
			self.YMax_Box.setText(str(self.YHigh))
			return
		slide = self.correctInput(valueEntered, self.YMin, self.YMax, 'c')
		self.YRange.setHigh(slide)
		self.YChangeValues(self.YRange.low(),slide)

	def YMaxSlice_BoxInput(self):
		valueEntered=float(self.YMaxSlice_Box.text())
		if valueEntered<self.YLowSlice or valueEntered>self.YMax:
			self.YMaxSlice_Box.setText(str(self.YHighSlice))
			return
		slide = self.correctInput(valueEntered, self.YMin, self.YMax, 'c')
		self.YRangeSlice.setHigh(slide)
		self.YChangeValuesSlice(self.YRangeSlice.low(), slide)

############### Region for Functions associated with Z Axis ####################

	def ZComboActivated(self,text):
		self.Zfeature=text
		self.ZMax=self.dMaxFeat[str(self.Zfeature)]
		self.ZMin=self.dMinFeat[str(self.Zfeature)]
		self.ZMinLable.setText(str(round(self.ZMin,1)))
		self.ZMaxLable.setText(str(round(self.ZMax,1)))
		self.ZChangeValues(self.ZRange.low(), self.ZRange.high())
		self.ZChangeValuesSlice(self.ZRangeSlice.low(), self.ZRangeSlice.high())

	def ZChangeValues(self, low, high):
		self.ZLow=(low*(self.ZMax-self.ZMin))/SLIDER_RANGE+self.ZMin
		self.ZHigh=(high*(self.ZMax-self.ZMin))/SLIDER_RANGE+self.ZMin	
		self.ZMin_Box.setText(str(round(self.ZLow,2)))
		self.ZMax_Box.setText(str(round(self.ZHigh,2)))		

	def ZChangeValuesSlice(self, low, high):
		self.ZLowSlice=(low*(self.ZMax-self.ZMin))/SLIDER_RANGE+self.ZMin
		self.ZHighSlice=(high*(self.ZMax-self.ZMin))/SLIDER_RANGE+self.ZMin		
		self.ZMinSlice_Box.setText(str(self.ZLowSlice))
		self.ZMaxSlice_Box.setText(str(self.ZHighSlice))

	def ZInitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.ZChangeValues)

	def ZInitRangeSliderSlice(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.ZChangeValuesSlice)

	def ZMin_BoxInput(self):
		valueEntered=float(self.ZMin_Box.text())
		if valueEntered>self.ZHigh or valueEntered<self.ZMin:
			self.ZMin_Box.setText(str(self.ZLow))
			return
		slide = self.correctInput(valueEntered, self.ZMin, self.ZMax, 'f')
		self.ZRange.setLow(slide)
		self.ZChangeValues(slide, self.ZRange.high())

	def ZMinSlice_BoxInput(self):
		valueEntered=float(self.ZMinSlice_Box.text())
		if valueEntered>self.ZHighSlice or valueEntered<self.ZMin:
			self.ZMinSlice_Box.setText(str(self.ZLowSlice))
			return
		slide = self.correctInput(valueEntered, self.ZMin, self.ZMax, 'f')
		self.ZRangeSlice.setLow(slide)
		self.ZChangeValuesSlice(slide, self.ZRangeSlice.high())

	def ZMax_BoxInput(self):
		valueEntered=float(self.ZMax_Box.text())
		if valueEntered<self.ZLow or valueEntered>self.ZMax:
			self.ZMax_Box.setText(str(self.ZHigh))
			return
		slide = self.correctInput(valueEntered, self.ZMin, self.ZMax, 'c')
		self.ZRange.setHigh(slide)
		self.ZChangeValues(self.ZRange.low(),slide)

	def ZMaxSlice_BoxInput(self):
		valueEntered=float(self.ZMaxSlice_Box.text())
		if valueEntered<self.ZLowSlice or valueEntered>self.ZMax:
			self.ZMaxSlice_Box.setText(str(self.ZHighSlice))
			return
		slide = self.correctInput(valueEntered, self.ZMin, self.ZMax, 'c')
		self.ZRangeSlice.setHigh(slide)
		self.ZChangeValuesSlice(self.ZRangeSlice.low(), slide)

############### Region for Functions associated with Size ####################

	def SComboActivated(self,text):
		self.Sfeature=text
		self.SMax=self.dMaxFeat[str(self.Sfeature)]
		self.SMin=self.dMinFeat[str(self.Sfeature)]
		self.SMinLable.setText(str(round(self.SMin,1)))
		self.SMaxLable.setText(str(round(self.SMax,1)))
		self.SChangeValues(self.SRange.low(), self.SRange.high())
		self.SChangeValuesSlice(self.SRangeSlice.low(), self.SRangeSlice.high())

	def SChangeValues(self, low, high):
		self.SLow=(low*(self.SMax-self.SMin))/SLIDER_RANGE+self.SMin
		self.SHigh=(high*(self.SMax-self.SMin))/SLIDER_RANGE+self.SMin	
		self.SMin_Box.setText(str(round(self.SLow,2)))
		self.SMax_Box.setText(str(round(self.SHigh,2)))			

	def SInitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.SChangeValues)

	def SMin_BoxInput(self):
		valueEntered=float(self.SMin_Box.text())
		if valueEntered>self.SHigh or valueEntered<self.SMin:
			self.SMin_Box.setText(str(self.SLow))
			return
		slide = self.correctInput(valueEntered, self.SMin, self.SMax, 'f')
		self.SRange.setLow(slide)
		self.SChangeValues(slide, self.SRange.high())

	def SMax_BoxInput(self):
		valueEntered=float(self.SMax_Box.text())
		if valueEntered<self.SLow or valueEntered>self.SMax:
			self.SMax_Box.setText(str(self.SHigh))
			return
		slide = self.correctInput(valueEntered, self.SMin, self.SMax, 'c')
		self.SRange.setHigh(slide)
		self.SChangeValues(self.SRange.low(),slide)

	def SChangeValuesSlice(self, low, high):
		self.SLowSlice=(low*(self.SMax-self.SMin))/SLIDER_RANGE+self.SMin
		self.SHighSlice=(high*(self.SMax-self.SMin))/SLIDER_RANGE+self.SMin	
		self.SMinSlice_Box.setText(str(self.SLowSlice))
		self.SMaxSlice_Box.setText(str(self.SHighSlice))

	def SInitRangeSliderSlice(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.SChangeValuesSlice)

	def SMinSlice_BoxInput(self):
		valueEntered=float(self.SMinSlice_Box.text())
		if valueEntered>self.SHighSlice or valueEntered<self.SMin:
			self.SMinSlice_Box.setText(str(self.SLowSlice))
			return
		slide = self.correctInput(valueEntered, self.SMin, self.SMax, 'f')
		self.SRangeSlice.setLow(slide)
		self.SChangeValuesSlice(slide, self.SRangeSlice.high())

	def SMaxSlice_BoxInput(self):
		valueEntered=float(self.SMaxSlice_Box.text())
		if valueEntered<self.SLowSlice or valueEntered>self.SMax:
			self.SMaxSlice_Box.setText(str(self.SHighSlice))
			return
		slide = self.correctInput(valueEntered, self.SMin, self.SMax, 'c')
		self.SRangeSlice.setHigh(slide)
		self.SChangeValuesSlice(self.SRangeSlice.low(), slide)

############### Region for Functions associated with Color ####################

	def CComboActivated(self,text):
		self.Cfeature=text
		self.CMax=self.dMaxFeat[str(self.Cfeature)]
		self.CMin=self.dMinFeat[str(self.Cfeature)]
		self.CMinLable.setText(str(round(self.CMin,1)))
		self.CMaxLable.setText(str(round(self.CMax,1)))
		self.CChangeValues(self.CRange.low(), self.CRange.high())
		self.CChangeValuesSlice(self.CRangeSlice.low(), self.CRangeSlice.high())

	def CChangeValues(self, low, high):
		self.CLow=(low*(self.CMax-self.CMin))/SLIDER_RANGE+self.CMin
		self.CHigh=(high*(self.CMax-self.CMin))/SLIDER_RANGE+self.CMin	
		self.CMin_Box.setText(str(round(self.CLow,2)))
		self.CMax_Box.setText(str(round(self.CHigh,2)))				

	def CInitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.CChangeValues)

	def CMin_BoxInput(self):
		valueEntered=float(self.CMin_Box.text())
		if valueEntered>self.CHigh or valueEntered<self.CMin:
			self.CMin_Box.setText(str(self.CLow))
			return
		slide = self.correctInput(valueEntered, self.CMin, self.CMax, 'f')
		self.CRange.setLow(slide)
		self.CChangeValues(slide, self.CRange.high())

	def CMax_BoxInput(self):
		valueEntered=float(self.CMax_Box.text())
		if valueEntered<self.CLow or valueEntered>self.CMax:
			self.CMax_Box.setText(str(self.CHigh))
			return
		slide = self.correctInput(valueEntered, self.CMin, self.CMax, 'c')
		self.CRange.setHigh(slide)
		self.CChangeValues(self.CRange.low(),slide)

	def CChangeValuesSlice(self, low, high):
		self.CLowSlice=(low*(self.CMax-self.CMin))/SLIDER_RANGE+self.CMin
		self.CHighSlice=(high*(self.CMax-self.CMin))/SLIDER_RANGE+self.CMin	
		self.CMinSlice_Box.setText(str(self.CLowSlice))
		self.CMaxSlice_Box.setText(str(self.CHighSlice))

	def CInitRangeSliderSlice(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(SLIDER_RANGE)
		slider.setLow(0)
		slider.setHigh(SLIDER_RANGE)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.CChangeValuesSlice)

	def CMinSlice_BoxInput(self):
		valueEntered=float(self.CMinSlice_Box.text())
		if valueEntered>self.CHighSlice or valueEntered<self.CMin:
			self.CMinSlice_Box.setText(str(self.CLowSlice))
			return
		slide = self.correctInput(valueEntered, self.CMin, self.CMax, 'f')
		self.CRangeSlice.setLow(slide)
		self.CChangeValuesSlice(slide, self.CRangeSlice.high())

	def CMaxSlice_BoxInput(self):
		valueEntered=float(self.CMaxSlice_Box.text())
		if valueEntered<self.CLowSlice or valueEntered>self.CMax:
			self.CMaxSlice_Box.setText(str(self.CHighSlice))
			return
		slide = self.correctInput(valueEntered, self.CMin, self.CMax, 'c')
		self.CRangeSlice.setHigh(slide)
		self.CChangeValuesSlice(self.CRangeSlice.low(), slide)

############### Function which is called when the date slider is changed ####################

	def DateActivated(self, index):
		self.dayofplot=self.timestamps[index]
		dateval=self.timestamps[index]
		dateval=dateval.date().isoformat()
		self.DateLable.setText(dateval)
		self.DateLable.adjustSize() 

############### Region for Plotting related fuctions ####################

	# Checkes if the value lies between the min and max, otherwise returns a NAN
	def inrange(self, x, minx, maxx):
		if x>=minx and x<=maxx: return x
		else: return np.NAN
	
	# Returns a value to be used in size array based on the scale and slice values
	def inrangeS(self, s, low, lowslice, high, highslice ,absmin, absmax):
		if s<=low: s=low
		elif s>=high: s=high
	
		if s<=lowslice: return 0
		elif s>=highslice: return 0
		else: return (199*((s-absmin)/(absmax-absmin))+10)

	# Returns a value to be used in color array based on the scale and slice values
	def inrangeC(self, c, low, lowslice, high, highslice ,absmin, absmax):
		if c<=low: c=low
		elif c>=high: c=high

		if c<=lowslice: return np.NAN
		elif c>=highslice: return np.NAN
		else: return (501*((c-absmin)/(absmax-absmin))+10)

	#Remove points from the plot - Clear the plot - No actual clear function yet in matplotlib
	def clean(self):
		if self.scatterpts:
			for pt in self.scatterpts :
				pt.remove()
		self.scatterpts = []
		if self.textpts:
			for pt in self.textpts :
				pt.remove()
		self.textpts = []

	# Reading data from the pandas object 
	def readdata(self, day):
		xs=self.PandasObject[str(self.Xfeature)].xs(day)
		ys=self.PandasObject[str(self.Yfeature)].xs(day)
		zs=self.PandasObject[str(self.Zfeature)].xs(day)		
		size=self.PandasObject[str(self.Sfeature)].xs(day)
		color=self.PandasObject[str(self.Cfeature)].xs(day)
		return (xs,ys,zs,size,color)

	# 5 Day Average for smoothning in the movie
	def avg(self,x1,x2,x3,x4,x5):
		return (x1+x2+x3+x4+x5)/5.0

	# Plotting Points - Just draws points - has a lot of work around techniques for bugs in matplotlib
	def PlotPoints(self, day):
		index = self.timestamps.index(day)
		# Check whether smoothning is required or not
		if self.MovieCheck.isChecked() and index<(len(self.timestamps)-2) and index>=2:
			(x1,y1,z1,s1,c1)= self.readdata(self.timestamps[index-2])
			(x2,y2,z2,s2,c2)= self.readdata(self.timestamps[index-1])
			(x3,y3,z3,s3,c3)= self.readdata(self.timestamps[index])
			(x4,y4,z4,s4,c4)= self.readdata(self.timestamps[index+1])
			(x5,y5,z5,s5,c5)= self.readdata(self.timestamps[index+2])
						
			xs= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(x1,x2,x3,x4,x5)]
			ys= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(y1,y2,y3,y4,y5)]
			zs= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(z1,z2,z3,z4,z5)]
			size= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(s1,s2,s3,s4,s5)]
			color= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(c1,c2,c3,c4,c5)]	

		else:
			(xs,ys,zs,size,color) = self.readdata(day)
		
		# Whether the points lie between size and scale values
		xs1 = [self.inrange(x, max(self.XLow, self.XLowSlice), min(self.XHigh, self.XHighSlice)) for x in xs]
		ys1 = [self.inrange(y, max(self.YLow, self.YLowSlice), min(self.YHigh, self.YHighSlice)) for y in ys]
		zs1 = [self.inrange(z, max(self.ZLow, self.ZLowSlice), min(self.ZHigh, self.ZHighSlice)) for z in zs]

		# Check if size is fixed or not
		if self.SizeCheck.isChecked():
			size1 =20
		else: size1 = [self.inrangeS(s, self.SLow, self.SLowSlice, self.SHigh, self.SHighSlice, self.SMin, self.SMax) for s in size]

		# Check if color is fixed or not
		if self.ColorCheck.isChecked():
			color1 = 'g'
		else: color1 = [self.inrangeC(c, self.CLow, self.CLowSlice, self.CHigh, self.CHighSlice, self.CMin, self.CMax) for c in color]

		# Scatter Plot
		pt=self.ax.scatter(xs1,ys1,zs1,marker='o', alpha=1, c=color1, s=size1, edgecolor='none')
		self.scatterpts.append(pt)
		
		# Check if labels need to be put in
		if self.TextCheck.isChecked():
			for x,y,z,l in zip(xs1,ys1,zs1,self.symbols):
				pt=self.ax.text(x,y,z,l)
				self.textpts.append(pt)
		self.datetext.set_text('Date : ' + day.date().isoformat())

	#Function to plot the figure, use the above and set limits and lables. To avoid redoing everything in the 5 day case
	def PlotFigure(self, day):
		self.PlotPoints(day)
		if self.Day5Check.isChecked():
			index = self.timestamps.index(day)
			for i in range(LOOKBACK_DAYS-1):
				if (index-i-1)>=0:
					self.PlotPoints(self.timestamps[index-i-1])

		self.ax.set_xlim(self.XLow, self.XHigh)
		self.ax.set_ylim(self.YLow, self.YHigh)
		self.ax.set_zlim(self.ZLow, self.ZHigh)		
		self.ax.set_xlabel(self.Xfeature)
		self.ax.set_ylabel(self.Yfeature)
		self.ax.set_zlabel(self.Zfeature)

############### Function to clear the canvas ####################

	def ClearCanvas(self):
		self.clean()
		xs=self.PandasObject[str(self.Xfeature)].xs(self.dayofplot)
		pt=self.ax.scatter(xs,xs,xs,marker='o', alpha=0, c='g', s=0)
		self.scatterpts.append(pt)
		self.ax.set_xlim(0, 1)
		self.ax.set_ylim(0, 1)
		self.ax.set_zlim(0, 1)		
		self.ax.set_xlabel(' ')
		self.ax.set_ylabel(' ')
		self.ax.set_zlabel(' ')
		self.canvas.draw()
		self.clean()
		self.statusBar().showMessage('Cleared the Plot')
		
############### Function called when the plot button is pressed ####################

	def PlotCanvas(self):
		self.clean()
		self.PlotFigure(self.dayofplot)
		self.canvas.draw()
		self.statusBar().showMessage('Update the Plot')

############### Functions to plot on the canvas2 - High resolution images for saved image and movie #############33

	#Remove points from the plot - Clear the plot - No actual clear function yet in matplotlib
	def clean2(self):
		if self.scatterpts2:
			for pt in self.scatterpts2 :
				pt.remove()
		self.scatterpts2 = []
		if self.textpts2:
			for pt in self.textpts2 :
				pt.remove()
		self.textpts2 = []

	# Plotting Points - Just draws points - has a lot of work around techniques for bugs in matplotlib
	def PlotPoints2(self, day):
		index = self.timestamps.index(day)
		# Check whether smoothning is required or not
		if self.MovieCheck.isChecked() and index<(len(self.timestamps)-2) and index>=2:
			(x1,y1,z1,s1,c1)= self.readdata(self.timestamps[index-2])
			(x2,y2,z2,s2,c2)= self.readdata(self.timestamps[index-1])
			(x3,y3,z3,s3,c3)= self.readdata(self.timestamps[index])
			(x4,y4,z4,s4,c4)= self.readdata(self.timestamps[index+1])
			(x5,y5,z5,s5,c5)= self.readdata(self.timestamps[index+2])
						
			xs= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(x1,x2,x3,x4,x5)]
			ys= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(y1,y2,y3,y4,y5)]
			zs= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(z1,z2,z3,z4,z5)]
			size= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(s1,s2,s3,s4,s5)]
			color= [ self.avg(a1,a2,a3,a4,a5) for a1,a2,a3,a4,a5 in zip(c1,c2,c3,c4,c5)]	

		else:
			(xs,ys,zs,size,color) = self.readdata(day)
		
		# Whether the points lie between size and scale values
		xs1 = [self.inrange(x, max(self.XLow, self.XLowSlice), min(self.XHigh, self.XHighSlice)) for x in xs]
		ys1 = [self.inrange(y, max(self.YLow, self.YLowSlice), min(self.YHigh, self.YHighSlice)) for y in ys]
		zs1 = [self.inrange(z, max(self.ZLow, self.ZLowSlice), min(self.ZHigh, self.ZHighSlice)) for z in zs]

		# Check if size is fixed or not
		if self.SizeCheck.isChecked():
			size1 =20
		else: size1 = [self.inrangeS(s, self.SLow, self.SLowSlice, self.SHigh, self.SHighSlice, self.SMin, self.SMax) for s in size]

		# Check if color is fixed or not
		if self.ColorCheck.isChecked():
			color1 = 'g'
		else: color1 = [self.inrangeC(c, self.CLow, self.CLowSlice, self.CHigh, self.CHighSlice, self.CMin, self.CMax) for c in color]

		# Scatter Plot
		pt=self.ax2.scatter(xs1,ys1,zs1,marker='o', alpha=1, c=color1, s=size1, edgecolor='none')
		self.scatterpts2.append(pt)
		
		# Check if labels need to be put in
		if self.TextCheck.isChecked():
			for x,y,z,l in zip(xs1,ys1,zs1,self.symbols):
				pt=self.ax2.text(x,y,z,l)
				self.textpts2.append(pt)
		self.datetext2.set_text('Date : ' + day.date().isoformat())

	#Function to plot the figure, use the above and set limits and lables. To avoid redoing everything in the 5 day case
	def PlotFigure2(self, day):
		self.PlotPoints2(day)
		if self.Day5Check.isChecked():
			index = self.timestamps.index(day)
			for i in range(LOOKBACK_DAYS-1):
				if (index-i-1)>=0:
					self.PlotPoints2(self.timestamps[index-i-1])

		self.ax2.set_xlim(self.XLow, self.XHigh)
		self.ax2.set_ylim(self.YLow, self.YHigh)
		self.ax2.set_zlim(self.ZLow, self.ZHigh)		
		self.ax2.set_xlabel(self.Xfeature)
		self.ax2.set_ylabel(self.Yfeature)
		self.ax2.set_zlabel(self.Zfeature)

############### Function to save the current plot ####################

	# Redraw of the Image is to account for the bug in matplotlib which loses the color -> If you have made the bug fix, No need to redraw

	def save_plot(self):
		fname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save file', os.environ['QS']+'/Tools/Visualizer/untitled.png', 'Images (*.png *.xpm *.jpg)', options=QtGui.QFileDialog.DontUseNativeDialog))
		if fname=='':
			return
		self.clean2()
		self.PlotFigure2(self.dayofplot)
		self.canvas2.print_png(fname, dpi=self.dpi*2, facecolor='gray', edgecolor='gray')
		self.statusBar().showMessage('Saved the File')

############### Function to create the movie over time with current settings ####################

	def make_movie(self):
		folderpath = os.environ['QS']+'/Tools/Visualizer/Movie/'
		text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter name of movie:')
		if ok:
			if len(text)<1:
				print "Movie name Invalid"
				return 
			folderpath= folderpath + str(text)
		else:
			return
		if not os.path.exists(folderpath):
			os.mkdir(folderpath)
		
		folderpath=folderpath + '/'

		files_at_this_path = dircache.listdir(folderpath)
		for _file in files_at_this_path:
			if (os.path.isfile(folderpath + _file)):
				os.remove(folderpath + _file)

		for i in range(0, len(self.timestamps)):
			self.clean2()
			self.PlotFigure2(self.timestamps[i])
			fname=folderpath + str(i) +'.png'
			self.canvas2.print_png(fname, dpi=self.dpi*2, facecolor='gray', edgecolor='gray')
		self.statusBar().showMessage('Movie Complete')
	
############### Function which is called when about is pressed ####################

	def on_about(self):
		msg = """ A Data Visualizer for QSTK:
        
         * Use the matplotlib for plotting 
         * Plotting various features of financial data
         * Integrated with Quant software toolkit
         * Save the plot to a file using the File menu
         * For more information visit http://wiki.quantsoftware.org/
		"""
		QtGui.QMessageBox.about(self, "About QuantViz", msg.strip())

#####################################################
''' END OF THE CLASS - THAT WAS AWESOME !! '''

# This is main (The easiest one to write in python)
def main():

	app = QtGui.QApplication(sys.argv)
	ex = Visualizer()
	ex.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()   
