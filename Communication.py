import serial, time

ser = serial.Serial("/dev/ttyUSB0", 57600, timeout=1, xonxoff=1)
ser.write("*RST\r\n".encode('utf-8'))
ser.write("*CLS\r\n".encode('utf-8'))



def measure(channels):
    writeString = "CONF:TEMP TC, T,(@%s)\r\n" % (channels, )
    ser.write(writeString.encode('utf-8'))
    ser.write("READ?\r\n".encode('utf-8'))
    InstrumentReturn = ser.readline()
    try:
        bbb = map(float, InstrumentReturn.split(","))
    except:
        bbb = [-999, -999]
        ser.write("*RST\r\n".encode("utf-8"))
        time.sleep(1.0)
        ser.write("*CLS\r\n".encode("utf-8"))
        time.sleep(1.0)
    return bbb

def temperature(channels):
    print(channels)
    writeString = "CONF:TEMP TC, T,(@%s)\r\n" % (channels, )
    ser.write(writeString.encode('utf-8'))
    ser.write("READ?\r\n".encode('utf-8'))
    InstrumentReturn = ser.readline()
    try:
        bbb = map(float, InstrumentReturn.split(","))
    except:
        bbb = [-999, -999]
        ser.write("*RST\r\n".encode('utf-8'))
        time.sleep(1.0)
        ser.write("*CLS\r\n".encode('utf-8'))
        time.sleep(1.0)
    return bbb

def flowmeas(channels):
    writeString = "CONF:VOLT:DC 10,0.00001, (@%s)\r\n" % (channels, )
    print(writeString)
    ser.write(writeString.encode('utf-8'))
    ser.write("READ?\r\n".encode("utf-8"))
    InstrumentReturn = ser.readline().decode("utf-8")
    print(InstrumentReturn)
    try:
    	bbb = list(map(float, InstrumentReturn.split(",")))
    except:
        bbb = [-999, -999]
        ser.write("*RST\r\n".encode("utf-8"))
        time.sleep(1.0)
        ser.write("*CLS\r\n".encode("utf-8"))
        time.sleep(1.0)
    
    return bbb
