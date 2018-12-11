# coding: utf-8
from threading import *
import time
import can
import os
import struct

# Echo server program
import socket

HOSTPLAT = "192.168.137.87"
PORTPLAT = 7777

#importing variables linked
import VarNairobi as VN

class MyReceivePlat(Thread):
    
    def __init__(self, splat, bus):
        Thread.__init__(self)
        self.bus = bus
        self.sock = splat
        print(self.getName(), 'initialized')
        
    def run(self):
        while True :
            data = self.sock.recv(1024)
            
            if not data: break
            if VN.PlatooningActive.isSet():
                print('Received', repr(data))
        
        self.sock.close()


class MyPlatooning(Thread):

    def __init__(self,bus):
        Thread.__init__(self)
        self.bus = bus
        print(self.getName(), 'initialized')

    def run(self):
        while True :
            if VN.PlatooningActive.isSet():
                splat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    splat.connect((HOSTPLAT, PORTPLAT))
                    print('Connected to', splat)
                    
                    #starting Communications Thread
                    newthread_platoon = MyReceivePlat(splat, self.bus)
                    newthread_platoon.setName('Th-ComPlatoon')
                    newthread_platoon.start()
                    
                    newthread_platoon.join()
                except socket.error:
                    print("Connexion error")
