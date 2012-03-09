import sys
import numpy as np
import AccessData as AD
from PyQt4 import QtGui, QtCore, Qt
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

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
		self.CMin=0.0
		self.CMax=1.0
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
		
		self.VisLable.setFont(self.font3)
		self.FactorLable.setFont(self.font)
		
		self.XLable=QtGui.QLabel('X', self)
		self.XLable.setFont(self.font2)

		self.XCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.XCombo)	
		self.XCombo.activated[str].connect(self.XComboActivated)

		self.XMinTag=QtGui.QLabel('Min :', self)
		self.XMaxTag=QtGui.QLabel('Max :', self)
		self.XLimitTag=QtGui.QLabel('Limit:', self)
		self.XSliceTag=QtGui.QLabel('Slice :', self)

		self.XMinLcd = QtGui.QLCDNumber(4, self)
		self.XMaxLcd = QtGui.QLCDNumber(4, self)
		self.XMinLcd.setSegmentStyle(2)
		self.XMaxLcd.setSegmentStyle(2)

		self.XMinLcdSlice = QtGui.QLCDNumber(4, self)
		self.XMaxLcdSlice = QtGui.QLCDNumber(4, self)
		self.XMinLcdSlice.setSegmentStyle(2)
		self.XMaxLcdSlice.setSegmentStyle(2)

		self.XMinLable=QtGui.QLabel(str(self.XMin), self)
		self.XMinLable.setFont(self.font1)
		
		self.XRange=RangeSlider(Qt.Qt.Horizontal)
		self.XInitRangeSlider(self.XRange)

		self.XRangeSlice=RangeSlider(Qt.Qt.Horizontal)
		self.XInitRangeSliderSlice(self.XRangeSlice)
	
		self.XMaxLable=QtGui.QLabel(str(self.XMax), self)
		self.XMaxLable.setFont(self.font1)

		self.YLable=QtGui.QLabel('Y', self)
		self.YLable.setFont(self.font2)

		self.YCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.YCombo)	
		self.YCombo.activated[str].connect(self.YComboActivated)

		self.YMinLcd = QtGui.QLCDNumber(4, self)
		self.YMaxLcd = QtGui.QLCDNumber(4, self)
		self.YMinLcd.setSegmentStyle(2)
		self.YMaxLcd.setSegmentStyle(2)

		self.YMinLcdSlice = QtGui.QLCDNumber(4, self)
		self.YMaxLcdSlice = QtGui.QLCDNumber(4, self)
		self.YMinLcdSlice.setSegmentStyle(2)
		self.YMaxLcdSlice.setSegmentStyle(2)

		self.YMinTag=QtGui.QLabel('Min :', self)
		self.YMaxTag=QtGui.QLabel('Max :', self)
		self.YLimitTag=QtGui.QLabel('Limit:', self)
		self.YSliceTag=QtGui.QLabel('Slice :', self)

		self.YMinLable=QtGui.QLabel(str(self.YMin), self)
		self.YMinLable.setFont(self.font1)
		
		self.YRange=RangeSlider(Qt.Qt.Horizontal)
		self.YInitRangeSlider(self.YRange)

		self.YRangeSlice=RangeSlider(Qt.Qt.Horizontal)
		self.YInitRangeSliderSlice(self.YRangeSlice)

		self.YMaxLable=QtGui.QLabel(str(self.YMax), self)
		self.YMaxLable.setFont(self.font1)

		self.ZLable=QtGui.QLabel('Z', self)
		self.ZLable.setFont(self.font2)		
	
		self.ZCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.ZCombo)	
		self.ZCombo.activated[str].connect(self.ZComboActivated)
	
		self.ZMinTag=QtGui.QLabel('Min :', self)
		self.ZMaxTag=QtGui.QLabel('Max :', self)
		self.ZLimitTag=QtGui.QLabel('Limit:', self)
		self.ZSliceTag=QtGui.QLabel('Slice :', self)
		
		self.ZMinLcd = QtGui.QLCDNumber(4, self)
		self.ZMaxLcd = QtGui.QLCDNumber(4, self)
		self.ZMinLcd.setSegmentStyle(2)
		self.ZMaxLcd.setSegmentStyle(2)

		self.ZMinLcdSlice = QtGui.QLCDNumber(4, self)
		self.ZMaxLcdSlice = QtGui.QLCDNumber(4, self)
		self.ZMinLcdSlice.setSegmentStyle(2)
		self.ZMaxLcdSlice.setSegmentStyle(2)

		self.ZMinLable=QtGui.QLabel(str(self.ZMin), self)
		self.ZMinLable.setFont(self.font1)
		
		self.ZRange=RangeSlider(Qt.Qt.Horizontal)
		self.ZInitRangeSlider(self.ZRange)

		self.ZRangeSlice=RangeSlider(Qt.Qt.Horizontal)
		self.ZInitRangeSliderSlice(self.ZRangeSlice)

		self.ZMaxLable=QtGui.QLabel(str(self.ZMax), self)
		self.ZMaxLable.setFont(self.font1)

		self.Frame1= QtGui.QFrame()
		self.Frame1.setFrameShape(4)

		self.DLable=QtGui.QLabel('Date ', self)
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

		self.Frame2= QtGui.QFrame()
		self.Frame2.setFrameShape(4)

		self.Frame3= QtGui.QFrame()
		self.Frame3.setFrameShape(4)

		self.Frame4= QtGui.QFrame()
		self.Frame4.setFrameShape(4)

		self.SizeLable=QtGui.QLabel('Size   ', self)
		self.SizeLable.setFont(self.font2)

		self.SizeCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.SizeCombo)	
		self.SizeCombo.activated[str].connect(self.SComboActivated)

		self.ColorLable=QtGui.QLabel('Color', self)
		self.ColorLable.setFont(self.font2)

		self.ColorCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.ColorCombo)	
		self.ColorCombo.activated[str].connect(self.CComboActivated)

		self.UpdateButton =QtGui.QPushButton('Refresh',self)
		self.UpdateButton.setToolTip('Update the plot')
		self.UpdateButton.resize(self.UpdateButton.sizeHint())
		self.UpdateButton.clicked.connect(self.PlotCanvas)

		ExitAction = QtGui.QAction(QtGui.QIcon('Exit.png'), 'Exit', self)
		ExitAction.setShortcut('Ctrl+Q')
		ExitAction.triggered.connect(QtGui.qApp.quit)

		SaveAction = QtGui.QAction(QtGui.QIcon('save.png'), 'Save', self)
		SaveAction.setShortcut('Ctrl+S')
		SaveAction.triggered.connect(QtGui.qApp.quit)

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
        
		for w in [  self.XLimitTag ,self.XMinLcd, self.XRange, self.XMaxLcd]:
			Xhbox3.addWidget(w)
			Xhbox3.setAlignment(w, QtCore.Qt.AlignVCenter)

		Xhbox4 = QtGui.QHBoxLayout()
        
		for w in [  self.XSliceTag, self.XMinLcdSlice, self.XRangeSlice, self.XMaxLcdSlice]:
			Xhbox4.addWidget(w)
			Xhbox4.setAlignment(w, QtCore.Qt.AlignVCenter)

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
        
		for w in [ self.YLimitTag, self.YMinLcd, self.YRange, self.YMaxLcd]:
			Yhbox3.addWidget(w)
			Yhbox3.setAlignment(w, QtCore.Qt.AlignVCenter)

		Yhbox4 = QtGui.QHBoxLayout()
        
		for w in [  self.YSliceTag,self.YMinLcdSlice, self.YRangeSlice, self.YMaxLcdSlice]:
			Yhbox4.addWidget(w)
			Yhbox4.setAlignment(w, QtCore.Qt.AlignVCenter)

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
        
		for w in [ self.ZLimitTag ,self.ZMinLcd, self.ZRange, self.ZMaxLcd]:
			Zhbox3.addWidget(w)
			Zhbox3.setAlignment(w, QtCore.Qt.AlignVCenter)

		Zhbox4 = QtGui.QHBoxLayout()
        
		for w in [  self.ZSliceTag,self.ZMinLcdSlice, self.ZRangeSlice, self.ZMaxLcdSlice]:
			Zhbox4.addWidget(w)
			Zhbox4.setAlignment(w, QtCore.Qt.AlignVCenter)

		shbox = QtGui.QHBoxLayout()

		for w in [  self.SizeLable, self.SizeCombo]:
			shbox.addWidget(w)
			shbox.setAlignment(w, QtCore.Qt.AlignVCenter)
		
		shbox.addStretch(1)

		chbox = QtGui.QHBoxLayout()

		for w in [self.ColorLable, self.ColorCombo]:
			chbox.addWidget(w)
			chbox.setAlignment(w, QtCore.Qt.AlignVCenter)

		chbox.addStretch(1)
		
		scvbox = QtGui.QVBoxLayout()
		scvbox.addLayout(shbox)
		scvbox.addLayout(chbox)

		schbox = QtGui.QHBoxLayout()
		schbox.addLayout(scvbox)
		schbox.setAlignment(schbox, QtCore.Qt.AlignVCenter)
		schbox.addWidget(self.UpdateButton)
		schbox.setAlignment(self.UpdateButton, QtCore.Qt.AlignVCenter)

		Datehbox1 = QtGui.QHBoxLayout()
		Datehbox1.addWidget(self.DLable)
		Datehbox1.addWidget(self.DateLable)
		Datehbox1.addStretch(1)

		Datehbox2 = QtGui.QHBoxLayout()
        
		for w in [  self.DateMinLable, self.DateSlider, self.DateMaxLable]:
			Datehbox2.addWidget(w)
			Datehbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Vbox1= QtGui.QVBoxLayout()
		Vbox1.addWidget(self.FactorLable)
		Vbox1.addWidget(self.Frame3)
		Vbox1.addLayout(Xhbox1)
		Vbox1.addLayout(Xhbox2)
		Vbox1.addLayout(Xhbox3)
		Vbox1.addLayout(Xhbox4)
		Vbox1.addLayout(Yhbox1)
		Vbox1.addLayout(Yhbox2)
		Vbox1.addLayout(Yhbox3)
		Vbox1.addLayout(Yhbox4)
		Vbox1.addLayout(Zhbox1)
		Vbox1.addLayout(Zhbox2)
		Vbox1.addLayout(Zhbox3)
		Vbox1.addLayout(Zhbox4)
		Vbox1.addWidget(self.Frame1)
		Vbox1.addLayout(Datehbox1)
		Vbox1.addLayout(Datehbox2)
		Vbox1.addWidget(self.Frame2)
		Vbox1.addLayout(schbox)
		Vbox1.addWidget(self.Frame4)

		Finalvbox = QtGui.QVBoxLayout()
#		Finalvbox.addWidget(self.Toolbar)
		Finalvbox.addWidget(self.VisLable)
		Finalvbox.addWidget(self.canvas)
#		Finalvbox.addWidget(self.mpl_toolbar)
		
		FinalBox= QtGui.QHBoxLayout()
		FinalBox.addLayout(Finalvbox)
		FinalBox.addLayout(Vbox1)
		FinalBox.addStretch(1)
		
		SuperFinalBox = QtGui.QVBoxLayout()
#		SuperFinalBox.addWidget(self.VisLable)
		SuperFinalBox.addLayout(FinalBox)
		SuperFinalBox.addStretch(1)

		self.setWindowTitle('QuantViz')
		self.setWindowIcon(QtGui.QIcon('V.png'))

		self.main_frame.setLayout(SuperFinalBox)
		self.setCentralWidget(self.main_frame)        

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

	def CComboActivated(self,text):
		self.Cfeature=text
		self.CMax=self.dMaxFeat[str(self.Cfeature)]
		self.CMin=self.dMinFeat[str(self.Cfeature)]

	def XChangeValues(self, low, high):
		self.XLow=low*0.02*(self.XMax-self.XMin)+self.XMin
		self.XHigh=high*0.02*(self.XMax-self.XMin)+self.XMin		
		self.XMinLcd.display(self.XLow)
		self.XMaxLcd.display(self.XHigh)

	def XChangeValuesSlice(self, low, high):
		self.XLowSlice=low*0.02*(self.XMax-self.XMin)+self.XMin
		self.XHighSlice=high*0.02*(self.XMax-self.XMin)+self.XMin		
		self.XMinLcdSlice.display(self.XLowSlice)
		self.XMaxLcdSlice.display(self.XHighSlice)		
		
	def XInitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(50)
		slider.setLow(0)
		slider.setHigh(50)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.XChangeValues)

	def XInitRangeSliderSlice(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(50)
		slider.setLow(0)
		slider.setHigh(50)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.XChangeValuesSlice)

	def YChangeValues(self, low, high):
		self.YLow=low*0.02*(self.YMax-self.YMin)+self.YMin
		self.YHigh=high*0.02*(self.YMax-self.YMin)+self.YMin		
		self.YMinLcd.display(self.YLow)
		self.YMaxLcd.display(self.YHigh)	

	def YChangeValuesSlice(self, low, high):
		self.YLowSlice=low*0.02*(self.YMax-self.YMin)+self.YMin
		self.YHighSlice=high*0.02*(self.YMax-self.YMin)+self.YMin		
		self.YMinLcdSlice.display(self.YLowSlice)
		self.YMaxLcdSlice.display(self.YHighSlice)	

	def YInitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(50)
		slider.setLow(0)
		slider.setHigh(50)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.YChangeValues)

	def YInitRangeSliderSlice(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(50)
		slider.setLow(0)
		slider.setHigh(50)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.YChangeValuesSlice)

	def ZChangeValues(self, low, high):
		self.ZLow=low*0.02*(self.ZMax-self.ZMin)+self.ZMin
		self.ZHigh=high*0.02*(self.ZMax-self.ZMin)+self.ZMin		
		self.ZMinLcd.display(self.ZLow)
		self.ZMaxLcd.display(self.ZHigh)		

	def ZChangeValuesSlice(self, low, high):
		self.ZLowSlice=low*0.02*(self.ZMax-self.ZMin)+self.ZMin
		self.ZHighSlice=high*0.02*(self.ZMax-self.ZMin)+self.ZMin		
		self.ZMinLcdSlice.display(self.ZLowSlice)
		self.ZMaxLcdSlice.display(self.ZHighSlice)

	def ZInitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(50)
		slider.setLow(0)
		slider.setHigh(50)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.ZChangeValues)

	def ZInitRangeSliderSlice(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(50)
		slider.setLow(0)
		slider.setHigh(50)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.ZChangeValuesSlice)

	def DateActivated(self, index):
		self.dayofplot=self.timestamps[index]
		dateval=self.timestamps[index]
		dateval=dateval.date().isoformat()
		self.DateLable.setText(dateval)
		self.DateLable.adjustSize() 

	def inrange(self, x, minx, maxx):
		if x>minx and x<maxx: return x
		else: return np.NAN

	def scale(self, x, minx, maxx):
		return (599*((x-minx)/(maxx-minx))+10)

	def PlotCanvas(self):
		self.ax.cla()
		self.ax.mouse_init(rotate_btn=1, zoom_btn=3)
		self.ax.set_frame_on(False)

		xs=self.PandasObject[str(self.Xfeature)].xs(self.dayofplot)
		ys=self.PandasObject[str(self.Yfeature)].xs(self.dayofplot)
		zs=self.PandasObject[str(self.Zfeature)].xs(self.dayofplot)	
	
		size=self.PandasObject[str(self.Sfeature)].xs(self.dayofplot)
		color=self.PandasObject[str(self.Cfeature)].xs(self.dayofplot)

		xs1 = [self.inrange(x, max(self.XLow, self.XLowSlice), min(self.XHigh, self.XHighSlice)) for x in xs]
		ys1 = [self.inrange(y, max(self.YLow, self.YLowSlice), min(self.YHigh, self.YHighSlice)) for y in ys]
		zs1 = [self.inrange(z, max(self.ZLow, self.ZLowSlice), min(self.ZHigh, self.ZHighSlice)) for z in zs]

		size1 =  [self.scale(s, self.SMin, self.SMax) for s in size]
		color1 = [self.scale(c, self.CMin, self.CMax) for c in color]

		p=self.ax.scatter(xs1,ys1,zs1,marker='o', alpha=0.5, c=color1, s=size1)
		
		self.ax.set_xlim(self.XLow, self.XHigh)
		self.ax.set_ylim(self.YLow, self.YHigh)
		self.ax.set_zlim(self.ZLow, self.ZHigh)	
	
#		self.ax.set_xlabel(self.Xfeature)
#		self.ax.set_ylabel(self.Yfeature)
#		self.ax.set_zlabel(self.Zfeature)

		self.ax.set_xlabel('X')
		self.ax.set_ylabel('Y')
		self.ax.set_zlabel('Z')


		self.canvas.draw()
		self.statusBar().showMessage('Update the Plot')

def main():
	(PandasObject, featureslist, symbols, timestamps)=AD.ReadData()
	(dMinFeat, dMaxFeat, startday, endday)=AD.DataParameter(PandasObject, featureslist, symbols, timestamps)
	
	app = QtGui.QApplication(sys.argv)
	ex = Visualizer(PandasObject, featureslist, symbols, timestamps, dMinFeat, dMaxFeat, startday, endday)
	ex.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()   
