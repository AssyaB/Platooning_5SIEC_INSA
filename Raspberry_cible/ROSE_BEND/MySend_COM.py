# coding: utf-8
from threading import *
import time
import can
import os
import struct
import socket #client_ROSE

PORTPLAT = 7777

#importing variables linked
import VarNairobi as VN


class mysend_COM(Thread):
    
    def __init__(self, splat, bus):
        Thread.__init__(self)
        self.bus = bus
        self.sock = splat
        
    def run(self):
        while !VN.stop_all.is_set() :
            VN.semaphore_TURN.acquire()
            if (VN.COM_TURN!='ouep'):
                self.sock.send(VN.COM_TURN.encode())
                print("data sent: " + str(VN.COM_TURN))
                VN.COM_TURN = 'ouep'
            VN.semaphore_TURN.release()
        self.connplat.close()
