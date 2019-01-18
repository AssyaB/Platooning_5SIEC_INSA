from rplidar import *
import time

lidar = RPLidar('/dev/ttyUSB0')
time.sleep(5)
lidar.stop()
lidar.stop_motor()
lidar.reset()
lidar.disconnect()
