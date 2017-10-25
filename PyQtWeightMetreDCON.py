# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 14:45:43 2017

@author: LeDima
"""

from GUIWeightMetreDCON import Ui_Form

import sys
import datetime

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MyMplCanvas(FigureCanvas):
    #"""Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
            # We want the axes cleared every time plot() is called
            self.axes.hold(False)
            #self.axes.
    
            self.compute_initial_figure()
    
            FigureCanvas.__init__(self, fig)    
            self.setParent(parent)
    
            FigureCanvas.setSizePolicy(self,
                    QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Expanding)
            FigureCanvas.updateGeometry(self)

        #def compute_initial_figure(self):
        #    pass

class MyStaticMplCanvas(MyMplCanvas):
    #"""Simple canvas with a sine plot."""
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)        

class MyDynamicMplCanvas(MyMplCanvas):
 #"""A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(500)
        self.j=0
    
    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')
        self.axes.set_title('Vertical lines demo')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self.j=self.j+1
        l = [1+i+self.j for i in range(4)]
        
        print(type(l))
        #self.axes.Axes(xscale=20, yscale=20)
        self.axes.plot(l, 'r')
        self.axes.set_title('Vertical lines demo')
        
        self.draw()            
        
class MyWindow(QtWidgets.QWidget,Ui_Form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=None)
        self.setupUi(self)
        
        # Подключить созданные нами слоты к виджетам
        #l = QtWidgets.QVBoxLayout(self.mplwindow)
        #sc = MyStaticMplCanvas(self.mplwindow, width=5, height=4, dpi=100)
        sc = MyDynamicMplCanvas(self.mplwindow, width=5, height=4, dpi=100)
        self.verticalLayout.addWidget(sc)
        self.verticalLayout.addWidget(self.textBrowser)
        #l.addWidget(sc)
        self.mplwindow.setFocus()
    def resizeEvent(self, e):
        self.mplwindow.setSizeIncrement(QtCore.QSize(e.size().width(), e.size().height()))
        #self.verticalLayout.SetFixedSize(e.size)
        #print("w = {0}; h = {1}".format(e.size().width(),
        #                                e.size().height()))
        QtWidgets.QWidget.resizeEvent(self, e) # Отправляем дальше

        
if __name__ == "__main__":
        
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())