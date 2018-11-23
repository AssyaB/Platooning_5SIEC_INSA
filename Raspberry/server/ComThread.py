# coding: utf-8

from threading import Thread
import time
import can
import os
import struct

#importing variables linked
import VarNairobi

MCM = 0x010
MS = 0x100
US1 = 0x000
US2 = 0x001
OM1 = 0x101
OM2 = 0x102

'''
 Messages envoyés :
    - ultrason avant gauche
    header : UFL payload : entier, distance en cm
    - ultrason avant centre
    header : UFC payload : entier, distance en cm
    - ultrason avant droite
    header : UFR payload : entier, distance en cm
    - ultrason arriere gauche
    header : URL payload : entier, distance en cm
    - ultrason arriere centre
    header : URC payload : entier, distance en cm
    - ultrason arriere droite
    header : URR payload : entier, distance en cm
    - position volant
    header : POS payload : entier, valeur brute du capteur
    - vitesse roue gauche
    header : SWL payload : entier, *0.01rpm
    - vitesse roue droite
    header : SWR payload : entier, *0.01rpm
    - Niveau de la batterie
    header : BAT payload : entier, mV
    - Pitch
    header : PIT payload : float, angle en degrée
    - Yaw
    header : YAW payload : float, angle en degrée
    - Roll
    header : ROL payload : float, angle en degrée

 Messages reçus :
    - Modification de la vitesse
    header : SPE payload : valeur entre 0 et 50
    - Control du volant (droite, gauche)
    header : STE paylaod : left | right | stop
    - Control de l'avancée
    header : MOV payload : forward | backward | stop
'''

class MySend(Thread):

    def __init__(self, conn, bus):
        Thread.__init__(self)
        self.conn = conn
        self.bus = bus

    def run(self):
        while True :
            msg = self.bus.recv()

            #print(msg.arbitration_id, msg.data)
            st = ""

            if msg.arbitration_id == US1:
                # ultrason avant gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "UFL:" + str(distance) + ";"
                size = self.conn.send(message.encode())
                if size == 0: break
                # ultrason avant droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "UFR:" + str(distance)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
                # ultrason arriere centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "URC:" + str(distance)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
            elif msg.arbitration_id == US2:
                # ultrason arriere gauche
                distance = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "URL:" + str(distance)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
                # ultrason arriere droit
                distance = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "URR:" + str(distance)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
                # ultrason avant centre
                distance = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "UFC:" + str(distance)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
            elif msg.arbitration_id == MS:
                # position volant
                angle = int.from_bytes(msg.data[0:2], byteorder='big')
                message = "POS:" + str(angle)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
                # Niveau de la batterie
                bat = int.from_bytes(msg.data[2:4], byteorder='big')
                message = "BAT:" + str(bat)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
                # vitesse roue gauche
                speed_left = int.from_bytes(msg.data[4:6], byteorder='big')
                message = "SWL:" + str(speed_left)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
                # vitesse roue droite
                # header : SWR payload : entier, *0.01rpm
                speed_right= int.from_bytes(msg.data[6:8], byteorder='big')
                message = "SWR:" + str(speed_right)+ ";"
                size = self.conn.send(message.encode())
                if size == 0: break
            elif msg.arbitration_id == OM1:
                # Yaw
                yaw = struct.unpack('>f',msg.data[0:4])
                message = "YAW:" + str(yaw[0])+ ";"
                #st += message
                size = self.conn.send(message.encode())
                if size == 0: break
                # Pitch
                pitch = struct.unpack('>f',msg.data[4:8])
                message = "PIT:" + str(pitch[0])+ ";"
                #st += message
                size = self.conn.send(message.encode())
                if size == 0: break
            elif msg.arbitration_id == OM2:
                # Roll
                roll = struct.unpack('>f',msg.data[0:4])
                message = "ROL:" + str(roll[0])+ ";"
                #st += message
                size = self.conn.send(message.encode())
                if size == 0: break

            #if (st!=""):print(st)


class MyReceive(Thread):
    def __init__(self,conn, bus):
        Thread.__init__(self)
        self.conn = conn
        self.bus  = can.interface.Bus(channel='can0', bustype='socketcan_native')

        self.speed_cmd = 0
        self.move = 0
        self.turn = 0
        self.enable = 0

    def run(self):
        self.speed_cmd = 0
        self.move = 0
        self.turn = 0
        self.enable = 0

        while True :
            data = conn.recv(1024)

            if not data: break

            header = data[0:3]
            payload = data[3:]
            print("header :", header, "payload:", str(payload))

            if (header == b'SPE'):  # speed
                self.speed_cmd = int(payload)
                print("speed is updated to ", self.speed_cmd)
            elif (header == b'STE'):  # steering
                if (payload == b'left'):
                    self.turn = -1
                    self.enable = 1
                    print("send cmd turn left")
                elif (payload == b'right'):
                    self.turn = 1
                    self.enable = 1
                    print("send cmd turn right")
                elif (payload == b'stop'):
                    self.turn = 0
                    self.enable = 0
                    print("send cmd stop to turn")
            elif (header == b'MOV'):  # move
                if (payload == b'stop'):
                    self.move = 0
                    self.enable = 0
                    print("send cmd move stop")
                elif (payload == b'forward'):
                    print("send cmd move forward")
                    self.move = 1
                    self.enable = 1
                elif (payload == b'backward'):
                    print("send cmd move backward")
                    self.move = -1
                    self.enable = 1
            elif (header == b'PLA'):
                if (payload == b'on'):
                    print("strarting platooning mode")
                if (payload == b'off'):
                    print("stopping platooning mode")

            print(self.speed_cmd)
            print(self.move)
            print(self.turn)
            print(self.enable)

            #edition des commandes de mouvement
            if ~self.move:
                cmd_mv = (50 + self.move*self.speed_cmd) & ~0x80
            else:
                cmd_mv = (50 + self.move*self.speed_cmd) | 0x80

            if ~self.turn:
                cmd_turn = 50 +self.turn*20 & 0x80
            else:
                cmd_turn = 50 + self.turn*20 | 0x80

            print("mv:",cmd_mv,"turn:",cmd_turn)

            msg = can.Message(arbitration_id=MCM,data=[cmd_mv, cmd_mv, cmd_turn,0,0,0,0,0],extended_id=False)

            print(msg)
            self.bus.send(msg)

        conn.close()
