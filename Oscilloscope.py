import visa
import numpy as np
import pyqtgraph as pg
import time




class OScope(object):

    def __init__(self, _rm):
        self.address = 'GPIB0::3::INSTR'
        self._rm = _rm
        self.isConnected = False
        self.vPos = [0, 0, 0, 0]
        self.hPos = 50
        self.vScales = [0, 0, 0, 0]
        self.hScale = 1
        self.state = ''
        self.chnls = [True, False, False, False]
        self.currChan = 1


    def connect(self):
        if not self.isConnected:
            try:
                self.oScope = self._rm.open_resource(self.address)
                self.oScope.timeout = 500
                self.isConnected = True
                print("connected to oscilloscope")
                self.queryParams()
            except visa.VisaIOError as e:
                print(e.args)


    def disconnect(self):
        if self.isConnected:
            self.oScope.write('R2')
            self.oScope.write('GTL')
            self.oScope.close()
            self.isConnected = False
            print("disconnected from oscilloscope")


    def queryParams(self):
        for ch in range(1, 5):
            self.vPos[ch - 1] = float(self.oScope.query('CH%d:POSition?' % (ch)))
            self.vScales[ch - 1] = float(self.oScope.query('CH%d:SCAle?' % (ch)))
        self.hPos = float(self.oScope.query('HORizontal:POSition?'))
        self.hScale = float(self.oScope.query('HORizontal:SCAle?'))


    def write(self, message):
        N = self.oScope.write(message)
        return N


    def query(self, message):
        N = self.oScope.query(message)
        return N


    def setAcquisitionState(self, state):
        if not self.isConnected:    return

        self.state = state

        if state == "run":
            self.oScope.write('ACQuire:STATE RUN')  # turn on acquisition
            self.oScope.write('ACQuire:STOPAfter RUNStop')  # set continuous acquisition
        elif state == "single":
            self.oScope.write('ACQuire:STATE RUN')
            self.oScope.write('ACQuire:STOPAfter SEQuence')     # set single acquisition
        elif state == "stop":
            self.oScope.write('ACQuire:STATE STOP')     # stop aquisition


    def setTriggerMode(self, mode):
        if not self.isConnected:    return

        if mode == "auto":
            self.oScope.write('TRIGger:A:MODe AUTO')   # sets trigger mode to auto
        elif mode == "normal":
            self.oScope.write('TRIGger:A:MODe NORMal')
        
        return self.oScope.query('TRIGger:A:MODe?')


    def adjustHPos(self, _dir):
        if not self.isConnected:    return

        if self.hPos > 1 and self.hPos < 98:
            if _dir == 'L':
                self.hPos -= 1
            elif _dir == 'R':
                self.hPos += 1
            self.oScope.write('HORizontal:POSition %d' % (self.hPos))


    def adjustVPos(self, ch, _dir):
        if not self.isConnected:    return

        if self.vPos[ch - 1] > -7.9 and self.vPos[ch - 1] < 7.9:
            if _dir == 'U':
                self.vPos[ch - 1] += 0.1
            elif _dir == 'D':
                self.vPos[ch - 1] -= 0.1
            self.oScope.write('CH%d:POSition %f' % (ch, self.vPos[ch - 1]))


    def adjustVScales(self, ch, scale):
        if not self.isConnected:    return

        self.vScales[ch - 1] = scale
        if self.vScales[ch - 1] > 0.001 and self.vScales[ch - 1] < 10:
            self.oScope.write('CH%d:SCAle %fE+00' % (ch, self.vScales[ch - 1]))


    def adjustHScale(self, scale):
        if not self.isConnected:    return

        self.hScale = scale
        if self.hScale > 0.2 and self.hScale < 40000000000:
            self.oScope.write('HORizontal:SCAle %fE-9' % (self.hScale))


    def changeChannel(self, ch):
        self.currChan = ch


    def getData(self):
        if not self.isConnected: return

        try:
            # query graph arguments from the oscilloscope
            self.xUnit = (self.oScope.query('WFMOutpre:XUNit?'))
            self.xIncr = (float)(self.oScope.query('WFMOutpre:XINcr?'))
            self.xZero = (float)(self.oScope.query('WFMOutpre:XZEro?'))
            self.yUnit = (self.oScope.query('WFMOutpre:YUNit?'))
            self.yMult = (float)(self.oScope.query('WFMOutpre:YMUlt?'))
            self.yOff = (float)(self.oScope.query('WFMOutpre:YOFf?'))
            self.yZero = (float)(self.oScope.query('WFMOutpre:YZEro?'))
            self.centerPt = (float)(self.oScope.query('WFMOutpre:PT_OFF?'))
            self.dataLength = (float)(self.oScope.query('HORizontal:RECOrdlength?'))
            self.oScope.write('DATa:STARt 1')
            self.oScope.write('DATa:ENCdg ASCIi')

            if self.state == 'stop':
                return

            # query graph data
            self.oScope.write('DATa:SOUrce CH%d' % (self.currChan))
            Y = np.array(self.oScope.query_ascii_values('CURVe?'))
            Y = np.multiply(Y, self.yMult, out=Y, casting='unsafe')
            X = np.arange(self.dataLength)
            X -= self.centerPt
            X *=self.xIncr

            return (X, Y)

        except visa.VisaIOError as e:
            #print(e.args)

            return self.getData()