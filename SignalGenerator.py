import visa


class SigGen(object):

    def __init__(self, _rm):
        self.address = 'GPIB0::7::INSTR'
        self._rm = _rm
        self.rfStatus = False
        self.freq = 0
        self.amp = 0
        self.isConnected = False


    def connect(self):
        if not self.isConnected:
            try:
                self.sigGen = self._rm.open_resource(self.address)
                self.isConnected = True
                print("connected to signal generator")
            except visa.VisaIOError as e:
                print(e.args)
                print(_rm.last_status)


    def changeFrequency(self, freq):
        self.freq = freq
        self.sigGen.write('FR%dMZ' % (freq)) # Change Frequency (MHz)


    def changeAmplitude(self, amp):
        self.amp = amp
        self.sigGen.write('AP%dDM' % (amp))  # Change Amplitude (dBm)


    def toggleRF(self):
        if self.rfStatus == False:
            self.rfStatus = True
            self.sigGen.write('R3')     # RF On
            return self.rfStatus

        else:
            self.rfStatus = False
            self.sigGen.write('R2')     # RF Off
            return self.rfStatus


    def disconnect(self):
        if self.isConnected:
            self.sigGen.write('R2')
            self.sigGen.write('GTL')
            self.sigGen.close()
            self.isConnected = False
            print("disconnected from signal generator")