# coding: utf-8
from threading import Thread
import time
import can
import os
import struct

# Echo server program
import socket

HOSTPLAT = "10.105.0.53"
PORTPLAT = 7777

#importing variables linked
from VarNairobi import *

class MyReceivePlat(Thread):
    
    def __init__(self, splat, bus):
        Thread.__init__(self)
        self.bus = bus
        self.sock = splat
        
    def run(self):
        while True :
            data = self.sock.recv(1024)
            
            if not data: break
                
            print('Received', repr(data))
        
        self.connplat.close()



class MyPlatooning(Thread):

    def __init__(self,bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
        while True :

            splat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                splat.connect((HOSTPLAT, PORTPLAT))
                print("Connexion : ", splat)
                print("type :")
                type(splat)
                
                newthread_platoon = MyReceivePlat(splat, self.bus)
                newthread_platoon.start()
                
                print("Génial on est connecté")
                
                newthread_platoon.join()
            except socket.error:
                print("Cosmic ray detected")
