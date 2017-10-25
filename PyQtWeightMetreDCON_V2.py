# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 12:24:22 2017

@author: Dima
"""
import os
import sys
import random
import csv
import json
import serial
import numpy as np
from time import strftime,localtime
#import matplotlib
# Make sure that we are using QT5
#matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

#from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#progname = os.path.basename(sys.argv[0])
#progversion = "0.1"

class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(dict)
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.runing =1
            
    def run(self):
        self.CreateFileConfigandDate()
        
        while 1:
            self.msleep(self.MainDict['PeriodDate']) 
            if self.runing==1:
                             # "Засыпаем" на 1 секунды
                
                self.data_to_send = self.write_serial_port(self.ser, "#"+self.MainDict['ICPCONAdres'])
                self.dataFloat =[float(self.data_to_send[i:i+7]) for i in range(56) if i%7==0]
                
                self.data1['Time'].append(strftime("%H:%M:%S",localtime()))
                
                if self.first==1: # Поверка на первый запуск приложения 
                    self.T_average=self.dataFloat[0] # Назначить среденее значение первым считаным значением 
                    self.first=0
                else:
                    if self.dataFloat[0]>self.T_average*1.5: # Отбрасывание значений превышаюших среднее в 1,5раз фильтр помех 
                        pass
                    else:
                        self.T_average=self.T_average + (self.dataFloat[0] - self.T_average) / 20.0 # Расчет среднего значения по двацати прошлым значениям  
                
               
                
                self.data1['Date'][0].append(round(self.T_average,3)) 
                self.data1['Date'][1].append(self.dataFloat[0])
                
    #            with open('DateFile.csv', 'a') as DateFile:
    #                DateFile.write(str(self.data1['Time'][-1:][0])+","+
    #                                   format(self.data1['Date'][0][-1:][0], '+.03f')+","+
    #                                   format(self.data1['Date'][1][-1:][0], '+.03f')+"\n")   
    #            DateFile.close()
    
           
                if self.counterSave>10:
                    with open('DateFile.txt', mode='w', encoding='utf-8') as f:
                        json.dump(self.data1, f, indent=2)
                    f.close()
                    
                    with open('DateFile.csv', 'a') as DateFile:
                        DateFile.write(str(self.data1['Time'][-1:][0])+","+
                                           format(self.data1['Date'][0][-1:][0], '+.03f')+","+
                                           format(self.data1['Date'][1][-1:][0], '+.03f')+"\n")   
                    DateFile.close()
                    self.counterSave=0
                
                self.counterSave+=1      
                
                print(self.data_to_send)
                
                self.mysignal.emit(self.data1)
            elif self.runing==2:
                pass
            else:
                self.ser.close()
                print("port close")
                break
            
            #self.parent.TextConsole.insertPlainText("asdasdas\n")
            # Передача данных из потока через сигнал
            
            
                
    
    
    def CreateFileConfigandDate(self):
        try:                                                        # При отстуствии файла конфигурации DateFile.txt создается новый
            with open('DateFile.txt', 'r', encoding='utf-8') as f:
                self.data1 = json.load(f) 
        except (OSError, IOError):
            self.data1={'Time':[],'Date':[[],[]]}
            with open('DateFile.txt', mode='w', encoding='utf-8') as f:
                    json.dump(self.data1, f, indent=2)
            with open('DateFile.txt', 'r', encoding='utf-8') as f:
                self.data1 = json.load(f)
        
        self.first=1   
        
        
        try:
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = json.load(f) 
        except (OSError, IOError):
            self.NewMainDict={'SerialName':'COM1' # Адрес COM-порта в Windows "COMn" в Linux "ttySn"
                              ,'SerialSpeed':9600 # Скорость COM-порта 
                              ,'SerialTimeout':.1 # 
                              ,'PeriodDate':500 # Переиод считывания данных с COM-порта в мс 
                              ,'ICPCONAdres':'01' # Адрес устройства с которым соиденяемся                            
                             }
            with open('ConfigandDate.txt', mode='w', encoding='utf-8') as f:
                    json.dump(self.NewMainDict, f, indent=2)
            with open('ConfigandDate.txt', 'r', encoding='utf-8') as f:
                self.MainDict = json.load(f)
        f.close()
        self.counterSave=0
        
        try:
            self.ser = self.open_serial_port(self.MainDict['SerialName'])
        except: 
            print('System error')
        
    def open_serial_port(self,serial_name):
        try:
            s = serial.Serial(serial_name, self.MainDict['SerialSpeed'])
            s.timeout = self.MainDict['SerialTimeout'];
            print('Serial port',serial_name,'connected.')
        except serial.SerialException:
            print('Error opening the port ',serial_name)
            #sys.stderr.write("Error opening the port {}".format(serial_name))
            #sys.exit(1)
        return s
        
    def write_serial_port(self,s, cmd="#01"):
        data = b""
        CRC = format(sum([ord(ss) for ss in cmd]),'02X')
        cmd1 =  cmd.encode("iso-8859-15") + CRC.encode("iso-8859-15") + b"\r"

        i=0
        while b"\r" not in data:
            s.write(cmd1)
            data += s.read(60)
            s.flushInput()
            i+=1
            if i>=2:
                #print("Error connected device",cmd + ".")
                #pass
#                while "Error connected device" not in sys.__stdout__ :
                print("Error connected device",cmd + ".\r")  
                break
            else:
                pass
                #print(data)
        
        if data[-3:-1].decode("iso-8859-15") == format(sum([ord(ss) for ss in data[:-3].decode("iso-8859-15")]),'02X')[-2:]:
            data=data[1:-3].decode("iso-8859-15")
        else:
            if i<2:
                print("Error CRC. ")
            data='+0.0000+0.0000+0.0000+0.0000+0.0000+0.0000+0.0000+0.0000'
                      
        return data   


class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.pare=parent

        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
  

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.main_widget = QtWidgets.QWidget(self)
        
        VBoxMain = QtWidgets.QVBoxLayout(self.main_widget)
        
        self.ButtonStop = QtWidgets.QPushButton("Stop")
        self.ButtonStart = QtWidgets.QPushButton("Start")
        self.ButtonClear = QtWidgets.QPushButton("Clear")
        self.TextVIN = QtWidgets.QLineEdit()
        self.TextVIN.setReadOnly(1)
        self.TextVINaverage = QtWidgets.QLineEdit()
        self.TextVINaverage.setReadOnly(1)
        self.TextConsole = QtWidgets.QPlainTextEdit()
        self.TextConsole.setReadOnly(1)
        self.TextConsole.insertPlainText("asdasdas\n")
        self.TextConsole.insertPlainText("asdasdas\n")
        
       
        
        #self.TextConsole.print("uyoiuoi")
        VBoxText = QtWidgets.QVBoxLayout()
        VBoxText.addWidget(self.TextVIN)
        VBoxText.addWidget(self.TextVINaverage)
        
        VBoxButton = QtWidgets.QVBoxLayout()
        HBoxButtonStartStop = QtWidgets.QHBoxLayout()
        HBoxButtonStartStop.addWidget(self.ButtonStart)
        HBoxButtonStartStop.addWidget(self.ButtonStop)
        VBoxButton.addLayout(HBoxButtonStartStop)
        VBoxButton.addWidget(self.ButtonClear)
        
        HBoxWidget = QtWidgets.QHBoxLayout()
        HBoxWidget.addLayout(VBoxText)
        HBoxWidget.addLayout(VBoxButton)
               
        self.dc = MyMplCanvas(parent=self,width=7, height=5, dpi=100)
        VBoxMain.addLayout(HBoxWidget)
        VBoxMain.addWidget(self.dc)
        VBoxMain.addWidget(self.TextConsole)
        
        self.mythread = MyThread()
        self.mythread.start() 
        self.mythread.mysignal.connect(self.on_change, QtCore.Qt.QueuedConnection)
        #l1 = QtWidgets.QVBoxLayout(self.main_widget)
        
        self.ButtonStart.clicked.connect(self.on_start)
        self.ButtonStop.clicked.connect(self.on_stop)
        self.ButtonClear.clicked.connect(self.on_clear)
        self.ButtonClear.setDisabled(True)  
        
        #VBoxMain.addLayout(l1)
        #l1.addWidget(self.ButtonStop)
        #print(type(l1),"\n",type(VBoxMain),"\n",type(self.ButtonStop))
        
        #l1.addWidget(self.pushButton)
        #l.addWidget(l1)
        #l.addWidget(self.pushButton)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        #self.statusBar().showMessage("All hail matplotlib!", 2000)
        
    def on_change(self, s):
        self.TextVIN.setText(format(s['Date'][1][-1:][0], '+.03f')+" V")
        self.TextVINaverage.setText(format(s['Date'][0][-1:][0], '+.03f')+" Vср")
        
        if len(s['Date'][0])<=10:
            minlen=10
        else: 
            minlen=len(s['Date'][0])
        
        self.dc.axes.cla()
        self.dc.axes.grid(True)
        #self.dc.axes.plot(np.array(s['Time'][0]),np.array(s['Date'][0]),color = 'red')
        self.dc.axes.plot(np.arange(len(s['Date'][0])),np.array(s['Date'][0]),color = 'red')
        self.dc.axes.plot(np.arange(len(s['Date'][1])),np.array(s['Date'][1]),color = 'blue', alpha=0.3)
        self.dc.axes.set_xbound(lower=len(s['Date'][0])-minlen, upper=len(s['Date'][0]))            
        self.dc.axes.set_ybound(lower=min(s['Date'][0][-minlen:])-0.005, upper=max(s['Date'][0][-minlen:])+0.005)
        #self.
        self.dc.draw()
#        self.dc.update_figure()
#        self.TextConsole.insertPlainText(str(s['Time'][-1:][0])+" -- "+
#                                         format(s['Date'][0][-1:][0], '+.03f')+"Vср "+""+
#                                         format(s['Date'][1][-1:][0], '+.03f')+"V \n")
    
    def on_stop(self):
        self.mythread.runing=2
        self.ButtonClear.setDisabled(False) 
        
    def on_start(self):
        self.mythread.runing=1
        self.ButtonClear.setDisabled(True)
    
    def on_clear(self):
        self.mythread.runing=2
        #self.mythread.wait(1000)
        try:
            os.remove('DateFile.txt')
            os.remove('DateFile.csv')
        except:
            pass
            
        self.ButtonClear.setDisabled(True)
        #self.mythread.wait(500)
        self.mythread.CreateFileConfigandDate()
        #self.mythread.wait(500)
        self.mythread.runing=1
        
        
    
    def closeEvent(self, event):       
        print("kjljuohoi")
        self.mythread.runing=0
        self.hide()
        self.mythread.wait(2000)
        self.mythread.terminate()
                         
            
          
if __name__ == "__main__":
        
    stdout_old_target = sys.stdout
    app = QtWidgets.QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()
    sys.exit(app.exec_())
    
