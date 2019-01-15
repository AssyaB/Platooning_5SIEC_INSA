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
        oldAngle = 180
        Kp = 0.06
        init = 0
        time.sleep(2)
        for new_scan, quality, angle, distance in self.lidar.iter_measurments():
            #print(self.getName(), 'reading lidar') #OK
            if VN.lidar_reinit.is_set():
                VN.lidar_reinit.clear()
                i=0
                bestQuality = 0
                DistTab = [7000]
                AnglTab = [0]
                bestDistance = 7000
                bestAngle = 180
                oldGoodValue = 7000
                oldAngle = 180
                init = 0
            if VN.exit_lidar.is_set() :
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
                if quality>= 10 and oldAngle-9 <=angle and angle<= oldAngle+9:
                    if (distance > 600):
                        if (distance < mean(DistTab)*0.9):
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
                    #print(self.getName(), ': Test')
                    if VN.DistLidarSem.acquire(False): #acquire semaphore without blocking
                        #print(self.getName(), ': access DistLidar')
                        VN.DistLidar = bestDistance
                        VN.DistLidarSem.release()
                    else:
                        print(self.getName(), ': can not access DistLidar')
                    if VN.PlatooningActive.is_set():
                        # Correction Vitesse
                        if bestDistance > 2000:
                            if oldGoodValue < 1600:
                                temp = bestDistance
                                bestDistance = oldGoodValue
                                oldGoodValue = temp
                            else:
                                oldGoodValue = bestDistance
                        else:
                            oldGoodvalue = bestDistance
                        errorDistance = bestDistance - 1600
                        speed = (errorDistance * Kp)
                        speed = int(speed)
                        if speed<=0:
                            speed = 0
                        elif speed >=20:
                            speed = 20
                        #Gestion d'anomalies et d'obstacles a� partir du 2eme tour du lidar
                        if init == 1:
                            diffDistance= oldDistance - bestDistance
                            if bestDistance>=1600:
                                speed = 0
                                print(self.getName(), "vehicle loss")
                                VN.lidar_loss.set()
                            elif diffDistance>=150:
                                speed = 0
                                VN.lidar_obstacle.set()
                                print(self.getName(), "obstacle detected")

                        cmd_mv = (50 + speed) | 0x80
                        #print(cmd_mv)
                        # Correction Angle
                        errorAngle = bestAngle - 180
                        corrAngle = int((errorAngle*15) / 9) #erreur * K (ici 15/9 pour un calcul rapide et peu complexe (adaptation à l'attendu commande))
                        if corrAngle > 15:
                            corrAngle = 15
                        elif corrAngle < -15:
                            corrAngle = -15
                        cmd_turn = (VN.cmd_turn_com - corrAngle)| 0x80
                        msg = can.Message(arbitration_id=MCM,data=[cmd_mv, cmd_mv, cmd_turn, 0, 0, 0, 0, 0], extended_id = False)
                        self.bus.send(msg)

                        #memorisation de la distance moyenne precedente
                        oldDistance = bestDistance
                        init = 1

                    i=0
                    oldAngle = mean(AnglTab)
                    bestQuality = 0
                    DistTab = [7000]
                    AnglTab = [0]
                    bestDistance = 7000
                    bestAngle = 0

