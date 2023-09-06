import threading
import time
import numpy as np
import control as ctrl

class Drone:
  def __init__(this, serial_comm):
    this.serial_comm = serial_comm
    this.last_time = time.time()

    # Set default time step
    this.dt = 0.01  

    # Transfer functions
    pitch_rate_tf_continuous_num = [-4.922, -29.87, 7.714, 0.2748];
    pitch_rate_tf_continuous_den = [1., 14.6, 226.8, 4.479, 69.48];
    pitch_rate_tf_continuous = ctrl.TransferFunction(pitch_rate_tf_continuous_num, pitch_rate_tf_continuous_den);

    roll_rate_tf_continuous_num = [10.16, 14, 104.4, -0.06075];
    roll_rate_tf_continuous_den = [1., 12.85, 30.84, 200.6, 2.071];
    roll_rate_tf_continuous = ctrl.TransferFunction(roll_rate_tf_continuous_num, roll_rate_tf_continuous_den);

    yaw_rate_tf_continuous_num = [-2.94, 6.54, 12.97, 34.83];
    yaw_rate_tf_continuous_den = [1., 4.923, 29.51, 41.25, 93.99];
    yaw_rate_tf_continuous = ctrl.TransferFunction(yaw_rate_tf_continuous_num, yaw_rate_tf_continuous_den);

    velocity_tf_continuous_num = [0.006708, 0.01154, 0.0166];
    velocity_tf_continuous_den = [1.00, 3.289, 3.91, 0.4614];
    velocity_tf_continuous = ctrl.TransferFunction(velocity_tf_continuous_num, velocity_tf_continuous_den);

    # Convert to discrete-time system
    this.p_sys = roll_rate_tf_continuous.sample(this.dt, method="zoh");
    this.q_sys = pitch_rate_tf_continuous.sample(this.dt, method="zoh");
    this.r_sys = yaw_rate_tf_continuous.sample(this.dt, method="zoh");
    this.v_sys = velocity_tf_continuous.sample(this.dt, method="zoh");

    # States [p, q, r, φ, θ, ψ, v_x, v_y, v_z];
    this.states = [.0, .0, .0, .0, .0, .0, .0, .0, .0];

    this.prev_output = [0];
    this.prev_input = [0];

  def get_command_input(self):
    """
    Retrieve command input from the serial communication.
    Return as a list for all four systems.
    """
    data = self.serial_comm.read()
    if data:
      try:
          # Assuming data is comma-separated for the four inputs
          inputs = [float(i) for i in data.split(',')]
          if len(inputs) != 4:
              raise ValueError
          return inputs
      except ValueError:
          print(f"Invalid data received: {data}")
    return [0.0, 0.0, 0.0, 0.0]  # default command inputs

  def update_state(self, command_inputs):
    """
    Update drone states based on the command inputs and transfer functions.
    """
    systems = [self.p_sys, self.q_sys, self.r_sys, self.v_sys]
    outputs = []

    for idx, (sys, command_input) in enumerate(zip(systems, command_inputs)):
        T, y = ctrl.forced_response(sys, [0, self.dt], [self.prev_input[idx], command_input], X0=self.prev_output[idx])
        output = y[-1]  # Last value is the current output

        # Store previous states
        self.prev_output[idx] = output
        self.prev_input[idx] = command_input

        outputs.append(output)

    # Assigning output values for readability
    p = outputs[0]
    q = outputs[1]
    r = outputs[2]
    v = outputs[3]

    # Update the states based on the outputs from the transfer functions
    self.states[0] = p
    self.states[1] = q
    self.states[2] = r
    self.states[6] = v  # Assuming the velocity magnitude updates v_x

    # Update Euler angles based on p, q, r
    phi = self.states[3]
    theta = self.states[4]
    
    phidot = p + q * np.sin(phi) * np.tan(theta) + r * np.cos(phi) * np.tan(theta)
    thetadot = q * np.cos(phi) - r * np.sin(phi)
    psidot = q * np.sin(phi) / np.cos(theta) + r * np.cos(phi) / np.cos(theta)

    # Integrate to get new Euler angles
    self.states[3] += phidot * self.dt
    self.states[4] += thetadot * self.dt
    self.states[5] += psidot * self.dt

  def run(this, shared_data, index):
    """
    Continuous update loop to run in a thread.
    """
    while True:
      command_input = this.get_command_input()
      y_value = this.update_state(command_input)
      shared_data[index] = y_value
      current_time = time.time()
      elapsed_time = current_time - this.last_time
      if elapsed_time < this.dt:
        time.sleep(this.dt - elapsed_time)
      this.last_time = current_time

  @staticmethod
  def process_function(drone_group, shared_data):
    """
    Function to run multiple drones in individual threads.
    """
    threads = [];
    for i, drone in enumerate(drone_group):
      t = threading.Thread(target=drone.run, args=(shared_data, i));
      t.start();
      threads.append(t);

    for t in threads:
      t.join();
