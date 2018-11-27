# coding: utf-8
from threading import Thread
import time
import can
import os
import struct

HOSTPLAT = "10.105.1.85"
PORTPLAT = 7777

class MyReceivePlat(Thread):
    
    def __init__(self,connplat, bus):
        Thread.__init__(self)
        self.bus = bus
        self.conn = connplat
        
    def run(self):
        while True :
            data = self.conn.recv(1024)
            
            if not data: break  
                
            print('Received', repr(data))
        
        self.conn.close()        



class MyPlatooning(Thread):

    def __init__(self,connplat, bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
        while True :

            splat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connplat = splat.connect(HOSTPLAT, PORTPLAT)
            
            newthread_platoon = MyReceivePlat(connplat, bus)
            newthread_platoon.start()

            newthread_platoon.join()
      
