import threading
import time
import numpy as np
import control as ctrl

from timer import timer

class Drone:
  def __init__(this, id, serial_comm):
    this.id = id;
    this.serial_comm = serial_comm;
    this.last_time = time.time();

    # Set default time step
    this.dt = 0.01; # 100 Hz

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

    # States [p, q, r, φ, θ, ψ, u, v, w];
    this.states = [.0] *9;

    this.prev_output = [.0] *4;
    this.prev_input = [.0] *4;

  def get_command_input(this):
    """
    Retrieve command input from the serial communication.
    Return a list of four command inputs.
    """
    data = this.serial_comm.read();
    if data:
      try:
          # Assuming data is comma-separated for the four inputs
          inputs = [float(i) for i in data.split(',')]
          if len(inputs) != 4:
              raise ValueError
          return inputs;
      except ValueError:
          print(f"W[{timer.elapsed_time():08.3f}] UAV{this.id}: INVALID DATA {data}");
    return [0.0, 0.0, 0.0, 0.0];  # default command inputs

  def update_state(this, command_inputs):
    """
    Update drone states based on the command inputs and transfer functions.
    """
    systems = [this.p_sys, this.q_sys, this.r_sys, this.v_sys];
    outputs = [];

    for idx, (sys, command_input) in enumerate(zip(systems, command_inputs)):
      T, y = ctrl.forced_response(sys, [0, this.dt], [this.prev_input[idx], command_input], X0=this.prev_output[idx]);
      output = y[-1];  # Last value is the current output

      # Store previous states
      this.prev_output[idx] = output;
      this.prev_input[idx] = command_input;

      outputs.append(output);

    # Assigning output values for readability
    p = outputs[0];
    q = outputs[1];
    r = outputs[2];
    v = outputs[3];

    # Update the states based on the outputs from the transfer functions
    this.states[0] = p;
    this.states[1] = q;
    this.states[2] = r;
    this.states[6] = v;  # Assuming the velocity magnitude updates u velocity only.

    # Update Euler angles based on p, q, r
    phi = this.states[3];
    theta = this.states[4];
    
    phidot = p + q * np.sin(phi) * np.tan(theta) + r * np.cos(phi) * np.tan(theta);
    thetadot = q * np.cos(phi) - r * np.sin(phi);
    psidot = q * np.sin(phi) / np.cos(theta) + r * np.cos(phi) / np.cos(theta);

    # Integrate to get new Euler angles
    this.states[3] += phidot * this.dt;
    this.states[4] += thetadot * this.dt;
    this.states[5] += psidot * this.dt;
  
    return this.states;  # Return the updated states

  def run(this, shared_data, index):
    """
    Continuous update loop to run in a thread.
    """
    while True:
      command_input = this.get_command_input();
      drone_states = this.update_state(command_input);  # Capture returned states
      shared_data[index] = drone_states;  # Update shared data
      current_time = time.time();
      elapsed_time = current_time - this.last_time;
      if elapsed_time < this.dt:
        time.sleep(this.dt - elapsed_time);
      this.last_time = current_time;

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
