
import time
import serial

class SerialComm:
  def __init__(this, port, baudrate):
    this.port = port;
    this.baudrate = baudrate;
    this.is_connected = False;
        
    try:
      this.connection = serial.Serial(this.port, this.baudrate, timeout=1);
      this.is_connected = True;
    except Exception as e:
      print(f"X[{time.process_time():08.3f}] SER/INIT-{this.port}: {e}");
      
  def read(this):
    """
    Reads data from the serial port and returns it.
    Handle possible exceptions and data processing here.
    """
    try:
      data = this.connection.readline().decode('utf-8').strip();
      return data;
    except Exception as e:
      print(f"X[{time.process_time():08.3f}] SER/READ-{this.port}: {e}");
      return None;
      
  # def write(this, data):
  #   """
  #   Writes data to the serial port.
  #   """
  #   try:
  #     this.connection.write(data.encode('utf-8'))
  #   except Exception as e:
  #     print(f"Error writing to {this.port}: {e}")
    
  def close(this):
    """
    Closes the serial port connection.
    """
    if this.connection:
      this.connection.close();