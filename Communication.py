import serial, time

    ser = serial.Serial("/dev/ttyUSB0", 57600, timeout=1, xonxoff=1)
    ser.write("*RST\r\n")
    ser.write("*CLS\r\n")



def measure():

    ser.write("CONF:VOLT:DC 10,0.00001,(@101:118\r\n")
    ser.write("READ?\r\n")
    InstrumentReturn = ser.readline()
    try:
        bbb = map(float, InstrumentReturn.split(","))
    except:
        bbb = [-999, -999]
        ser.write("*RST\r\n")
        time.sleep(1.0)
        ser.write("*CLS\r\n")
        time.sleep(1.0)
    return bbb

def temperature(channels):
    ser.write("CONF:TEMP TC, T,(@%s\r\n") % (channels, )
    ser.write("READ?\r\n")
    InstrumentReturn = ser.readline()
    try:
        bbb = map(float, InstrumentReturn.split(","))
    except:
        bbb = [-999, -999]
        ser.write("*RST\r\n")
        time.sleep(1.0)
        ser.write("*CLS\r\n")
        time.sleep(1.0)
    return bbb

def flowmeas():
    ser.write("CONF:VOLT:DC 10,0.00001,(@201:209\r\n")
    ser.write("READ?\r\n")
    InstrumentReturn = ser.readline()
    try:
        bbb = map(float, InstrumentReturn.split(","))
    except:
        bbb = [-999, -999]
        ser.write("*RST\r\n")
        time.sleep(1.0)
        ser.write("*CLS\r\n")
        time.sleep(1.0)
    return bbb
