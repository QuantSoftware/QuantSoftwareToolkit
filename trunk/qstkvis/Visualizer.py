import sys
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


class Visualizer(QtGui.QMainWindow):
    
	def __init__(self):
		super(Visualizer, self).__init__()
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
		
		self.VisLable = QtGui.QLabel('DataVisualizer', self)
		
		self.VisLable.setFont(self.font3)
		self.FactorLable.setFont(self.font)
		
		self.XLable=QtGui.QLabel('X', self)
		self.XLable.setFont(self.font2)

		self.XCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.XCombo)	
		self.XCombo.activated[str].connect(self.ComboActivated)

		self.XSpace=QtGui.QLabel('    ', self)

		self.XMinLcd = QtGui.QLCDNumber(3, self)
		self.XMaxLcd = QtGui.QLCDNumber(3, self)

		self.XMinLable=QtGui.QLabel('Min', self)
		self.XMinLable.setFont(self.font1)
		
		self.XRange=RangeSlider(Qt.Qt.Horizontal)
		self.InitRangeSlider(self.XRange)
		
		self.XMaxLable=QtGui.QLabel('Max', self)
		self.XMaxLable.setFont(self.font1)

		self.YLable=QtGui.QLabel('Y', self)
		self.YLable.setFont(self.font2)

		self.YCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.YCombo)	
		self.YCombo.activated[str].connect(self.ComboActivated)

		self.YSpace=QtGui.QLabel('    ', self)

		self.YMinLcd = QtGui.QLCDNumber(3, self)
		self.YMaxLcd = QtGui.QLCDNumber(3, self)

		self.YMinLable=QtGui.QLabel('Min', self)
		self.YMinLable.setFont(self.font1)
		
		self.YRange=RangeSlider(Qt.Qt.Horizontal)
		self.InitRangeSlider(self.YRange)

		self.YMaxLable=QtGui.QLabel('Max', self)
		self.YMaxLable.setFont(self.font1)

		self.ZLable=QtGui.QLabel('Z', self)
		self.ZLable.setFont(self.font2)		
	
		self.ZCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.ZCombo)	
		self.ZCombo.activated[str].connect(self.ComboActivated)
	
		self.ZSpace=QtGui.QLabel('    ', self)
		
		self.ZMinLcd = QtGui.QLCDNumber(3, self)
		self.ZMaxLcd = QtGui.QLCDNumber(3, self)

		self.ZMinLable=QtGui.QLabel('Min', self)
		self.ZMinLable.setFont(self.font1)
		
		self.ZRange=RangeSlider(Qt.Qt.Horizontal)
		self.InitRangeSlider(self.ZRange)

		self.ZMaxLable=QtGui.QLabel('Max', self)
		self.ZMaxLable.setFont(self.font1)

		self.Frame1= QtGui.QFrame()
		self.Frame1.setFrameShape(4)

		self.DLable=QtGui.QLabel('Date ', self)
		self.DLable.setFont(self.font2)

		self.DateLable=QtGui.QLabel('1-1-2011', self)
		self.DateLable.setFont(self.font1)

		self.DateMinLable=QtGui.QLabel('Start Date', self)
		self.DateMinLable.setFont(self.font1)

		self.DateSlider= QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.DateSlider.valueChanged.connect(self.DateActivated)

		self.DateMaxLable=QtGui.QLabel('End Date', self)
		self.DateMaxLable.setFont(self.font1)

		self.Frame2= QtGui.QFrame()
		self.Frame2.setFrameShape(4)

		self.Frame3= QtGui.QFrame()
		self.Frame3.setFrameShape(4)

		self.Frame4= QtGui.QFrame()
		self.Frame4.setFrameShape(4)

		self.SizeLable=QtGui.QLabel('Size', self)
		self.SizeLable.setFont(self.font2)

		self.SizeCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.SizeCombo)	
		self.SizeCombo.activated[str].connect(self.ComboActivated)

		self.ColorLable=QtGui.QLabel('Color', self)
		self.ColorLable.setFont(self.font2)

		self.ColorCombo = QtGui.QComboBox(self)
		self.FeatureComboBox(self.ColorCombo)	
		self.ColorCombo.activated[str].connect(self.ComboActivated)

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
        
		for w in [  self.XLable, self.XCombo, self.XSpace, self.XMinLcd, self.XMaxLcd]:
			Xhbox1.addWidget(w)
			Xhbox1.setAlignment(w, QtCore.Qt.AlignVCenter)

		Xhbox2 = QtGui.QHBoxLayout()
        
		for w in [  self.XMinLable, self.XRange, self.XMaxLable]:
			Xhbox2.addWidget(w)
			Xhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Yhbox1 = QtGui.QHBoxLayout()
        
		for w in [  self.YLable, self.YCombo, self.YSpace, self.YMinLcd, self.YMaxLcd]:
			Yhbox1.addWidget(w)
			Yhbox1.setAlignment(w, QtCore.Qt.AlignVCenter)

		Yhbox2 = QtGui.QHBoxLayout()
        
		for w in [  self.YMinLable, self.YRange, self.YMaxLable]:
			Yhbox2.addWidget(w)
			Yhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		Zhbox1 = QtGui.QHBoxLayout()
        
		for w in [  self.ZLable, self.ZCombo, self.ZSpace, self.ZMinLcd, self.ZMaxLcd]:
			Zhbox1.addWidget(w)
			Zhbox1.setAlignment(w, QtCore.Qt.AlignVCenter)

		Zhbox2 = QtGui.QHBoxLayout()
        
		for w in [  self.ZMinLable, self.ZRange, self.ZMaxLable]:
			Zhbox2.addWidget(w)
			Zhbox2.setAlignment(w, QtCore.Qt.AlignVCenter)

		schbox = QtGui.QHBoxLayout()

		for w in [  self.SizeLable, self.SizeCombo, self.ColorLable, self.ColorCombo]:
			schbox.addWidget(w)
			schbox.setAlignment(w, QtCore.Qt.AlignVCenter)

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
		Vbox1.addLayout(Yhbox1)
		Vbox1.addLayout(Yhbox2)
		Vbox1.addLayout(Zhbox1)
		Vbox1.addLayout(Zhbox2)
		Vbox1.addWidget(self.Frame1)
		Vbox1.addLayout(Datehbox1)
		Vbox1.addLayout(Datehbox2)
		Vbox1.addWidget(self.Frame2)
		Vbox1.addLayout(schbox)
		Vbox1.addWidget(self.Frame4)

		Finalvbox= QtGui.QVBoxLayout()
		Finalvbox.addWidget(self.canvas)
#		Finalvbox.addWidget(self.mpl_toolbar)
		
		FinalBox= QtGui.QHBoxLayout()
		FinalBox.addLayout(Finalvbox)
		FinalBox.addLayout(Vbox1)
		
		SuperFinalBox = QtGui.QVBoxLayout()
		SuperFinalBox.addWidget(self.VisLable)
		SuperFinalBox.addLayout(FinalBox)

		self.setWindowTitle('DataVisualizer')
		self.setWindowIcon(QtGui.QIcon('V.png'))

		self.main_frame.setLayout(SuperFinalBox)
		self.setCentralWidget(self.main_frame)        

	def FeatureComboBox(self, combo):
		combo.addItem("Ubuntu")
		combo.addItem("Mandriva")
		combo.addItem("Fedora")
		combo.addItem("Red Hat")
		combo.addItem("Gentoo")
        
	def ComboActivated(self,text):
		self.statusBar().showMessage(text)

	def ChangeValues(self, low, high):
		print 'Low is '+ str(low) + ' High is ' + str(high)

	def InitRangeSlider(self, slider):
		slider.setMinimum(0)
		slider.setMaximum(10000)
		slider.setLow(0)
		slider.setHigh(10000)
		slider.setTickPosition(QtGui.QSlider.TicksBelow)
		QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved'), self.ChangeValues)

	def DateActivated(self, text):
		self.DateLable.setText(str(text))
		self.DateLable.adjustSize() 

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Visualizer()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()   
