import socket

from timer import timer

class UdpComm:
  def __init__(this, 
               local_ip="0.0.0.0", local_port=12345, 
               remote_ip="127.0.0.1", remote_port=12346,
               buffer_size=1024):
    
    this.local_ip = local_ip;
    this.local_port = local_port;
    this.remote_ip = remote_ip;
    this.remote_port = remote_port;

    this.buffer_size = buffer_size;
    
    try:
      # Creating a UDP socket
      this.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      # Bind the socket to the local address and port
      this.sock.bind((this.local_ip, this.local_port))
      print(f"[{timer.elapsed_time():08.3f}] UDP/INIT: Succesfully bound {this.local_ip}:{this.local_port}");
      print(f"[{timer.elapsed_time():08.3f}] UDP/INIT: Will transmit to {this.remote_ip}:{this.remote_port}");
    except socket.error as e:
      print(f"X[{timer.elapsed_time():08.3f}] UDP/INIT Failed: {e}");



  def send(this, data):
    """
    Sends data to the specified remote IP and port.
    """
    
    this.sock.sendto(data, (this.remote_ip, this.remote_port));
  
  def send_str(this, data, remote_ip, remote_port):
    """
    Sends data to the specified remote IP and port.
    """
    # Convert data to bytes if it's a string
    if isinstance(data, str):
        data = data.encode();
    
    this.sock.sendto(data, (remote_ip, remote_port));

  def receive_data(this):
    """
    Listens for incoming data and returns the data and address from which it was received.
    """
    data, addr = this.sock.recvfrom(this.buffer_size);
    return data, addr;

  def close(this):
    """
    Closes the UDP socket.
    """
    this.sock.close();