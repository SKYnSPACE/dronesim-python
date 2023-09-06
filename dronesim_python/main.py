import time
from timer import timer
import multiprocessing
from collections import defaultdict

print(f"[{timer.elapsed_time():08.3f}] SYS: Importing custom modules...");

from serial_comm import SerialComm
from drone import Drone
# from UdpComm import UdpComm

print(f"[{timer.elapsed_time():08.3f}] SYS: Successfully imported custom modules.");

# Configurations
CONFIGS = [
  {'drone_id': 0, 'serial_port': 'COM3',  'baudrate': 9600, 'process_id': 0},
  {'drone_id': 1, 'serial_port': 'COM4',  'baudrate': 9600, 'process_id': 0},
  {'drone_id': 2, 'serial_port': 'COM5',  'baudrate': 9600, 'process_id': 0},
  {'drone_id': 3, 'serial_port': 'COM6',  'baudrate': 9600, 'process_id': 0},
  {'drone_id': 4, 'serial_port': 'COM7',  'baudrate': 9600, 'process_id': 1},
  {'drone_id': 5, 'serial_port': 'COM8',  'baudrate': 9600, 'process_id': 1},
  {'drone_id': 6, 'serial_port': 'COM9',  'baudrate': 9600, 'process_id': 1},
  {'drone_id': 7, 'serial_port': 'COM10', 'baudrate': 9600, 'process_id': 1},
]

print(f"[{timer.elapsed_time():08.3f}] SYS: {len(CONFIGS)} drones will be initialized.");

# Initializations
serial_comms = {config['drone_id']: SerialComm(config['serial_port'], config['baudrate']) for config in CONFIGS};
drones = {config['drone_id']: Drone(serial_comms[config['drone_id']]) for config in CONFIGS}
