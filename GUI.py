# Import PyQt wrappers
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QFontDatabase
from PyQt5 import uic
from PyQt5 import QtGui
import PyQt5

# import utility packages
import os
import sys
import time
import pyqtgraph as pg
import numpy as np
#from os.path import expanduser

import visa

from SignalGenerator import SigGen
from Oscilloscope import OScope
from SpectrumAnalyzer import SpecAn

_rm = visa.ResourceManager()

Ui_MainWindow, QtBaseClass = uic.loadUiType('GUI.ui')

oScope = OScope(_rm)
sigGen = SigGen(_rm)
specAn = SpecAn(_rm)



class WorkerScanOS(QObject):
    data = pyqtSignal(tuple)

    def __init__(self, ch):
        super().__init__()
        self.ch = ch
        self.isRunning = True


    def update_OS(self):
        # fetch oscilloscope graph data depending on mode
        while True:
            if self.isRunning:
                if oScope.state == 'run':
                    t = oScope.getData()
                    #time.sleep(0.05)
                    self.data.emit(t)

                elif oScope.state == 'single':
                    t = oScope.getData()
                    self.data.emit(t)
                    break

            else:
                break


    def stop(self):
        self.isRunning = False



class WorkerScanSA(QObject):
    data = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.isRunning = True


    def update_SA(self):
        # fetch spectrum analyzer graph data depending on mode
        while True:
            if self.isRunning:
                #if state == 'run':
                t = specAn.getData()
                self.data.emit(t)
                #elif state == 'single':
                #    t = specAn.getData()
                #    self.data.emit(t)
                #    break

            else:
                break


    def update_SA_single(self):
        t = specAn.getData()
        self.data.emit(t)
        self.isRunning = False



    def stop(self):
        self.isRunning = False




class App(QMainWindow):

    def __init__(self):
        super(App, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # connect ui to functions
        self.initSigGen()       # Signal Generator UI
        self.initOScope()       # Oscilloscope UI
        self.initSpecAn()       # Spectrum Analyzer UI


        self.os_graphOn = False
        self.sa_graphState = ''


    def initOScope(self):
        self.ui.pushButton_os_connect.clicked.connect(lambda: oScope.connect())
        self.ui.pushButton_os_disconnect.clicked.connect(lambda: oScope.disconnect())
        self.ui.pushButton_os_run.clicked.connect(lambda: self.runClicked())
        self.ui.pushButton_os_stop.clicked.connect(lambda: oScope.setAcquisitionState('stop'))
        self.ui.pushButton_os_singleRun.clicked.connect(lambda: self.singleClicked())
        self.ui.pushButton_os_mode_auto.clicked.connect(lambda: oScope.setTriggerMode('auto'))
        self.ui.pushButton_os_mode_normal.clicked.connect(lambda: oScope.setTriggerMode('normal'))
        self.initOScope_vertical()
        self.initOScope_horizontal()
        self.initOScope_channels()
        self.addPlot_OS()
        self.ui.pushButton_os_graph_start.clicked.connect(lambda: self.startGraph())
        self.ui.pushButton_os_graph_stop.clicked.connect(lambda: self.stopGraph())
        self.vertBars.sigRegionChanged.connect(lambda: self.getVertInterval())
        self.horBars.sigRegionChanged.connect(lambda: self.getHorInterval())


    def initOScope_vertical(self):
        # initialize position buttons
        self.ui.pushButton_os_vPos_up_1.clicked.connect(lambda: oScope.adjustVPos(1, 'U'))
        self.ui.pushButton_os_vPos_up_2.clicked.connect(lambda: oScope.adjustVPos(2, 'U'))
        self.ui.pushButton_os_vPos_up_3.clicked.connect(lambda: oScope.adjustVPos(3, 'U'))
        self.ui.pushButton_os_vPos_up_4.clicked.connect(lambda: oScope.adjustVPos(4, 'U'))
        self.ui.pushButton_os_vPos_down_1.clicked.connect(lambda: oScope.adjustVPos(1, 'D'))
        self.ui.pushButton_os_vPos_down_2.clicked.connect(lambda: oScope.adjustVPos(2, 'D'))
        self.ui.pushButton_os_vPos_down_3.clicked.connect(lambda: oScope.adjustVPos(3, 'D'))
        self.ui.pushButton_os_vPos_down_4.clicked.connect(lambda: oScope.adjustVPos(4, 'D'))

        #initialize scale settings
        self.ui.doubleSpinBox_os_vScale_1.valueChanged.connect(lambda: oScope.adjustVScales(1, 
                                                self.ui.doubleSpinBox_os_vScale_1.value()))
        self.ui.doubleSpinBox_os_vScale_1.valueChanged.connect(lambda: oScope.adjustVScales(2, 
                                                self.ui.doubleSpinBox_os_vScale_2.value()))
        self.ui.doubleSpinBox_os_vScale_1.valueChanged.connect(lambda: oScope.adjustVScales(3, 
                                                self.ui.doubleSpinBox_os_vScale_3.value()))
        self.ui.doubleSpinBox_os_vScale_1.valueChanged.connect(lambda: oScope.adjustVScales(4, 
                                                self.ui.doubleSpinBox_os_vScale_4.value()))


    def initOScope_horizontal(self):
        self.ui.pushButton_os_hPos_left.clicked.connect(lambda: oScope.adjustHPos('L'))
        self.ui.pushButton_os_hPos_right.clicked.connect(lambda: oScope.adjustHPos('R'))
        self.ui.doubleSpinBox_os_hScale.valueChanged.connect(lambda: oScope.adjustHScale( 
                                                self.ui.doubleSpinBox_os_hScale.value()))


    def initOScope_channels(self):
        self.ui.pushButton_os_disp_ch1.clicked.connect(lambda: oScope.changeChannel(1))
        self.ui.pushButton_os_disp_ch2.clicked.connect(lambda: oScope.changeChannel(2))
        self.ui.pushButton_os_disp_ch3.clicked.connect(lambda: oScope.changeChannel(3))
        self.ui.pushButton_os_disp_ch4.clicked.connect(lambda: oScope.changeChannel(4))


    def initSpecAn(self):
        self.ui.pushButton_sa_connect.clicked.connect(lambda: specAn.connect())
        self.ui.pushButton_sa_disconnect.clicked.connect(lambda: specAn.disconnect())
        self.ui.pushButton_sa_setParam.clicked.connect(lambda: self.setSpecAnParam())
        self.addPlot_SA()


    def initSigGen(self):
        self.ui.pushButton_sg_connect.clicked.connect(lambda: sigGen.connect())
        self.ui.pushButton_sg_disconnect.clicked.connect(lambda: sigGen.disconnect())
        self.ui.pushButton_sg_set.clicked.connect(lambda: self.setSigGenParam())
        self.ui.pushButton_sa_run.clicked.connect(lambda: self.scanSA('run'))
        self.ui.pushButton_sa_single.clicked.connect(lambda: self.scanSA('single'))
        self.ui.pushButton_sa_stop.clicked.connect(lambda: self.stopScanSA())


    def setSigGenParam(self):
        freq = self.ui.doubleSpinBox_sg_freq.value()
        amp = self.ui.doubleSpinBox_sg_amp.value()
        rfToggle = self.ui.radioButton_rf.isChecked()

        if sigGen.isConnected:
            sigGen.changeFrequency(freq)
            sigGen.changeAmplitude(amp)
            if rfToggle != sigGen.rfStatus:
                sigGen.toggleRF()


    def setSpecAnParam(self):
        # get parameter values
        center = self.ui.sa_centBand.value()
        span = self.ui.sa_span.value()
        start = self.ui.sa_start.value()
        stop = self.ui.sa_stop.value()

        ref = self.ui.sa_reference.value()
        gridScale = self.ui.sa_gridScale.value()
        atten = self.ui.sa_attenuation.value()

        res = self.ui.sa_resBand.value()
        video = self.ui.sa_videoBand.value()
        sweepTime = self.ui.sa_sweepTime.value()
        sweepPoints = self.ui.sa_sweepPoints.value()

        # send parameters to spectrum analyzer based on mode

        if self.ui.pushButton_sa_center_option.isChecked():
            specAn.setFreqParam(center, span, 'center')
        elif self.ui.pushButton_sa_start_option.isChecked():
            specAn.setFreqParam(start, stop, 'start')


        if self.ui.sa_attenuation_auto.isChecked():
            specAn.setAmpParam(ref, gridScale, atten, 'auto')
        else:
            specAn.setAmpParam(ref, gridScale, atten, 'manual')


        if self.ui.sa_resBand_auto.isChecked():
            specAn.setRes(res, 'auto')
        else:
            specAn.setRes(res, 'manual')

        if self.ui.sa_videoBand_auto.isChecked():
            specAn.setVideo(video, 'auto')
        else:
            specAn.setVideo(video, 'manual')

        if self.ui.sa_sweepTime_auto.isChecked():
            specAn.setSweepTime(sweepTime, 'auto')
        else:
            specAn.setSweepTime(sweepTime, 'manual')

        specAn.setSweepPoints(sweepPoints)


    def scanSA(self, mode):
        if not specAn.isConnected or not self.sa_graphState == '':      return

        self.thread_sa = QThread()
        self.worker_sa = WorkerScanSA()
        self.worker_sa.data[tuple].connect(self.updateGraph_SA)
        self.worker_sa.moveToThread(self.thread_sa)

        if mode == 'run':
            self.thread_sa.started.connect(self.worker_sa.update_SA)
            self.thread_sa.start()
            self.ui.pushButton_sa_single.setEnabled(False)
            self.ui.pushButton_sa_setParam.setEnabled(False)
            self.sa_graphState = 'run'

        elif mode == 'single':
            self.thread_sa.started.connect(self.worker_sa.update_SA_single)
            self.thread_sa.start()
            self.sa_graphState = 'single'
            self.stopScanSA()


    def stopScanSA(self):
        if not specAn.isConnected or self.sa_graphState == '':      return

        self.sa_graphState = ''

        self.worker_sa.stop()
        self.thread_sa.quit()
        self.thread_sa.wait()

        self.ui.pushButton_sa_single.setEnabled(True)
        self.ui.pushButton_sa_setParam.setEnabled(True)




    def runClicked(self):
        oScope.setAcquisitionState('run')
        if self.os_graphOn:
            self.worker.update_OS


    def singleClicked(self):
        oScope.setAcquisitionState('single')
        if self.os_graphOn:
            self.worker.update_OS


    def getVertInterval(self):
        t = self.vertBars.getRegion()
        interval = (float) (t[1] - t[0])*1000000000
        _str = '%f ns' % (interval)

        self.ui.lineEdit_os_vertInterval.setText(_str)


    def getHorInterval(self):
        t = self.horBars.getRegion()
        interval = (float) (t[1] - t[0])
        _str = '%f V' % (interval)

        self.ui.lineEdit_os_horInterval.setText(_str)


    def startGraph(self):
        if not oScope.isConnected or self.os_graphOn or oScope.state == '':  return

        # add separate thread for graph to update in
        self.thread = QThread()
        self.worker = WorkerScanOS(oScope.currChan)
        self.worker.data[tuple].connect(self.updateGraph_OS)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.update_OS)
        self.thread.start()
        self.os_graphOn = True

        # disable certain buttons when graph is running
        self.disableOSButtons()



    def stopGraph(self):
        if not oScope.isConnected or not self.os_graphOn:  return
        self.os_graphOn = False

        # enable certain buttons when graph is not running
        self.enableOSButtons()


        # stop graph thread
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()


    def disableOSButtons(self):
        self.ui.pushButton_os_run.setEnabled(False)
        self.ui.pushButton_os_stop.setEnabled(False)
        self.ui.pushButton_os_singleRun.setEnabled(False)
        self.ui.pushButton_os_disp_ch1.setEnabled(False)
        self.ui.pushButton_os_disp_ch2.setEnabled(False)
        self.ui.pushButton_os_disp_ch3.setEnabled(False)
        self.ui.pushButton_os_disp_ch4.setEnabled(False)
        self.ui.pushButton_os_mode_auto.setEnabled(False)
        self.ui.pushButton_os_mode_normal.setEnabled(False)


    def enableOSButtons(self):
        self.ui.pushButton_os_run.setEnabled(True)
        self.ui.pushButton_os_stop.setEnabled(True)
        self.ui.pushButton_os_singleRun.setEnabled(True)
        self.ui.pushButton_os_disp_ch1.setEnabled(True)
        self.ui.pushButton_os_disp_ch2.setEnabled(True)
        self.ui.pushButton_os_disp_ch3.setEnabled(True)
        self.ui.pushButton_os_disp_ch4.setEnabled(True)
        self.ui.pushButton_os_mode_auto.setEnabled(True)
        self.ui.pushButton_os_mode_normal.setEnabled(True)



    @pyqtSlot(tuple)
    def updateGraph_OS(self, t):
        X = t[0]
        Y = t[1]

        #self.ui.os_plot.setRange(xRange=[np.amin(X), np.amax(X)])
        self.ui.os_plot.removeItem(self.chPlot)
        self.chPlot = self.ui.os_plot.plot(X, Y, pen=self.ch1Pen)


    @pyqtSlot(tuple)
    def updateGraph_SA(self, t):
        X = t[0]
        Y = t[1]

        xMin = specAn.start / 1000000   # units of MHz
        xMax = specAn.stop / 1000000

        yMax = specAn.refLevel
        yMin = yMax - specAn.gridScale * 10
        

        self.ui.sa_plot.removeItem(self.saPlot)
        self.saPlot = self.ui.sa_plot.plot(X, Y, pen=self.sa_pen)
        # set plot range limits to specified parameters
        self.ui.sa_plot.setRange(xRange=[xMin, xMax], yRange=[yMin, yMax], padding=0.02)



    def addPlot_OS(self):
        # setup plot settings
        labelStyle = {'color': '#000', 'font-size': '14pt'}
        axispen = pg.mkPen(color='#000', fontsize='14pt')
        axisfont = QtGui.QFont()
        axisfont.setFamily('Cambria')
        axisfont.setPointSize(22)
        axisfont.setBold(True)

        self.ui.os_plot.setBackground(background=None)
        self.ui.os_plot.showGrid(x=True, y=True, alpha=0.25)
        self.ui.os_plot.setLabel(
            'bottom', text='Time (ns)', units=None,  **labelStyle)
        self.ui.os_plot.setLabel('left', 'Voltage', 'V', **labelStyle)

        self.ui.os_plot.plotItem.getAxis('bottom').setPen(axispen)
        self.ui.os_plot.plotItem.getAxis('bottom').setFont(axisfont)
        self.ui.os_plot.plotItem.getAxis('left').setStyle(tickFont=axisfont)
        self.ui.os_plot.plotItem.getAxis('left').setPen(axispen)

        self.ui.os_plot.plotItem.getAxis('top').setPen(axispen)
        self.ui.os_plot.plotItem.getAxis('right').setPen(axispen)
        self.ui.os_plot.plotItem.getAxis('top').setTicks([])
        self.ui.os_plot.plotItem.getAxis('right').setTicks([])

        self.ui.os_plot.plotItem.showAxis('right', show=True)
        self.ui.os_plot.plotItem.showAxis('left', show=True)
        self.ui.os_plot.plotItem.showAxis('top', show=True)
        self.ui.os_plot.plotItem.showAxis('bottom', show=True)

        self.ch1Pen = pg.mkPen(color='r', width=1)
        self.ch2Pen = pg.mkPen(color='g', width=1)
        self.ch3Pen = pg.mkPen(color='b', width=1)
        self.ch4Pen = pg.mkPen(color='m', width=1)
        self.clearBrush = pg.mkBrush(None)
        self.bars = pg.mkPen(color='k', width=1)

        self.chPlot = self.ui.os_plot.plot([], [], pen=self.ch1Pen, name='CH1')

        self.vertBars = pg.LinearRegionItem([0,0],brush=self.clearBrush)
        self.horBars = pg.LinearRegionItem([0,0],orientation=pg.LinearRegionItem.Horizontal,
                                            brush=self.clearBrush)

        self.vertBars.lines[0].setPen(self.bars)
        self.vertBars.lines[1].setPen(self.bars)
        #self.vertBars.setHoverBrush(None)
        self.horBars.lines[0].setPen(self.bars)
        self.horBars.lines[1].setPen(self.bars)
        #self.horBars.setHoverBrush(None)

        self.ui.os_plot.addItem(self.vertBars)
        self.ui.os_plot.addItem(self.horBars)


    def addPlot_SA(self):
        # setup plot settings
        labelStyle = {'color': '#000', 'font-size': '14pt'}
        axispen = pg.mkPen(color='#000', fontsize='14pt')
        axisfont = QtGui.QFont()
        axisfont.setFamily('Cambria')
        axisfont.setPointSize(22)
        axisfont.setBold(True)

        self.ui.sa_plot.setBackground(background=None)
        self.ui.sa_plot.showGrid(x=True, y=True, alpha=0.25)
        self.ui.sa_plot.setLabel(
            'bottom', text='Frequency (MHz)', units=None,  **labelStyle)
        self.ui.sa_plot.setLabel('left', 'Amplitude', 'dBm', **labelStyle)

        self.ui.sa_plot.plotItem.getAxis('bottom').setPen(axispen)
        self.ui.sa_plot.plotItem.getAxis('bottom').setFont(axisfont)
        self.ui.sa_plot.plotItem.getAxis('left').setStyle(tickFont=axisfont)
        self.ui.sa_plot.plotItem.getAxis('left').setPen(axispen)

        self.ui.sa_plot.plotItem.getAxis('top').setPen(axispen)
        self.ui.sa_plot.plotItem.getAxis('right').setPen(axispen)
        self.ui.sa_plot.plotItem.getAxis('top').setTicks([])
        self.ui.sa_plot.plotItem.getAxis('right').setTicks([])

        self.ui.sa_plot.plotItem.showAxis('right', show=True)
        self.ui.sa_plot.plotItem.showAxis('left', show=True)
        self.ui.sa_plot.plotItem.showAxis('top', show=True)
        self.ui.sa_plot.plotItem.showAxis('bottom', show=True)

        self.sa_pen = pg.mkPen(color='r', width=1)

        self.saPlot = self.ui.sa_plot.plot([], [], pen=self.sa_pen, name='Spectrum Analyzer')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

