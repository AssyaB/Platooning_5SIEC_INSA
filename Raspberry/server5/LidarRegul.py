# coding: utf-8
from threading import *
import time
import os
import struct
import can
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
    return res
    

class Lidar_thread(Thread):
    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        print(self.getName(), 'initialized')
        self.lidar = RPLidar(PORT_NAME)


    def run(self):
        print(self.getName(), 'running')
        i=0 #used to know if one or more correct data has been collected.
        DistTab = [7000]
        AnglTab = [0]
        bestDistance = 7000
        bestAngle = 90
        oldAngle = 90
        VN.Lidar_init = 0
        index = 0
        time.sleep(2)
        for new_scan, quality, angle, distance in self.lidar.iter_measurments():
            if new_scan:
                index = (index + 1)%2
            if index == 0:
                #print(self.getName(), 'reading lidar') #OK
                if VN.lidar_reinit.is_set():
                    VN.lidar_reinit.clear()
                    VN.lidar_avail.clear()
                    i=0
                    DistTab = [7000]
                    AnglTab = [0]
                    bestDistance = 7000
                    bestAngle = 90
                    VN.Lidar_oldGoodValue = 7000
                    oldAngle = 90
                    VN.Lidar_init = 0
                elif VN.exit_lidar.is_set() :
                    print(self.getName(), 'stopping')
                    # dans VarNairobi exit_lidar=threading.Even(); exit_lidar.clear()
                    # et dans le main on ajoute signal.signal(signal.sigint signal handler)???
                    self.lidar.stop()
                    self.lidar.stop_motor()
                    self.lidar.disconnect()
                    time.sleep(5)
                    break
                else :
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

                    # Set available data and throw possible calculation
                    elif angle > 210 and i==1:
                        bestDistance = int(mean(DistTab))
                        bestAngle = int(mean(AnglTab))
                        if VN.DistLidarSem.acquire(False): #acquire semaphore without blocking
                            #print(self.getName(), ': access DistLidar')
                            VN.DistLidar = bestDistance
                            VN.DistLidarSem.release()
                        else:
                            print(self.getName(), ': can not access DistLidar')
                        if VN.LidarSem.acquire(False):
                            VN.Lidar_bDist = bestDistance
                            VN.Lidar_bAngle = bestAngle
                            VN.LidarSem.release()
                            VN.lidar_avail.set()
                        else:
                            print(self.getName(), ': can not access LidarSem, try again')
                        i=0
                        oldAngle = bestAngle
                        if oldAngle > 90 + 60:
                            oldAngle = 90+60
                        elif oldAngle < 90-60:
                            oldAngle = 90-60
                        DistTab = [7000]
                        AnglTab = [0]
                        bestDistance = 7000
                        bestAngle = 0
                        #self.lidar.clear_input()


class regul_thread(Thread):
    def __init__(self, bus):
        Thread.__init__(self)
        self.bus = bus
        self.speed = 0
        self.Treduced = 0
        self.timestop = Timer(5., self.stopCar)
        self.timered = Timer(.5, self.reduce_speed)
        print(self.getName(), 'initialized')
    
    def reduce_speed(self):
        if self.speed > 0 :
            self.Treduced = 1
            self.speed = self.speed - 1
            self.timered = Timer(.5, self.reduce_speed)
            self.timered.start()
    
    def stopCar(self):
        if self.speed > 0 :
            timered = Timer(.5, self.reduce_speed)
            self.timered.start()

    def run(self):
        print(self.getName(), 'running')
        bestDistance = 7000
        bestAngle = 90
        VN.Lidar_oldGoodValue = 7000
        Kp = 0.08
        leaving = 0
        while ~VN.stop_all.is_set():
            if VN.PlatooningActive.is_set():
                VN.lidar_avail.wait(timeout = 5.)
                if VN.lidar_avail.is_set():
                    # Reset lidar_avail and collect Lidar data.
                    VN.lidar_avail.clear()
                    VN.LidarSem.acquire() #attente infinie
                    bestDistance = VN.Lidar_bDist
                    bestAngle = VN.Lidar_bAngle
                    VN.LidarSem.release()
                    #print(self.getName(),' régule')
                    # Correction Vitesse
                    if bestDistance > 2600:
                        if VN.Lidar_oldGoodValue < 1600:
                            temp = bestDistance
                            bestDistance = VN.Lidar_oldGoodValue
                            VN.Lidar_oldGoodValue = temp
                        else:
                            VN.Lidar_oldGoodValue = bestDistance
                    else:
                        VN.Lidar_oldGoodValue = bestDistance
                    if(leaving == 0):
                        errorDistance = bestDistance - 1600
                        self.speed = (errorDistance * Kp)
                        self.speed = int(self.speed)
                        if self.speed<=0:
                            self.speed = 0
                        elif self.speed >=20:
                            self.speed = 20
                        
                    #Gestion d'anomalies et d'obstacles a� partir du 2eme tour du lidar
                    if VN.Lidar_init == 1:
                        diffDistance = VN.Lidar_oldGoodValue - bestDistance
                        if bestDistance>=2600:
                            if self.speed >=10:
                                self.speed = 10
                                self.timestop = Timer(5., self.stopCar)
                                self.timestop.start()
                            else:
                                self.speed = 0
                                self.timered = Timer(5., self.reduce_speed)
                                self.timestop.cancel()
                                self.timered.start()
                            print(self.getName(), "vehicle loss")
                            VN.lidar_loss.set()
                            leaving = 1
                            
                        elif diffDistance>=150:
                            self.speed = 0
                            VN.lidar_obstacle.set()
                            print(self.getName(), "obstacle detected")
                        
                    #print(self.getName(), "speed : ", self.speed)
                    cmd_mv = (50 + self.speed) | 0x80
                    
                    #Calcul d'angle
                    
                    # Correction Angle
                    errorAngle = bestAngle - 90
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
                    VN.Lidar_init = 1
            else:
                leaving = 0

