#!/usr/bin/env python3
'''Records measurments to a given file. Usage example:
$ ./record_measurments.py out1.txt'''
import sys
from rplidar import RPLidar
import can
import sys
import os
import time
HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port

MCM = 0x010
MS = 0x100
US1 = 0x000
US2 = 0x001
OM1 = 0x101
OM2 = 0x102


bestQuality = 0
speed = 0
bestDistance = 7000
i = 0
Kp = 0.03
Kd = 0.09


previousErrorDistance = 0
sumErrors = 0


PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(PORT_NAME)

if __name__ == '__main__':

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
        print('Recording measurments... Press Crl+C to stop.')
        #print('Recording measurments...')
        for new_scan, quality, angle, distance in lidar.iter_measurments():
	
        #Filtrage des donnees recuperees par le lidar
            if quality!=0 and 172 <=angle and angle<= 188:
                if quality > bestQuality:
                    bestQuality = quality
                    if distance < bestDistance:
                        bestDistance = int(distance)
                i=1	
           #Calcul de la vitesse			
            elif angle > 198 and i==1:
	           #Refaire les mesures de vitesse pour obtenir un meilleur coefficient
                errorDistance = bestDistance - 2000
                variationError = errorDistance - previousErrorDistance
                boost = (errorDistance * Kp) + (Kd * variationError)	
                previousErrorDistance = errorDistance
                boost = int(boost)
                speed = speed + boost
                if speed<=0:
                    speed = 0
                elif speed >=20:
                    speed = 20
                if bestDistance>=3000:
                    speed = 0
                #Commande des roues
                cmd_mv = (50 + speed) | 0x80
                print(cmd_mv)
                msg = can.Message(arbitration_id=MCM,data=[cmd_mv, cmd_mv,0,0,0,0,0,0],extended_id=False)
                bus.send(msg)
                bestQuality = 0
                bestDistance = 7000
                i=0

    except KeyboardInterrupt:
        time.sleep(5)
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        msg = can.Message(arbitration_id=MCM,data=[50,50,50,0,0,0,0,0],extended_id=False)
        bus.send(msg)
        print('Stoping.')
