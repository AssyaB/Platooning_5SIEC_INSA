# coding: utf-8
from threading import *
import time
import can
import os
import struct
from math import *

# Echo server program
import socket

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
        self.turn = 0
        while VN.PlatooningActive.is_set():
            data = self.sock.recv(1024)
            data = str(data)
            if not data: continue
            data = data[2:len(data)-1]
            
            print(self.getName(), 'Received', repr(data))
            if (data == 'left'):
                self.turn = 1
                cmd_turn = 95
                print(self.getName(), "send cmd turn left")
            elif (data == 'right'):
                self.turn = 1
                cmd_turn = 5
                print(self.getName(), "send cmd turn right")
            elif (data == 'str'):
                self.turn = 1
                cmd_turn = 50
                print(self.getName(), "send cmd turn right")
            elif (data == 'stop'):
                self.turn = 0
                print(self.getName(), "send cmd stop to turn")

            #commande turn
            if self.turn == 0:
                cmd_turn = 50
            else:
                cmd_turn |= 0x80
            speed_rpm = 0.01*((VN.speed_left+VN.speed_right)/2.)
            speed = speed_rpm*(2.*pi*0.095)/60.
            if(speed >= 0.05):
                VN.temps_depl =int( (((VN.DistLidar)*0.001) / speed))
                print(self.getName(), ': temps calculé ', VN.temps_depl, ' (', speed, ')')
            #envoi commande
                time.sleep(VN.temps_depl)
                VN.cmd_turn_com = cmd_turn
        self.sock.close()


class MyPlatooning(Thread):

    def __init__(self,bus):
        Thread.__init__(self)
        self.bus = bus
        print(self.getName(), 'initialized')

    def run(self):
        while True :
            if VN.PlatooningActive.is_set():
                print(self.getName(), 'received order to start')
                splat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #print(self.getName(), '1')
                try:
                    print(self.getName(), 'try on ', VN.IPPLAT)
                    splat.connect((VN.IPPLAT, PORTPLAT))
                    #print(self.getName(), '3')
                    print('Connected to', splat)
                    #print(self.getName(), '4')

                    #starting Communications Thread
                    newthread_platoon = MyReceivePlat(splat, self.bus)
                    #print(self.getName(), '5')
                    newthread_platoon.setName('Th-ComPlatoon')
                    #print(self.getName(), '6')
                    newthread_platoon.start()
                    #print(self.getName(), '7')

                    newthread_platoon.join()
                except socket.error as e:
                    print("Connexion error : ", e)
