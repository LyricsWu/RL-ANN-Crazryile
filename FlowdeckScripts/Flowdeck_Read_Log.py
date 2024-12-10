# x is forward for crazyflie, y is side and z is down
# x with a dot over it means speed in x direction
# teta px is field of view in rad
# Nx is the pixel width
# higher the height more every pixel size
# h . w(b,y) is a formule for compansating angled height where ToF will measure wrong
# you read height with range.zrange with log system
# lower you are less accurate is the measurement keep it at least half a meter from desk

import time
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.utils import uri_helper
import matplotlib.pyplot as plt

import cflib.crtp

# define the URI of the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/83/2M/E7E7E7E7EA')

# positions is a dictionary that stores the x and y positions, where x and y are lists
positions = {"x": [], "y": []}
# current_position is a dictionary that stores the current x and y positions
current_position = {"x": 0, "y": 0}

def log_callback(timestamp, data, logconf):
global current_position

# data is a dictionary that stores the log variables
# motion.deltaX and motion.deltaY are the optical flow measurements in the x and y directions
# range.zrange is the range measurement from the flow deck

# TODO: Update the current position using the optical flow measurements and the range measurement
# use data["motion.deltaX"], data["motion.deltaY"] to access the optical flow measurements
# use data["range.zrange"] to access the range measurement from the flow deck
# convert the optical flow measurements in pixels to meters by dividing by scaling_factor_deltap
# convert the range measurement from millimiters to meters by dividing by scaling_factor_zrange
scaling_factor_deltap = 0.436 / 30
scaling_factor_zrange = 1000
delta_x = data["motion.deltaX"] * scaling_factor_deltap # optical flow measurement in the x direction
delta_y = data["motion.deltaY"] * scaling_factor_deltap # optical flow measurement in the y direction
height = data["range.zrange"] * scaling_factor_zrange # range measurement from the flow deck

#delta_x = data["motion.deltaX"] / 1000 # optical flow measurement in the x direction
#delta_y = data["motion.deltaY"] / 1000 # optical flow measurement in the y direction
#height = data["range.zrange"]

# Update the current position using the optical flow measurements and the range measurement
current_position["x"] += delta_x * height # use delta_x and height to update the x position
current_position["y"] += delta_y * height # use delta_y and height to update the y position

# Append the current position to the positions dictionary
positions["x"].append(current_position["x"])
positions["y"].append(current_position["y"])

def check_flow_deck(cf):
deck_status = cf.param.get_value("deck.bcFlow2")
if deck_status == 0:
raise RuntimeError("Flow Deck 2 not detected! Please attach the deck and restart.")

def main():
# Initialize Crazyflie
cflib.crtp.init_drivers()
cf=Crazyflie(rw_cache = './cache')

# Open the link to the Crazyflie
cf.open_link(uri)

try:
check_flow_deck(cf)

# Add the log configuration for the Flow Deck: motion.deltaX, motion.deltaY, range.zrange
lg_motion = LogConfig(name='FlowDeck', period_in_ms=10)
lg_motion.add_variable('motion.deltaX', 'int16_t') # int 16
lg_motion.add_variable('motion.deltaY', 'int16_t')

#lg_range = LogConfig(name='Range', period_in_ms=10)
lg_motion.add_variable('range.zrange', 'uint16_t') # unsigned int16

cf.log.add_config(lg_motion)
#cf.log.add_config(lg_range)

# Add the callback function to the log configuration
lg_motion.data_received_cb.add_callback(log_callback)
#lg_range.data_received_cb.add_callback(log_callback)

# Start the log configuration
lg_motion.start()
#lg_range.start()

print("Logging Flow Deck data. Press Ctrl+C to stop.")
while True:
time.sleep(1)