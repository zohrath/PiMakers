import serial, time

def temperature(ser, channels):
    writeString = "CONF:TEMP TC, T,(@%s)\r\n" % (channels, )
    print(writeString)
    ser.write(writeString.encode())
    ser.write("READ?\r\n".encode())
    InstrumentReturn = ser.readline()
    print(InstrumentReturn)
    InstrumentReturn = InstrumentReturn.decode()
    bbb = list(map(float, InstrumentReturn.split(",")))
    ser.write("*CLS\r\n".encode())
    ser.write("*RST\r\n".encode())
    return bbb

def voltDC(ser, channels):
    writeString = "CONF:VOLT:DC 10,0.00001, (@%s)\r\n" % (channels, )
    print(writeString)
    ser.write(writeString.encode())
    ser.write("READ?\r\n".encode())
    InstrumentReturn = ser.readline()
    print(InstrumentReturn)
    InstrumentReturn = InstrumentReturn.decode()
    bbb = list(map(float, InstrumentReturn.split(",")))
    ser.write("*CLS\r\n".encode())
    ser.write("*RST\r\n".encode())
    return bbb
    

    

