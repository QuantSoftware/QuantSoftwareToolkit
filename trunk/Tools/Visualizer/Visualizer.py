import sys
import numpy as np
import math 
import AccessData as AD
from PyQt4 import QtGui, QtCore, Qt
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

SLIDER_RANGE=100

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


class Visualizer(QtGui.QMainWindow):
    
	def __init__(self, PandasObject1, featureslist1, symbols1, timestamps1, dMinFeat1, dMaxFeat1, startday1, endday1):
		super(Visualizer, self).__init__()

		self.PandasObject=PandasObject1
		self.featureslist=featureslist1
		self.symbols=symbols1
		self.timestamps=timestamps1
		self.dMinFeat=dMinFeat1
		self.dMaxFeat=dMaxFeat1
		self.startday=startday1
		self.endday=endday1
		self.flag=1
		self.scatterpts=[]
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
		self.CMin=0.0
		self.CMax=1.0
		self.CLow=self.CMin
		self.CHigh=self.CMax
		self.dayofplot=self.timestamps[0]
		self.create_main_frame()
        
	def create_main_frame(self):
		self.main_frame = QtGui.QWidget()

		self.statusBar().showMessage('Ready')		
		
		self.dpi=100
		self.fig = Figure((5.0, 5.0), dpi=self.dpi)
		
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.main_frame)

		self.ax = self.fig.gca(projection='3d')

#		self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
		
		self.FactorLable=QtGui.QLabel('Factors', self)
		self.font = QtGui.QFont("Times", 16, QtGui.QFont.Bold, True)
		self.font1 = QtGui.QFont("Times", 12)
		self.font2 = QtGui.QFont("Times", 14, QtGui.QFont.Bold, True)
		self.font3 = QtGui.QFont("Times", 20, QtGui.QFont.Bold, True)
		
		self.VisLable = QtGui.QLabel('QuantViz', self)
		self.SpacerItem = Qt.QSpacerItem(300,0,Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Expanding)		
		self.VisLable.setFont(self.font3)
		self.FactorLable.setFont(self.font)

############################################3

		self.XLable=QtGui.QLabel('X', self)
		self.XLable.setFont(self.font2)

		self.XCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.XCombo)	
		self.XCombo.activated[str].connect(self.XComboActivated)

		self.XMinTag=QtGui.QLabel('Min :', self)
		self.XMaxTag=QtGui.QLabel('Max :', self)
		self.XLimitTag=QtGui.QLabel('Scale:', self)
		self.XSliceTag=QtGui.QLabel('Slice :', self)

		self.XMinLable=QtGui.QLabel(str(self.XMin), self)
		self.XMinLable.setFont(self.font1)
		
		self.XRange=RangeSlider(Qt.Qt.Horizontal)
		self.XInitRangeSlider(self.XRange)

		self.XRangeSlice=RangeSlider(Qt.Qt.Horizontal)
		self.XInitRangeSliderSlice(self.XRangeSlice)
	
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

		self.XMin_Box.setText(str(self.XLow))
		self.XMax_Box.setText(str(self.XHigh))
		self.XMinSlice_Box.setText(str(self.XLowSlice))	
		self.XMaxSlice_Box.setText(str(self.XHighSlice))

		self.connect(self.XMin_Box, QtCore.SIGNAL('editingFinished()'), self.XMin_BoxInput)
		self.connect(self.XMax_Box, QtCore.SIGNAL('editingFinished()'), self.XMax_BoxInput)
		self.connect(self.XMinSlice_Box, QtCore.SIGNAL('editingFinished()'), self.XMinSlice_BoxInput)
		self.connect(self.XMaxSlice_Box, QtCore.SIGNAL('editingFinished()'), self.XMaxSlice_BoxInput)

########################################

		self.YLable=QtGui.QLabel('Y', self)
		self.YLable.setFont(self.font2)

		self.YCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.YCombo)	
		self.YCombo.activated[str].connect(self.YComboActivated)

		self.YMinTag=QtGui.QLabel('Min :', self)
		self.YMaxTag=QtGui.QLabel('Max :', self)
		self.YLimitTag=QtGui.QLabel('Scale:', self)
		self.YSliceTag=QtGui.QLabel('Slice :', self)

		self.YMinLable=QtGui.QLabel(str(self.YMin), self)
		self.YMinLable.setFont(self.font1)
		
		self.YRange=RangeSlider(Qt.Qt.Horizontal)
		self.YInitRangeSlider(self.YRange)

		self.YRangeSlice=RangeSlider(Qt.Qt.Horizontal)
		self.YInitRangeSliderSlice(self.YRangeSlice)

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

		self.YMin_Box.setText(str(self.YLow))
		self.YMax_Box.setText(str(self.YHigh))
		self.YMinSlice_Box.setText(str(self.YLowSlice))	
		self.YMaxSlice_Box.setText(str(self.YHighSlice))

		self.connect(self.YMin_Box, QtCore.SIGNAL('editingFinished()'), self.YMin_BoxInput)
		self.connect(self.YMax_Box, QtCore.SIGNAL('editingFinished()'), self.YMax_BoxInput)
		self.connect(self.YMinSlice_Box, QtCore.SIGNAL('editingFinished()'), self.YMinSlice_BoxInput)
		self.connect(self.YMaxSlice_Box, QtCore.SIGNAL('editingFinished()'), self.YMaxSlice_BoxInput)

###############################################

		self.ZLable=QtGui.QLabel('Z', self)
		self.ZLable.setFont(self.font2)		
	
		self.ZCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.ZCombo)	
		self.ZCombo.activated[str].connect(self.ZComboActivated)
	
		self.ZMinTag=QtGui.QLabel('Min :', self)
		self.ZMaxTag=QtGui.QLabel('Max :', self)
		self.ZLimitTag=QtGui.QLabel('Scale:', self)
		self.ZSliceTag=QtGui.QLabel('Slice :', self)

		self.ZMinLable=QtGui.QLabel(str(self.ZMin), self)
		self.ZMinLable.setFont(self.font1)
		
		self.ZRange=RangeSlider(Qt.Qt.Horizontal)
		self.ZInitRangeSlider(self.ZRange)

		self.ZRangeSlice=RangeSlider(Qt.Qt.Horizontal)
		self.ZInitRangeSliderSlice(self.ZRangeSlice)

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

		self.ZMin_Box.setText(str(self.ZLow))
		self.ZMax_Box.setText(str(self.ZHigh))
		self.ZMinSlice_Box.setText(str(self.ZLowSlice))	
		self.ZMaxSlice_Box.setText(str(self.ZHighSlice))

		self.connect(self.ZMin_Box, QtCore.SIGNAL('editingFinished()'), self.ZMin_BoxInput)
		self.connect(self.ZMax_Box, QtCore.SIGNAL('editingFinished()'), self.ZMax_BoxInput)
		self.connect(self.ZMinSlice_Box, QtCore.SIGNAL('editingFinished()'), self.ZMinSlice_BoxInput)
		self.connect(self.ZMaxSlice_Box, QtCore.SIGNAL('editingFinished()'), self.ZMaxSlice_BoxInput)

#######################################################

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

#####################################################

		self.DLable=QtGui.QLabel('Time ', self)
		self.DLable.setFont(self.font2)

		self.DateLable=QtGui.QLabel(self.startday.date().isoformat(), self)
		self.DateLable.setFont(self.font1)

		self.DateMinLable=QtGui.QLabel(self.startday.date().isoformat(), self)
		self.DateMinLable.setFont(self.font1)

		self.DateSlider= QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.DateSlider.setRange(0,len(self.timestamps)-1)
		self.DateSlider.valueChanged.connect(self.DateActivated)

		self.DateMaxLable=QtGui.QLabel(self.endday.date().isoformat(), self)
		self.DateMaxLable.setFont(self.font1)

########################################################

		self.SizeLable=QtGui.QLabel('Size   ', self)
		self.SizeLable.setFont(self.font2)

		self.SizeCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.SizeCombo)	
		self.SizeCombo.activated[str].connect(self.SComboActivated)

		self.SMinTag=QtGui.QLabel('Min :', self)
		self.SMaxTag=QtGui.QLabel('Max :', self)
		self.SLimitTag=QtGui.QLabel('Scale:', self)

		self.SMinLable=QtGui.QLabel(str(self.SMin), self)
		self.SMinLable.setFont(self.font1)
		
		self.SRange=RangeSlider(Qt.Qt.Horizontal)
		self.SInitRangeSlider(self.SRange)

		self.SMaxLable=QtGui.QLabel(str(self.SMax), self)
		self.SMaxLable.setFont(self.font1)

		self.SMin_Box= QtGui.QLineEdit()	
		self.SMax_Box= QtGui.QLineEdit()	

		self.SMin_Box.setMaxLength(4)
		self.SMax_Box.setMaxLength(4)
		
		self.SMin_Box.setFixedSize(50,27)
		self.SMax_Box.setFixedSize(50,27)

		self.SMin_Box.setText(str(self.SLow))
		self.SMax_Box.setText(str(self.SHigh))

		self.connect(self.SMin_Box, QtCore.SIGNAL('editingFinished()'), self.SMin_BoxInput)
		self.connect(self.SMax_Box, QtCore.SIGNAL('editingFinished()'), self.SMax_BoxInput)

#####################################################

		self.ColorLable=QtGui.QLabel('Color', self)
		self.ColorLable.setFont(self.font2)

		self.ColorCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.ColorCombo)	
		self.ColorCombo.activated[str].connect(self.CComboActivated)

		self.CMinTag=QtGui.QLabel('Min :', self)
		self.CMaxTag=QtGui.QLabel('Max :', self)
		self.CLimitTag=QtGui.QLabel('Scale:', self)

		self.CMinLable=QtGui.QLabel(str(self.CMin), self)
		self.CMinLable.setFont(self.font1)
		
		self.CRange=RangeSlider(Qt.Qt.Horizontal)
		self.CInitRangeSlider(self.CRange)

		self.CMaxLable=QtGui.QLabel(str(self.CMax), self)
		self.CMaxLable.setFont(self.font1)

		self.CMin_Box= QtGui.QLineEdit()	
		self.CMax_Box= QtGui.QLineEdit()	

		self.CMin_Box.setMaxLength(4)
		self.CMax_Box.setMaxLength(4)
		
		self.CMin_Box.setFixedSize(50,27)
		self.CMax_Box.setFixedSize(50,27)

		self.CMin_Box.setText(str(self.CLow))
		self.CMax_Box.setText(str(self.CHigh))

		self.connect(self.CMin_Box, QtCore.SIGNAL('editingFinished()'), self.CMin_BoxInput)
		self.connect(self.CMax_Box, QtCore.SIGNAL('editingFinished()'), self.CMax_BoxInput)

		self.UpdateButton =QtGui.QPushButton('Plot',self)
		self.UpdateButton.setToolTip('Update the plot')
		self.UpdateButton.resize(self.UpdateButton.sizeHint())
		self.UpdateButton.clicked.connect(self.PlotCanvas)

############################################################3333

		ExitAction = QtGui.QAction(QtGui.QIcon('Exit.png'), 'Exit', self)
		ExitAction.setShortcut('Ctrl+Q')
		ExitAction.triggered.connect(QtGui.qApp.quit)

		SaveAction = QtGui.QAction(QtGui.QIcon('save.png'), 'Save', self)
		SaveAction.setShortcut('Ctrl+S')
		SaveAction.triggered.connect(self.save_plot)

		MovieAction = QtGui.QAction(QtGui.QIcon('movie.png'), 'Movie', self)
		MovieAction.setShortcut('Ctrl+M')
		MovieAction.triggered.connect(QtGui.qApp.quit)

		SettingAction = QtGui.QAction(QtGui.QIcon('settings.png'), 'Settings', self)
		SettingAction.setShortcut('Ctrl+T')
		SettingAction.triggered.connect(QtGui.qApp.quit)

		HelpAction = QtGui.QAction(QtGui.QIcon('help.png'), 'Help', self)
		HelpAction.setShortcut('Ctrl+H')
		HelpAction.triggered.connect(QtGui.qApp.quit)        

		AboutAction = QtGui.QAction(QtGui.QIcon('about.png'), 'About', self)
		AboutAction.setShortcut('Ctrl+A')
		AboutAction.triggered.connect(QtGui.qApp.quit)

		self.Toolbar = self.addToolBar('Toolbar')
		self.Toolbar.addAction(ExitAction)
		self.Toolbar.addAction(SaveAction)
		self.Toolbar.addAction(MovieAction)
		self.Toolbar.addAction(SettingAction)
		self.Toolbar.addAction(HelpAction)
		self.Toolbar.addAction(AboutAction)

########################################################33

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


############################################################

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

##############################################################3

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

#########################################################

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

##########################################################

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

		
		Datehbox1 = QtGui.QHBoxLayout()
		Datehbox1.addWidget(self.DLable)
		Datehbox1.addWidget(self.DateLable)
		Datehbox1.addStretch(1)
		Datehbox1.addWidget(self.UpdateButton)

		Datehbox2 = QtGui.QHBoxLayout()
        
		for w in [  self.DateMinLable, self.DateSlider, self.DateMaxLable]:
			Datehbox2.addWidget(w)
			Datehbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

##############################################

		Vbox1= QtGui.QVBoxLayout()
		Vbox1.addWidget(self.FactorLable)
		Vbox1.addWidget(self.Frame1)
		Vbox1.addLayout(Xhbox1)
		Vbox1.addLayout(Xhbox2)
		Vbox1.addLayout(Xhbox3)
		Vbox1.addLayout(Xhbox4)
		Vbox1.addWidget(self.Frame2)
		Vbox1.addLayout(Yhbox1)
		Vbox1.addLayout(Yhbox2)
		Vbox1.addLayout(Yhbox3)
		Vbox1.addLayout(Yhbox4)
		Vbox1.addWidget(self.Frame3)
		Vbox1.addLayout(Zhbox1)
		Vbox1.addLayout(Zhbox2)
		Vbox1.addLayout(Zhbox3)
		Vbox1.addLayout(Zhbox4)
		Vbox1.addWidget(self.Frame4)
		Vbox1.addLayout(Shbox1)
		Vbox1.addLayout(Shbox2)
		Vbox1.addLayout(Shbox3)
		Vbox1.addWidget(self.Frame5)
		Vbox1.addLayout(Chbox1)
		Vbox1.addLayout(Chbox2)
		Vbox1.addLayout(Chbox3)
		Vbox1.addItem(self.SpacerItem)

		Vbox2 = QtGui.QVBoxLayout()
#		Vbox2.addWidget(self.Toolbar)
		Vbox2.addWidget(self.VisLable)
		Vbox2.addWidget(self.canvas)
		Vbox2.addWidget(self.Frame6)
		Vbox2.addLayout(Datehbox1)
		Vbox2.addLayout(Datehbox2)
		Vbox2.addStretch(1)
#		Vbox2.addWidget(self.mpl_toolbar)
		
		HBox= QtGui.QHBoxLayout()
		HBox.addLayout(Vbox2)
		HBox.addLayout(Vbox1)
		HBox.addStretch(1)
		
		FinalBox = QtGui.QVBoxLayout()
#		FinalBox.addWidget(self.VisLable)
		FinalBox.addLayout(HBox)
		FinalBox.addWidget(self.Frame7)
		FinalBox.addStretch(1)

		self.setWindowTitle('QuantViz')
		self.setWindowIcon(QtGui.QIcon('V.png'))

		self.main_frame.setLayout(FinalBox)
		self.setCentralWidget(self.main_frame)

#######################################################

	def FeatureComboBox(self, combo):
		for feat in self.featureslist:
			combo.addItem(feat)
        
	def XComboActivated(self,text):
		self.Xfeature=text
		self.XMax=self.dMaxFeat[str(self.Xfeature)]
		self.XMin=self.dMinFeat[str(self.Xfeature)]
		self.XMinLable.setText(str(round(self.XMin,1)))
		self.XMaxLable.setText(str(round(self.XMax,1)))
		self.XChangeValues(self.XRange.low(), self.XRange.high())
		self.XChangeValuesSlice(self.XRangeSlice.low(), self.XRangeSlice.high())

	def YComboActivated(self,text):
		self.Yfeature=text
		self.YMax=self.dMaxFeat[str(self.Yfeature)]
		self.YMin=self.dMinFeat[str(self.Yfeature)]
		self.YMinLable.setText(str(round(self.YMin,1)))
		self.YMaxLable.setText(str(round(self.YMax,1)))
		self.YChangeValues(self.YRange.low(), self.YRange.high())
		self.YChangeValuesSlice(self.YRangeSlice.low(), self.YRangeSlice.high())

	def ZComboActivated(self,text):
		self.Zfeature=text
		self.ZMax=self.dMaxFeat[str(self.Zfeature)]
		self.ZMin=self.dMinFeat[str(self.Zfeature)]
		self.ZMinLable.setText(str(round(self.ZMin,1)))
		self.ZMaxLable.setText(str(round(self.ZMax,1)))
		self.ZChangeValues(self.ZRange.low(), self.ZRange.high())
		self.ZChangeValuesSlice(self.ZRangeSlice.low(), self.ZRangeSlice.high())

	def SComboActivated(self,text):
		self.Sfeature=text
		self.SMax=self.dMaxFeat[str(self.Sfeature)]
		self.SMin=self.dMinFeat[str(self.Sfeature)]
		self.SMinLable.setText(str(round(self.SMin,1)))
		self.SMaxLable.setText(str(round(self.SMax,1)))
		self.SChangeValues(self.SRange.low(), self.SRange.high())

	def CComboActivated(self,text):
		self.Cfeature=text
		self.CMax=self.dMaxFeat[str(self.Cfeature)]
		self.CMin=self.dMinFeat[str(self.Cfeature)]
		self.CMinLable.setText(str(round(self.CMin,1)))
		self.CMaxLable.setText(str(round(self.CMax,1)))
		self.CChangeValues(self.CRange.low(), self.CRange.high())

###################################################3

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
		slide = math.floor(((valueEntered- self.XMin)*SLIDER_RANGE)/(self.XMax-self.XMin))
		self.XRange.setLow(slide)
		self.XChangeValues(slide, self.XRange.high())

	def XMinSlice_BoxInput(self):
		valueEntered=float(self.XMinSlice_Box.text())
		if valueEntered>self.XHighSlice or valueEntered<self.XMin:
			self.XMinSlice_Box.setText(str(self.XLowSlice))
			return
		slide = math.floor(((valueEntered- self.XMin)*SLIDER_RANGE)/(self.XMax-self.XMin))
		self.XRangeSlice.setLow(slide)
		self.XChangeValuesSlice(slide, self.XRangeSlice.high())

	def XMax_BoxInput(self):
		valueEntered=float(self.XMax_Box.text())
		if valueEntered<self.XLow or valueEntered>self.XMax:
			self.XMax_Box.setText(str(self.XHigh))
			return
		slide = math.ceil(((valueEntered- self.XMin)*SLIDER_RANGE)/(self.XMax-self.XMin))
		self.XRange.setHigh(slide)
		self.XChangeValues(self.XRange.low(),slide)

	def XMaxSlice_BoxInput(self):
		valueEntered=float(self.XMaxSlice_Box.text())
		if valueEntered<self.XLowSlice or valueEntered>self.XMax:
			self.XMaxSlice_Box.setText(str(self.XHighSlice))
			return
		slide = math.ceil(((valueEntered- self.XMin)*SLIDER_RANGE)/(self.XMax-self.XMin))
		self.XRangeSlice.setHigh(slide)
		self.XChangeValuesSlice(self.XRangeSlice.low(), slide)

####################################################

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
		slide = math.floor(((valueEntered- self.YMin)*SLIDER_RANGE)/(self.YMax-self.YMin))
		self.YRange.setLow(slide)
		self.YChangeValues(slide, self.YRange.high())

	def YMinSlice_BoxInput(self):
		valueEntered=float(self.YMinSlice_Box.text())
		if valueEntered>self.YHighSlice or valueEntered<self.YMin:
			self.YMinSlice_Box.setText(str(self.YLowSlice))
			return
		slide = math.floor(((valueEntered- self.YMin)*SLIDER_RANGE)/(self.YMax-self.YMin))
		self.YRangeSlice.setLow(slide)
		self.YChangeValuesSlice(slide, self.YRangeSlice.high())

	def YMax_BoxInput(self):
		valueEntered=float(self.YMax_Box.text())
		if valueEntered<self.YLow or valueEntered>self.YMax:
			self.YMax_Box.setText(str(self.YHigh))
			return
		slide = math.ceil(((valueEntered- self.YMin)*SLIDER_RANGE)/(self.YMax-self.YMin))
		self.YRange.setHigh(slide)
		self.YChangeValues(self.YRange.low(),slide)

	def YMaxSlice_BoxInput(self):
		valueEntered=float(self.YMaxSlice_Box.text())
		if valueEntered<self.YLowSlice or valueEntered>self.YMax:
			self.YMaxSlice_Box.setText(str(self.YHighSlice))
			return
		slide = math.ceil(((valueEntered- self.YMin)*SLIDER_RANGE)/(self.YMax-self.YMin))
		self.YRangeSlice.setHigh(slide)
		self.YChangeValuesSlice(self.YRangeSlice.low(), slide)

######################################################################

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
		slide = math.floor(((valueEntered- self.ZMin)*SLIDER_RANGE)/(self.ZMax-self.ZMin))
		self.ZRange.setLow(slide)
		self.ZChangeValues(slide, self.ZRange.high())

	def ZMinSlice_BoxInput(self):
		valueEntered=float(self.ZMinSlice_Box.text())
		if valueEntered>self.ZHighSlice or valueEntered<self.ZMin:
			self.ZMinSlice_Box.setText(str(self.ZLowSlice))
			return
		slide = math.floor(((valueEntered- self.ZMin)*SLIDER_RANGE)/(self.ZMax-self.ZMin))
		self.ZRangeSlice.setLow(slide)
		self.ZChangeValuesSlice(slide, self.ZRangeSlice.high())

	def ZMax_BoxInput(self):
		valueEntered=float(self.ZMax_Box.text())
		if valueEntered<self.ZLow or valueEntered>self.ZMax:
			self.ZMax_Box.setText(str(self.ZHigh))
			return
		slide = math.ceil(((valueEntered- self.ZMin)*SLIDER_RANGE)/(self.ZMax-self.ZMin))
		self.ZRange.setHigh(slide)
		self.ZChangeValues(self.ZRange.low(),slide)

	def ZMaxSlice_BoxInput(self):
		valueEntered=float(self.ZMaxSlice_Box.text())
		if valueEntered<self.ZLowSlice or valueEntered>self.ZMax:
			self.ZMaxSlice_Box.setText(str(self.ZHighSlice))
			return
		slide = math.ceil(((valueEntered- self.ZMin)*SLIDER_RANGE)/(self.ZMax-self.ZMin))
		self.ZRangeSlice.setHigh(slide)
		self.ZChangeValuesSlice(self.ZRangeSlice.low(), slide)

##################################################

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
		slide = math.floor(((valueEntered- self.SMin)*SLIDER_RANGE)/(self.SMax-self.SMin))
		self.SRange.setLow(slide)
		self.SChangeValues(slide, self.SRange.high())

	def SMax_BoxInput(self):
		valueEntered=float(self.SMax_Box.text())
		if valueEntered<self.SLow or valueEntered>self.SMax:
			self.SMax_Box.setText(str(self.SHigh))
			return
		slide = math.ceil(((valueEntered- self.SMin)*SLIDER_RANGE)/(self.SMax-self.SMin))
		self.SRange.setHigh(slide)
		self.SChangeValues(self.SRange.low(),slide)

###########################################################

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
		slide = math.floor(((valueEntered- self.CMin)*SLIDER_RANGE)/(self.CMax-self.CMin))
		self.CRange.setLow(slide)
		self.CChangeValues(slide, self.CRange.high())

	def CMax_BoxInput(self):
		valueEntered=float(self.CMax_Box.text())
		if valueEntered<self.CLow or valueEntered>self.CMax:
			self.CMax_Box.setText(str(self.CHigh))
			return
		slide = math.ceil(((valueEntered- self.CMin)*SLIDER_RANGE)/(self.CMax-self.CMin))
		self.CRange.setHigh(slide)
		self.CChangeValues(self.CRange.low(),slide)

	def DateActivated(self, index):
		self.dayofplot=self.timestamps[index]
		dateval=self.timestamps[index]
		dateval=dateval.date().isoformat()
		self.DateLable.setText(dateval)
		self.DateLable.adjustSize() 

#########################################################

	def inrange(self, x, minx, maxx):
		if x>minx and x<maxx: return x
		else: return np.NAN

	def inrangeS(self, x, minx, maxx, absmin, absmax):
		if x>minx and x<maxx: return (599*((x-absmin)/(absmax-absmin))+10)
		else: return 0

	def inrangeC(self, x, minx, maxx, absmin, absmax):
		if x>minx and x<maxx: return (599*((x-absmin)/(absmax-absmin))+10)
		else: return np.NAN

	def PlotCanvas(self):

		if self.flag==0:
			for pt in self.scatterpts :
				pt.remove()
		self.scatterpts = []

		xs=self.PandasObject[str(self.Xfeature)].xs(self.dayofplot)
		ys=self.PandasObject[str(self.Yfeature)].xs(self.dayofplot)
		zs=self.PandasObject[str(self.Zfeature)].xs(self.dayofplot)	
	
		size=self.PandasObject[str(self.Sfeature)].xs(self.dayofplot)
		color=self.PandasObject[str(self.Cfeature)].xs(self.dayofplot)

		xs1 = [self.inrange(x, max(self.XLow, self.XLowSlice), min(self.XHigh, self.XHighSlice)) for x in xs]
		ys1 = [self.inrange(y, max(self.YLow, self.YLowSlice), min(self.YHigh, self.YHighSlice)) for y in ys]
		zs1 = [self.inrange(z, max(self.ZLow, self.ZLowSlice), min(self.ZHigh, self.ZHighSlice)) for z in zs]

		size1 = [self.inrangeS(s, self.SLow, self.SHigh, self.SMin, self.SMax) for s in size]
		color1 = [self.inrangeC(c, self.CLow, self.CHigh, self.CMin, self.CMax) for c in color]

#	If you do not want color to rescale itself then plot the scatter iteratively and use alpha as parameter of Iter.

		pt=self.ax.scatter(xs1,ys1,zs1,marker='o', alpha=0.5, c=color1, s=size1)
		self.scatterpts.append(pt)
		
		self.ax.set_xlim(self.XLow, self.XHigh)
		self.ax.set_ylim(self.YLow, self.YHigh)
		self.ax.set_zlim(self.ZLow, self.ZHigh)	
	
		self.ax.set_xlabel(self.Xfeature)
		self.ax.set_ylabel(self.Yfeature)
		self.ax.set_zlabel(self.Zfeature)

		self.canvas.draw()
		self.flag=0

		self.statusBar().showMessage('Update the Plot')

#####################################################

	def save_plot(self):
		fname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save file', '/home/untitled.png', 'Images (*.png *.xpm *.jpg)', options=QtGui.QFileDialog.DontUseNativeDialog))

		if self.flag==0:
			for pt in self.scatterpts :
				pt.remove()
		self.scatterpts = []

		xs=self.PandasObject[str(self.Xfeature)].xs(self.dayofplot)
		ys=self.PandasObject[str(self.Yfeature)].xs(self.dayofplot)
		zs=self.PandasObject[str(self.Zfeature)].xs(self.dayofplot)	
	
		size=self.PandasObject[str(self.Sfeature)].xs(self.dayofplot)
		color=self.PandasObject[str(self.Cfeature)].xs(self.dayofplot)

		xs1 = [self.inrange(x, max(self.XLow, self.XLowSlice), min(self.XHigh, self.XHighSlice)) for x in xs]
		ys1 = [self.inrange(y, max(self.YLow, self.YLowSlice), min(self.YHigh, self.YHighSlice)) for y in ys]
		zs1 = [self.inrange(z, max(self.ZLow, self.ZLowSlice), min(self.ZHigh, self.ZHighSlice)) for z in zs]

		size1 = [self.inrangeS(s, self.SLow, self.SHigh, self.SMin, self.SMax) for s in size]
		color1 = [self.inrangeC(c, self.CLow, self.CHigh, self.CMin, self.CMax) for c in color]

		pt=self.ax.scatter(xs1,ys1,zs1,marker='o', alpha=0.5, c=color1, s=size1)
		self.scatterpts.append(pt)
		
		self.ax.set_xlim(self.XLow, self.XHigh)
		self.ax.set_ylim(self.YLow, self.YHigh)
		self.ax.set_zlim(self.ZLow, self.ZHigh)	
	
		self.ax.set_xlabel(self.Xfeature)
		self.ax.set_ylabel(self.Yfeature)
		self.ax.set_zlabel(self.Zfeature)
		self.canvas.print_png(fname, dpi=self.dpi, facecolor='gray', edgecolor='gray')

#####################################################

def main():
	(PandasObject, featureslist, symbols, timestamps)=AD.ReadData()
	(dMinFeat, dMaxFeat, startday, endday)=AD.DataParameter(PandasObject, featureslist, symbols, timestamps)
	
	app = QtGui.QApplication(sys.argv)
	ex = Visualizer(PandasObject, featureslist, symbols, timestamps, dMinFeat, dMaxFeat, startday, endday)
	ex.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()   
