# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 12:24:22 2017

@author: Dima
"""
import os
import random
import datetime
import sys
import json
import serial
import numpy as np
from time import strftime,localtime,strptime,time
#import matplotlib
# Make sure that we are using QT5
 #matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets



#from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange, date2num,datestr2num, DateFormatter

#progname = os.path.basename(sys.argv[0])
#progversion = "0.1"
class Profiler(object):
    def __enter__(self):
        self._startTime = time()
         
    def __exit__(self, type, value, traceback):
        print ("Elapsed time: {:.3f} sec".format(time() - self._startTime))



class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(dict)
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.runing =1
            
    def run(self):
        self.CreateFileConfigandDate()
        
        while 1:
            self.msleep(self.MainDict['PeriodDate'])  # "Засыпаем" на PeriodDate милисекунды
            if self.runing==1:
                with Profiler() as p:            
                    self.data_to_send = self.write_serial_port(self.ser, "#"+self.MainDict['ICPCONAdres'])
                
                    self.dataFloat =[float(self.data_to_send[i:i+7]) for i in range(56) if i%7==0]
                    
                    self.dataFloat[5]-=0.318 # Поправка измерения питающего напряжения мВ
                    
                    self.data1['Time'].append(strftime("%H:%M:%S",localtime()))
                    
                    if self.first==1: # Поверка на первый запуск приложения 
                        self.Date_average=self.dataFloat[0] # Назначить среденее значение первым считаным значением 
                        self.Vsup_average=self.dataFloat[5] # Назначить среденее значение питающего напряжения первым считаным значением 
                        self.first=0
                    else:
                        if (self.dataFloat[0]>self.Date_average*1.3)|(self.dataFloat[0]<self.Date_average*0.7) : # Отбрасывание значений превышаюших среднее в 1,5раз фильтр помех 
                            pass
                        else:
                            self.Date_average=self.Date_average + (self.dataFloat[0] - self.Date_average) / 20.0 # Расчет среднего значения по двацати прошлым значениям  
                        
                        if self.dataFloat[5]<self.Vsup_average*0.8: # Отбрасывание значений питающего напряжения меньше среднего 0,8раз фильтр помех 
                            pass
                        else:
                            self.Vsup_average=self.Vsup_average + (self.dataFloat[5] - self.Vsup_average) / 20.0 # Расчет среднего значения питающего напряжения по двацати прошлым значениям  
                
               
                    
                    self.data1['Date'][0].append(round(self.Date_average,3)) 
                    self.data1['Date'][1].append(self.dataFloat[0])
                    self.data1['Vsup'][0].append(round(self.Vsup_average,3)) 
                    self.data1['Vsup'][1].append(self.dataFloat[5])
                    
        #            with open('DateFile.csv', 'a') as DateFile:
        #                DateFile.write(str(self.data1['Time'][-1:][0])+","+
        #                                   format(self.data1['Date'][0][-1:][0], '+.03f')+","+
        #                                   format(self.data1['Date'][1][-1:][0], '+.03f')+"\n")   
        #            DateFile.close()
        
               
                     
                    
                        
                    if self.counterSave>20:
                        with open('DateFile.txt', mode='w', encoding='utf-8') as f:
                            json.dump(self.data1, f, indent=2)
                        f.close()
                        
                        
                        with open('DateFile.csv', 'a') as DateFile:
                            lendata=len(self.data1['Time'])
                            
                            for i in range(-21,0,1):
#                                print(self.data1['Time'][lendata+i])
                                DateFile.write(self.data1['Time'][lendata+i]+","+
                                                   format(self.data1['Date'][0][lendata+i], '+.03f')+","+
                                                   format(self.data1['Date'][1][lendata+i], '+.03f')+","+
                                                   format(self.data1['Vsup'][0][lendata+i], '+.03f')+","+
                                                   format(self.data1['Vsup'][1][lendata+i], '+.03f')+"\n")
                            
                        DateFile.close()
                        
                        
                        self.counterSave=0
                    
                    self.counterSave+=1      
                    
    #                print(self.data_to_send)
                    
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
            self.data1={'Time':[],'Date':[[],[]],'Vsup':[[],[]]}
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


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
      
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("PyQtWeightMetreDCON")

        self.main_widget = QtWidgets.QWidget(self)
        
        self.figVIN = Figure(figsize=(8, 5), dpi=100)
        self.figVsup = Figure(figsize=(8, 5), dpi=100)
        self.canvasVIN = FigureCanvas(self.figVIN)
        self.canvasVIN.setParent(self.main_widget)
        self.canvasVsup = FigureCanvas(self.figVsup)
        self.axesVIN = self.figVIN.add_subplot(111)
        self.axesVsup = self.figVsup.add_subplot(111)
        self.figVIN.subplots_adjust(right=0.98,left=0.07)
        self.figVsup.subplots_adjust(right=0.98,left=0.07)
        
     
        VBoxMain = QtWidgets.QVBoxLayout(self.main_widget)
        
        self.ButtonStop = QtWidgets.QPushButton("Stop")
        self.ButtonStart = QtWidgets.QPushButton("Start")
        self.ButtonClear = QtWidgets.QPushButton("Clear")
        self.TextVIN = QtWidgets.QLineEdit()
        self.TextVIN.setReadOnly(1)
        self.TextVINaverage = QtWidgets.QLineEdit()
        self.TextVINaverage.setReadOnly(1)
        self.TextVsup = QtWidgets.QLineEdit()
        self.TextVsup.setReadOnly(1)
        self.TextVsupaverage = QtWidgets.QLineEdit()
        self.TextVsupaverage.setReadOnly(1)
        self.TextConsole = QtWidgets.QPlainTextEdit()
        self.TextConsole.setReadOnly(1)
        self.TextConsole.insertPlainText("asdasdas\n")      
        
        VBoxTextVIN = QtWidgets.QVBoxLayout()
        VBoxTextVIN.addWidget(self.TextVIN)
        VBoxTextVIN.addWidget(self.TextVINaverage)
        
        VBoxTextVsup = QtWidgets.QVBoxLayout()
        VBoxTextVsup.addWidget(self.TextVsup)
        VBoxTextVsup.addWidget(self.TextVsupaverage)
        
        HBoxText = QtWidgets.QHBoxLayout()
        HBoxText.addLayout(VBoxTextVIN)
        HBoxText.addLayout(VBoxTextVsup)
        
        
        VBoxButton = QtWidgets.QVBoxLayout()
        HBoxButtonStartStop = QtWidgets.QHBoxLayout()
        HBoxButtonStartStop.addWidget(self.ButtonStart)
        HBoxButtonStartStop.addWidget(self.ButtonStop)
        VBoxButton.addLayout(HBoxButtonStartStop)
        VBoxButton.addWidget(self.ButtonClear)
        
        HBoxWidget = QtWidgets.QHBoxLayout()
        HBoxWidget.addLayout(HBoxText)
        HBoxWidget.addLayout(VBoxButton)
               
          
        self.toolbar = NavigationToolbar(self.canvasVIN,self.main_widget)
        self.toolbar2 = NavigationToolbar(self.canvasVsup,self.main_widget)
        
        VBoxMain.addLayout(HBoxWidget)
        VBoxMain.addWidget(self.canvasVIN)
        VBoxMain.addWidget(self.toolbar)
        VBoxMain.addWidget(self.canvasVsup)
        VBoxMain.addWidget(self.toolbar2)
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
#        with Profiler() as p:
        self.TextVIN.setText(format(s['Date'][1][-1:][0], '+.03f')+" V")
        self.TextVINaverage.setText(format(s['Date'][0][-1:][0], '+.03f')+" Vср")
        self.TextVsup.setText(format(s['Vsup'][1][-1:][0], '+.03f')+" V sup")
        self.TextVsupaverage.setText(format(s['Vsup'][0][-1:][0], '+.03f')+" Vср sup")
        
#        if len(s['Date'][0])<=10:
#            minlen=10
#        else: 
#            minlen=len(s['Date'][0])
        
        self.axesVIN.cla()
        self.axesVIN.grid(True)
        self.axesVsup.axes.cla()
        self.axesVsup.axes.grid(True)
        
       
    
#        converted_dates = map(datetime.datetime.strptime, s['Time'], len(s['Time'])*["%H:%M:%S"])
        x_axis =[datetime.datetime.strptime(s['Time'][i],"%H:%M:%S")for i in range(len(s['Time']))]
#        x_axis = [strptime(d, "%H:%M:%S") for d in s['Time']]
#        xs = strptime(s['Time'])
        formatter = DateFormatter('%H:%M:%S')

#        x = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(12)]
#        y = [i+random.gauss(0,1) for i,_ in enumerate(x)]
#        print(s['Time'],x_axis)
#        
#        # plot
#        self.axesVIN.plot(x,y)
#        # beautify the x-labels
#        self.figVIN.autofmt_xdate()

        self.axesVIN.plot(x_axis,np.array(s['Date'][0]),color = 'red',label="VIN")
        self.axesVIN.plot(x_axis,np.array(s['Date'][1]),color = 'blue', alpha=0.3,)
        
#        VINlowerY=min(s['Date'][0][-5000:])-0.01
#        VINupperY=max(s['Date'][0][-5000:])+0.01
#        
#        VINlowerX=x_axis[0]
#        VINupperX=x_axis[-1:][0]
        
#        print(VINlowerY,VINlowerY,(VINupperY-VINlowerY)/10,VINlowerX,VINupperX,(VINupperX-VINlowerX)/10)
        self.axesVIN.set_ybound(lower=min(s['Date'][0][-5000:])-0.02, upper=max(s['Date'][0][-5000:])+0.02)
#        self.figVIN.autofmt_xdate(rotation=10)
        self.axesVIN.xaxis.set_major_formatter(formatter)
#        self.axesVIN.set_yticks(np.arange(VINlowerY, VINupperY, round(((VINupperY-VINlowerY)/10),3)))
#        try:
#            self.axesVIN.set_xticks(np.arange(VINlowerX, VINupperX, (VINupperX-VINlowerX)/10))
#        except:
#            pass

#        self.axesVIN.plot(np.arange(len(s['Date'][0])),np.array(s['Date'][0]),color = 'red',label="VIN")
#        self.axesVIN.plot(np.arange(len(s['Date'][1])),np.array(s['Date'][1]),color = 'blue', alpha=0.3,)
#        self.axesVIN.set_xbound(lower=len(s['Date'][0])-minlen, upper=len(s['Date'][0]))            
#        self.axesVIN.set_ybound(lower=min(s['Date'][0][-1000:])-0.01, upper=max(s['Date'][0][-1000:])+0.01)
#        self.figVIN.autofmt_xdate(rotation=90)
#
#        
        self.axesVsup.plot(x_axis,np.array(s['Vsup'][0]),color = 'red',label="Vsup")
        self.axesVsup.plot(x_axis,np.array(s['Vsup'][1]),color = 'blue',alpha=0.3)
#            self.axesVsup.set_xbound(lower=len(s['Vsup'][0])-minlen, upper=len(s['Vsup'][0]))            
        self.axesVsup.set_ybound(lower=min(s['Vsup'][0][-5000:])-0.01, upper=max(s['Vsup'][0][-5000:])+0.01)
#        self.figVsup.autofmt_xdate(rotation=10)
        self.axesVsup.xaxis.set_major_formatter(formatter)
    
        self.canvasVIN.draw()
        self.canvasVsup.draw()
    
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
#        print("kjljuohoi")
        self.mythread.runing=0
        self.hide()
        self.mythread.wait(4000)
        self.mythread.terminate()
                         
            
          
if __name__ == "__main__":
        
    try:
        stdout_old_target = sys.stdout
        app = QtWidgets.QApplication(sys.argv)
        window = ApplicationWindow()
        window.show()
        sys.exit(app.exec_())
    except:
        window.mythread.terminate()
        
