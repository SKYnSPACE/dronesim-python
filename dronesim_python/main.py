import time
import multiprocessing
import threading
import numpy as np
from collections import defaultdict


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

from timer import timer
print(f"[{timer.elapsed_time():08.3f}] SYS: Importing custom modules... (Messages will be repeated based on the number of 'process_id's you provided)");

from serial_comm import SerialComm
from drone import Drone
# from UdpComm import UdpComm

print(f"[{timer.elapsed_time():08.3f}] SYS: Successfully imported custom modules. (Messages will be repeated based on the number of 'process_id's you provided)");



def main():
  print(f"[{timer.elapsed_time():08.3f}] SYS: {len(CONFIGS)} drones will be initialized.");

  # Enable multiprocessing
  manager = multiprocessing.Manager()

    # Group drones by processes
  processes = defaultdict(list)
  for config in CONFIGS:
      processes[config["process_id"]].append(config)

  shared_data_map = {pid: manager.list(np.zeros(9 * len(process_configs))) for pid, process_configs in processes.items()}

  # Initializations
  serial_comms = {config['drone_id']: SerialComm(config['serial_port'], config['baudrate']) for config in CONFIGS};
  drones = {config['drone_id']: Drone(config['drone_id'], serial_comms[config['drone_id']]) for config in CONFIGS};
  # udp_comm = UdpComm();

  print(f"[{timer.elapsed_time():08.3f}] SYS: Initialization completed.");







  # Run drones in separate processes
  process_handlers = [];
  for pid, process_configs in processes.items():
    drone_group = [drones[config['drone_id']] for config in process_configs]
    p = multiprocessing.Process(target=Drone.process_function, args=(drone_group, shared_data_map[pid]))
    p.start()
    process_handlers.append(p)





  # Main process to run (logging & UDP comm.)
  try:
    while True:
      # This is a simple example of fetching and printing the data for all drones
      for pid, shared_data in shared_data_map.items():
        print(f"Process {pid}: {list(shared_data)}");

      # Logic for the UdpComm.

      # Print every 2 seconds
      time.sleep(2);
  
  except KeyboardInterrupt:
    print(f"[{timer.elapsed_time():08.3f}] SYS: Stopping all processes.")
    for p in process_handlers:
      p.terminate();

  print(f"[{timer.elapsed_time():08.3f}] SYS: Program terminated.");





if __name__ == "__main__":
  main();