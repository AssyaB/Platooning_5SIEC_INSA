# coding: utf-8



from threading import *
import time
import can
import os
import struct
from math import pi

#importing variables linked
import VarNairobi as VN

#importing Communications Threads
#from Platooning_thread import *


MCM = 0x010
MS = 0x100
US1 = 0x000
US2 = 0x001
OM1 = 0x101
OM2 = 0x102

class calcul_temps(Thread):

    def __init__(self):
        Thread.__init__(self)
        print(self.getName(), 'initialized')

    def run(self):
       print(self.getName(), 'will work now')
       while(True):
          speed_rpm = 0.01*((VN.speed_left+VN.speed_right)/2)
          speed = speed_rpm*(2*pi*0.095)/60
          print(VN.speed_left, ' - ', VN.speed_right, ' - ', speed_rpm, ' - ', speed)
          if(speed == 0):
              print(self.getName(), "t'es à l'arrêt abruti")
          else:
              VN.temps_depl =int( (((VN.DistLidar- 1000)*1000) / speed))
              print(self.getName(), ': temps calculé ', VN.temps_depl)
          













		
