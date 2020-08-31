import visa

if __name__ == '__main__':
    
    rm = visa.ResourceManager()
    res = rm.list_resources()
    print(res)

    # Signal Generator Test #
    # --------------------------------------------------------------- #
    """
    sigGen = rm.open_resource('GPIB0::7::INSTR')
    print(sigGen)

    sigGen.write('FR10MZ')      # Change Frequency (MHz)
    sigGen.write('AP5DM')       # Change Amplitude (dBm)
    #sigGen.write('R2')          # RF Off
    #sigGen.write('R3')          # RF On
    #sigGen.write('DCL')         # Sets amp and freq to default
    #sigGen.write('GTL')         # End remote operation

    sigGen.close()


    # Oscilloscope Test #
    # --------------------------------------------------------------- #
    oScope = rm.open_resource('GPIB0::3::INSTR')
    print(oScope)

    oScope.write('HEADer ON')

    print(oScope.query('*IDN?'))    # Query oscilloscope identification code
    print(oScope.query('ACQuire?')) # Query all acquisition parameters
    print(oScope.query('CURSor?'))  # Query cursor all settings

    oScope.write('DATa:SOUrce CH1')
    oScope.write('DATa:STARt 1')
    oScope.write('DATa:STOP 500')
    oScope.write('DATa:ENCdg ASCIi')
    print(oScope.query('WFMOutpre?'))
    print(oScope.query('WFMOutpre:PT_Fmt?'))
    print(oScope.query('HORizontal:RECOrdlength?'))
    print(oScope.query('WFMOutpre:BYT_Nr?'))
    print(oScope.query('WFMOutpre:XUNit?'))
    oScope.write('HEADer OFF')
    print(oScope.query_ascii_values('CURVe?'))


    oScope.close()
    """


    # Spectrum Analyzer Test #
    # --------------------------------------------------------------- #
    specAn = rm.open_resource('GPIB0::5::INSTR')
    print(specAn.query('*IDN?'))

    specAn.write('TDF ASC;')
    print(specAn.query_ascii_values('TRD? TRACE1;'))
    print(specAn.query('SP?;'))

    specAn.close()

    print('closed connection')