# coding: utf-8
from threading import *

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

