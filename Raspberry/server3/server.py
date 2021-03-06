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

#importing Communications Threads
#from Platooning_thread import *

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

    #Looking for IP address to "know" which network is used
    ip = os.popen('hostname -I').read() #get chain with '[@IP] \n'
    ip = ip[:len(ip)-2] #(suppress ' \n')
    # Only correct with the two cars black and pink
    if ip == '10.105.1.17': #IOT network
        VN.IPPLAT = '10.105.0.53'
    elif ip == '192.168.137.149': #Nairobibi network
        VN.IPPLAT = '192.168.137.87'
    
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
        '''
        #starting platooning thread
        newthreadplat = MyPlatooning(bus)
        newthreadplat.setName('Th-Platooning')
        newthreadplat.start()
        '''
        #starting Lidar and regulation threads
        newLidar = Lidar_thread(bus)
        newLidar.setName('Th-Lidar')
        newLidar.start()
        '''
        newRegul = commande_LIDAR(bus)
        newRegul.setName('Th-Regul')
        newRegul.start()
        '''
    except KeyboardInterrupt:#To finish : Stop correctly all the threads
        VN.stop_all.set()



    newthread.join()
    newsend.join()

    VN.exit_lidar.set()
    newLidar.join()
    '''
    newRegul.join()
    newthreadplat.join()
    '''
    print('Bring down CAN0....')
    os.system("sudo ifconfig can0 down")
    time.sleep(0.1)
