import visa
import numpy as np
import time




class SpecAn(object):


    def __init__(self, _rm):
        self.address = 'GPIB0::5::INSTR'
        self._rm = _rm
        self.isConnected = False



    def connect(self):
        if not self.isConnected:
            try:
                self.specAn = self._rm.open_resource(self.address)
                self.specAn.timeout = 500
                self.isConnected = True
                print("connected to spectrum analyzer")
                self.queryParams()
            except visa.VisaIOError as e:
                print(e.args)


    def disconnect(self):
        if self.isConnected:

            self.specAn.close()
            self.isConnected = False
            print("disconnected from spectrum analyzer")


    def queryParams(self):
        # query instrument for initial parameters
        self.center = (float)(self.specAn.query('CF?;'))
        self.span = (float)(self.specAn.query('SP?;'))
        self.start = (float)(self.specAn.query('FA?;'))
        self.stop = (float)(self.specAn.query('FB?;'))
        self.sweepPoints = (int)(self.specAn.query('PO?;'))
        self.refLevel = (float)(self.specAn.query('RL?;'))
        self.gridScale = (float)(self.specAn.query('SD?;'))


    def setFreqParam(self, p1, p2, mode):
        if not self.isConnected:    return

        if mode == 'center':    # p1 is center frequency; p2 is span
            self.specAn.write('CF %fMHZ;' % (p1))    # center frequency
            self.specAn.write('SP %fMHZ;' % (p2))    # set span

        elif mode == 'start':   # p1 is start freq; p2 is stop freq
            self.specAn.write('FA %fMHZ;' % (p1))    # start freq
            self.specAn.write('FB %fMHZ;' % (p2))    # stop freq

        self.center = (float)(self.specAn.query('CF?;'))
        self.span = (float)(self.specAn.query('SP?;'))
        self.start = (float)(self.specAn.query('FA?;'))
        self.stop = (float)(self.specAn.query('FB?;'))


    def setAmpParam(self, ref, scale, atten, mode):
        if not self.isConnected:    return

        self.specAn.write('RL %fDBM;' % (ref))      # reference level
        self.refLevel = ref
        self.specAn.write('SD %fDB;' % (scale))     # grid scale
        self.gridScale = scale

        if mode == 'auto':
            self.specAn.write('ATA ON;')
        else:
            self.specAn.write('ATA OFF;')
            self.specAn.write('AT %fDB;' % (atten))     # attenutation


    def setRes(self, res, mode):
        if not self.isConnected:    return

        if mode == 'auto':
            self.specAn.write('RBA ON;')
        else:
            self.specAn.write('RBA OFF;')
            self.specAn.write('RB %fKHZ;' % (res))      # resolution bandwidth


    def setVideo(self, vid, mode):    
        if not self.isConnected:    return

        if mode == 'auto':
            self.specAn.write('VBA ON;')
        else:
            self.specAn.write('VBA OFF;')
            self.specAn.write('VB %fKHZ;' % (vid))      # video bandwidth


    def setSweepTime(self, time, mode):
        if not self.isConnected:    return

        if mode == 'auto':
            self.specAn.write('STA ON;')
        else:
            self.specAn.write('STA OFF;')
            self.specAn.write('ST %fMSEC;' % (time))        # sweep time


    def setSweepPoints(self, pts):
        if not self.isConnected:    return

        self.specAn.write('PO %d;' % (pts))     # number of data points
        self.sweepPoints = pts


    def getData(self):
        self.specAn.write('TDF ASC;')    # set ascii as data format
        Y = np.array(self.specAn.query_ascii_values('TRD? TRACE1;'))    # units of dBm
        interval = self.span / 1000000 / self.sweepPoints    # x interval between points
        temp = []
        for i in range(self.sweepPoints):
            temp.append((self.start / 1000000) + (i*interval))

        X = np.array(temp)        # units of MHz

        return (X, Y)

