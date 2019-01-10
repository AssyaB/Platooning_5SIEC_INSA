# coding: utf-8

#CLIENT_VOITURE_ROSE

from threading import Thread
import time
import can
import os
import struct

#importing Communications Threads
from ComThread import *
from MySend_COM import *
#importing variables linked
from VarNairobi import *

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port
PORTPLAT = 7777


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

        
    # Connection à l'application   
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    print('Connected by', addr)

    newthread = MyReceive(conn, bus)
    newthread.start()
    newsend = MySend(conn, bus)
    newsend.start()

    
    # Connection à la voiture qui suit
    print('ready to be connected')
    splat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('bug')
    splat.bind((HOST, PORTPLAT))
    splat.listen(1)
    print('bug2')
    connplat, addrplat = splat.accept()
    print('Connected by', addrplat)

    print("Sock :")
    type(splat)
    print("Conn :")
    type(connplat)

    #starting Communications Thread
    newsendplat = mysend_COM(connplat, bus)
    newsendplat.start()
    
    newthread.join()
    newsend.join()
    newsendplat.join()

    
    print('Bring down CAN0....')
    os.system("sudo ifconfig can0 down")
    time.sleep(0.1)
