import math
import time
from grpc import access_token_call_credentials
import pygame
from math import cos, sin, pi, atan, sqrt
import matplotlib.pyplot as plt
##### This part isn't explained here, I haven't understood it yet #####
GRAVITY = 9.81
MASS = 1200
CGToFront = 2.0*10
CGToBack = 2.0*10
cgToFrontAxle = 1.25*10
cgToBackAxle = 1.25*10
CGHeight = 0.55
wheelRadius = 0.3
tireGrip = 2
lockGrip = 0.7
engineForce = 8000
brakeForce = 12000
weightTransfer = 0.2
maxSteer = 0.6
cornerStiffnesFront = 5
cornerStiffnesBack = 5.2
airResist = 2.5
rollResist = 8.0
INERTIA = MASS
def sign(x):
    if x<0:
        return -1
    elif x == 0:
        return 0
    return 1
def clamp(x,min,max):
    if x<min:
        return min
    elif x>max:
        return max
    return x
labels = ["steerAngle","steer",
            "heading", "yawRate",

            "velocity_c.x","velocity_c.y",
            "accel_c.x", "accel_c.y",
            "yawSpeed.Front", "yawSpeed.Rear",
            "slipAngle.Front","slipAngle.Rear",
            "Friction.Front", "Friction.Rear"]
blacklist = ["steerAngle","steer","velocity_c.x","velocity_c.y",
"accel_c.x","accel_c.y","Friction.Front", "Friction.Rear"]
withelist = []#["slipAngle.Front","slipAngle.Rear","heading","yawRate"]
class Data():
    steerAngle = [0]
    steer = [0]
    heading = [0]
    velocity_c = [[0],[0]]
    accel_c = [[0],[0]]
    yawRate = [0]
    yawSpeed = [[0],[0]]
    slipAngle = [[0],[0]]
    Friction = [[0],[0]]
    def append_(self,data):
        self.steerAngle.append(data[0])
        self.steer.append(data[1])
        self.heading.append(data[2])

        self.velocity_c[0].append(data[3][0][0])
        self.velocity_c[1].append(data[3][0][1])

        self.yawRate.append(data[5])

        self.accel_c[0].append(data[4][0][0])
        self.accel_c[1].append(data[4][0][1])

        self.yawSpeed[0].append(data[6][0])
        self.yawSpeed[1].append(data[6][1])

        self.slipAngle[0].append(data[7][0])
        self.slipAngle[1].append(data[7][1])

        self.Friction[0].append(data[8][0]/MASS)
        self.Friction[1].append(data[8][1]/MASS)
    def getData(self):
        data = [
            self.steerAngle,self.steer,
            self.heading, self.yawRate,

            self.velocity_c[0],self.velocity_c[1],
            self.accel_c[0], self.accel_c[1],
            self.yawSpeed[0], self.yawSpeed[1],
            self.slipAngle[0],self.slipAngle[1],
            self.Friction[0], self.Friction[1]
        ]
        return data

class Plot():
    times = [0]
    data = Data()
    def __init__(self):
        plt.ion()
    def update(self,data,dt,vis):
        #plt.gca().cla()
        self.times.append(self.times[-1]+dt)
        self.data.append_(data)
        if vis:
            self.show()
    def show(self,end = False):
        data_ = self.data.getData()
        for i, element in enumerate(data_):
            if labels[i] in blacklist:
                continue
            if len(withelist) !=0:
                if not labels[i] in withelist:
                    continue
            plt.plot(self.times,element,label = labels[i])
        plt.legend()
        if end:
            plt.show(block = True)
            #return
        else:
            plt.draw()
            plt.pause(0.001)
class Car():
    inputs = 0#-1, 0, 1 left, straight, right
    throttle = 0
    brake = 0

    heading = 0
    position = [0,0]
    velocity = [0,0]
    accel_c = [0,0]
    yawRate = 0.0
    absVel = 0
    velocity_c = (0,0)
    steer = 0
    steerAngle = 0
    def __init__(self) -> None:
        pass
    def update(self,dt):
        steerInput = self.steer
        self.steerAngle = steerInput*maxSteer
        self.doPhyisiks(dt)
    def doPhyisiks(self,dt):
        # High speed Implementation
        sn = sin(self.heading)
        cs = cos(self.heading)

        velocity_c = [
            cs*self.velocity[0] + sn *self.velocity[1],
            sn*self.velocity[0] - cs *self.velocity[1],
        ]
        axleWeigth = MASS * GRAVITY * 0.5

        yawSpeedFront = cgToFrontAxle*self.yawRate
        yawSpeedRear = -cgToBackAxle*self.yawRate
        #print(velocity_c[1]+yawSpeedFront, abs(velocity_c[0])-sign(velocity_c[0])*self.steerAngle)
        if (abs(velocity_c[0])!=0):
            slipAngleFront = atan((velocity_c[1]+yawSpeedFront)/abs(velocity_c[0]))-sign(velocity_c[0])*self.steerAngle
            slipAngleRear = atan((velocity_c[1]+yawSpeedRear)/abs(velocity_c[0]))
        else:
            slipAngleRear = 0
            slipAngleFront = 0
        #print(slipAngleFront,slipAngleRear)
        FrictionFront = clamp(-cornerStiffnesFront*slipAngleFront,-tireGrip,tireGrip)*axleWeigth
        FrictionRear = clamp(-cornerStiffnesBack*slipAngleRear,-tireGrip,tireGrip)*axleWeigth
        #print(FrictionFront,FrictionRear)

        brake = self.brake*brakeForce
        throttle = self.throttle * engineForce
        tractionForce = throttle - brake*sign(velocity_c[0])#Maybe only RWD

        #dragForce_x = 0#rollResist*velocity_c[0] + airResist*velocity_c[0]*abs(velocity_c[0])
        #dragForce_y = 0#rollResist*velocity_c[1] + airResist*velocity_c[1]*abs(velocity_c[1])

        totalForce_x = tractionForce
        totalForce_y = cos(self.steerAngle) * FrictionFront + FrictionRear

        self.accel_c = [totalForce_x/MASS,totalForce_y/MASS]
        
        x,y = velocity_c
        absVel = sqrt(x*x+y*y)
        if abs(absVel) < 0.5*10 and not throttle:
            velocity_c[0] = velocity_c[1] = absVel = 0
            self.velocity[0] = self.velocity[1] = 0
            angularTorque = self.yawRate = 0
            self.brake = 0
        
        cs = -cs
        sn = -sn

        accel = [
            cs*self.accel_c[0] - sn*self.accel_c[1],
            sn*self.accel_c[0] + cs*self.accel_c[1]
        ]
        self.velocity[0] += accel[0]*dt
        self.velocity[1] += accel[1]*dt

        angularTorque = cos(self.steerAngle)*FrictionFront*CGToFront -  FrictionRear*CGToBack

        angularAccel = angularTorque/INERTIA

        self.yawRate += angularAccel*dt
        self.heading += self.yawRate*dt

        self.position[0] += self.velocity[0]*dt
        self.position[1] += self.velocity[1]*dt

        data = [
            self.steerAngle,
            self.steer,
            self.heading,
            [velocity_c],
            [self.accel_c],
            self.yawRate,
            [yawSpeedFront,yawSpeedRear],
            [slipAngleFront,slipAngleRear],
            [FrictionFront,FrictionRear]
        ]
        data_plot.update(data,dt,False)
    def collisions(self,line):
        x, y = self.position
        coordinates = [[-0.8,-2],[-0.8,2],[0.8,2],[0.8,-2]]
        for i in range(len(coordinates)):
            coor = coordinates[i]
            sn = sin(self.car.heading+0.5*pi)
            cs = cos(self.car.heading+0.5*pi)
            coor = [cs*coor[0] - sn*coor[1],sn*coor[0]+cs*coor[1]]
            coor = [coor[0]*10+x,coor[1]*10+y]
            coordinates[i] = coor
        collsion = []
        for i in range(-1,3,1):
            lineB = (coordinates[i],coordinates[i+1])
            collsion.append(self.collision(line,lineB))
    def collision(self,lineA,lineB):
        p1 = lineB[0]
        p2 = lineB[1]
        
        #print(self.velocity)
##### -------------------------------------------- #####
data_plot =Plot()
auto = Car()
class Game():
    car = None
    dis = None
    running = False
    def __init__(self):
        pygame.init()
        self.dis = pygame.display.set_mode((1000,600))
        self.car = Car()
        
    def event_Handling(self,events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.car.throttle = 1
                if event.key == pygame.K_DOWN:
                    self.car.brake = 1
                if event.key == pygame.K_LEFT:
                    self.car.steer = 1
                if event.key == pygame.K_RIGHT:
                    self.car.steer = -1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.car.throttle = 0
                if event.key == pygame.K_DOWN:
                    self.car.brake = 0
                if event.key == pygame.K_LEFT:
                    self.car.steer = 0
                if event.key == pygame.K_RIGHT:
                    self.car.steer = 0
            if event.type == pygame.QUIT:
                pygame.quit()
                data_plot.show(True)
    def update(self):
        self.dis.fill((255,255,255))
        x, y = self.car.position
        if x>1000 or x<0:
            self.car.position[0] = 500
        if y>600 or y<0:
            self.car.position[1] = 300
        coordinates = [[-0.8,-2],[-0.8,2],[0.8,2],[0.8,-2]]
        for i in range(len(coordinates)):
            coor = coordinates[i]
            sn = sin(self.car.heading+0.5*pi)
            cs = cos(self.car.heading+0.5*pi)
            coor = [cs*coor[0] - sn*coor[1],sn*coor[0]+cs*coor[1]]
            coor = [coor[0]*10+x,coor[1]*10+y]
            coordinates[i] = coor
        pygame.draw.polygon(self.dis,(0,0,0),coordinates)
        #pygame.draw.rect(self.dis,(0,0,0),[x,y,100,10])
        pygame.display.update()
    def main(self):
        self.running = True
        counter = 0
        
        while self.running:
            self.car.update(0.001)
            self.event_Handling(pygame.event.get())
            self.update()
            if False:
                if counter == 0:
                    self.car.throttle = 1
                counter +=1
                if counter == 30:
                    self.car.throttle = 0
                    self.car.steer = 1
                if counter == 30*10:
                    self.car.steer = 0
                if counter == 30*20:
                    
                    while True:
                        data_plot.show(True)
                        time.sleep(10)
            else:
                time.sleep(0.001) # I know that pygame has a clock, and it would probably be more elegant to use it
game = Game()
game.main()