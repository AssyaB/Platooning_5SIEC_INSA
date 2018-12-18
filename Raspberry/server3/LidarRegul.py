# coding: utf-8
from threading import *
import time
import can
import os
import struct
from rplidar import *
#importing variables linked
import VarNairobi as VN

PORT_NAME = '/dev/ttyUSB0'

MCM = 0x010

'''
bestQuality and bestDistance used to decide of the best distance to see.
DistLidar (global variable in VarNairobi) needs to be set after with the last bestDistance value to be sent to the app.
'''
def mean(data):
    res = 0
    for x in data:
        res += x
    res /= len(data)
    return res;

class Lidar_thread(Thread):  
    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        print(self.getName(), 'initialized')
        self.lidar = RPLidar(PORT_NAME)
        
    
    def run(self):
        print(self.getName(), 'running')
        i=0
        bestQuality = 0
        DistTab = [7000]
        AnglTab = [0]
        bestDistance = 7000
        bestAngle = 180
        oldGoodValue = 7000
        Kp = 0.06
        time.sleep(2)
        for new_scan, quality, angle, distance in self.lidar.iter_measurments():
            #print(self.getName(), 'reading lidar') #OK
            if VN.exit_lidar.isSet() :
                print(self.getName(), 'stopping')
                # dans VarNairobi exit_lidar=threading.Even(); exit_lidar.clear()
                # et dans le main on ajoute signal.signal(signal.sigint signal handler)???
                time.sleep(5)
                self.lidar.stop()
                self.lidar.stop_motor()
                self.lidar.disconnect()
                break
            else :
                #dans VarNairobi wait_interface_on=threading.Even(); wait_interface_on.clear()
                #Filtrage des donnees recuperees par le lidar
                if quality>= 10 and 160 <=angle and angle<= 200:
                    if distance > 500:
                        if distance < mean(DistTab)*0.9:
                            DistTab = [distance]
                            AnglTab = [angle]
                        elif distance <= mean(DistTab)*1.1:
                            DistTab.append(distance)
                            AnglTab.append(angle)
                            #print(self.getName(), ': BD : ', int(mean(DistTab)))
                        i=1				
                #Calcul de la cmd vitesse			
                elif angle > 210 and i==1:
                    bestDistance = int(mean(DistTab))
                    bestAngle = int(mean(AnglTab))
                    print(self.getName(), ': Test')
                    if VN.DistLidarSem.acquire(False): #acquire semaphore without blocking
                        print(self.getName(), ': access DistLidar')
                        VN.DistLidar = bestDistance
                        VN.DistLidarSem.release()
                    else:
                        print(self.getName(), ': can not access DistLidar')
                    if VN.PlatooningActive.isSet():
                        # Correction Vitesse
                        if bestDistance > 4000:
                            if oldGoodValue < 3000:
                                temp = bestDistance
                                bestDistance = oldGoodValue
                                oldGoodValue = temp
                            else:
                                oldGoodValue = bestDistance
                        else:
                            oldGoodvalue = bestDistance
                        errorDistance = bestDistance - 2000
                        speed = (errorDistance * Kp)	
                        speed = int(speed)
                        if speed<=0:
                            speed = 0
                        elif speed >=20:
                            speed = 20
                        if bestDistance>=3000:
                            speed = 0
                        cmd_mv = (50 + speed) | 0x80
                        print(cmd_mv)
                        # Correction Angle
                        errorAngle = bestAngle - 180
                        corrAngle = int((errorAngle*50) / 20) #erreur*  * K (ici 50/20 pour un calcul rapide et peu complexe (adaptation à l'attendu commande))
                        cmd_turn = (50 - corrAngle)| 0x80
                        msg = can.Message(arbitration_id=MCM,data=[cmd_mv, cmd_mv, cmd_turn, 0, 0, 0, 0, 0], extended_id = False)
                        self.bus.send(msg)
                    i=0
                    bestQuality = 0
                    DistTab = [7000]
                    AnglTab = [0]
                    bestDistance = 7000
                    bestAngle = 0


class commande_LIDAR(Thread):

    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus

    def run(self):
        while True:
            if VN.PlatooningActive.isSet():
                #Commande des roues
                #il faut ajouter des sémaphores pour avoir l'exclusion mutuelle au CAN entre l'IHM et COMMANDE_LIDAR
                cmd_mv = (50 + speed) | 0x80
                print(cmd_mv)
                msg = can.Message(arbitration_id=MCM,data=[cmd_mv, cmd_mv, 0, 0, 0, 0, 0, 0], extended_id = False)
                self.bus.send(msg)


