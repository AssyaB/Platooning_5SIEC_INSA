# coding: utf-8
from threading import *


#IP of the front vehicle
global IPPLAT
IPPLAT = '10.105.0.53'
#Signal all stop
global stop_all
stop_all = Event()
stop_all.clear()

#Var for communication to the threads (app)
global conn
global addr

#Sem and var for Distance communication to the app
global DistLidarSem
DistLidarSem = BoundedSemaphore(1)
global DistLidar
DistLidar = 2000

# Signals and events for LidarRegul
global exit_lidar
exit_lidar = Event()
exit_lidar.clear()
global PlatooningActive
PlatooningActive = Event()
PlatooningActive.clear()
global lidar_obstacle
lidar_obstacle = Event()
lidar_obstacle.clear()
global lidar_loss
lidar_loss = Event()
lidar_loss.clear()
global lidar_reinit
lidar_reinit = Event()
lidar_reinit.clear()
