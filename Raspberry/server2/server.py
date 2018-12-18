# coding: utf-8

from threading import *
import time
import can
import os
import struct

#importing Communications Threads
from ComThread import *

#importing variables linked
import VarNairobi as VN

#importing LidarRegul.py for our regulation
from LidarRegul import *


HOST = ''                # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port

# Echo server program
import socket

if __name__ == "__main__":

    print('Bring up CAN0....')
    os.system("sudo ifconfig can0 down")
    time.sleep(0.1)
    os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
    time.sleep(0.1)

    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
    except OSError:
        print('Cannot find PiCAN board.')
        exit()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        VN.conn, VN.addr = s.accept()
        print('Connected by', VN.addr)


        #starting HMI Communications Threads
        newthread = MyReceive(VN.conn, bus)
        newthread.setName('Th-Receiver')
        newthread.start()
        newsend = MySend(VN.conn, bus)
        newsend.setName('Th-Sender')
        newsend.start()
        
        #starting platooning thread
        newthreadplat = MyPlatooning(bus)
        newthreadplat.setName('Th-Platooning')
        newthreadplat.start()
        
        #starting Lidar and regulation threads
        newLidar = Lidar_thread()
        newLidar.setName('Th-Lidar')
        newLidar.start()
        newRegul = commande_LIDAR(bus)
        newRegul.setName('Th-Regul')
    
    except KeyboardInterrupt:#To finish : Stop correctly all the threads
        VN.stop_all.set()
        VN.exit_lidar.set()
        
    
    newthread.join()
    newsend.join()
    newLidar.join()
    newRegul.join()
    newthreadplat.join()
    
    print('Bring down CAN0....')
    os.system("sudo ifconfig can0 down")
    time.sleep(0.1)
