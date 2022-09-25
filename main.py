import time
from turtle import position
import pygame
import math

class Car():
    #velocity = (0,0,0) # velocity relative to the cars x and y
    position = (100,100,0)
    global_velocity = [0,0,0]
    direction = 90 # the direction the car is facing
    reibung = 10# negativ influence the y velocity
    max_speed = 10
    max_acceleration = 100
    acceleration = 0
    z = 0
    gravity = -9.81
    jump_force = 10
    counter = 0
    def accelerate(self):
        self.counter = 0
        self.acceleration = self.max_acceleration
    def bremsen(self):
        self.acceleration = -self.max_acceleration
    
    def jump(self):
        x,y,z = self.velocity
        z = self.jump_force
        self.velocity = (x,y,z)
    
    def update(self, time):
        self.counter +=1
        if self.counter == 1/time:
            self.acceleration = 0
            self.counter =0
        x, y, z = self.position
        #x2, y2, z2 = self.velocity
        # 90 degree no roatatioon
        #[ [x*cos (a)+ y*-sin(a)],
        # [x*sin(a) + y*cos[a]]]
        # Zeile[x][y] * Spalte[x][y]
        # 
        angle = self.direction*math.pi/180
        #x, y, z = self.position
        x += self.global_velocity[0]*time
        y += self.global_velocity[1]*time
        z += self.global_velocity[2]*time
        if z<0:
            z=0
        self.position = (x,y,z)
        
        z_velocity = self.global_velocity[2]
        if z>0:
            z_velocity += self.gravity
        else:
            z_velocity =0 
        x, y, _ = self.global_velocity
        velocity = [x*math.cos(angle)+ y*-math.sin(angle),
                    x*math.sin(angle)+y*math.cos(angle)]
        old = velocity[1]
        velocity[1] += self.acceleration*time
        
        if old <0 and velocity[1]>1 or old>0 and velocity[1]<0:
            self.acceleration = 0
            velocity[1] = 0
        
        if abs(velocity[1])>self.max_speed:
            velocity[1] = velocity[1]/abs(velocity[1]) *self.max_speed
        if velocity[0]<0:
            velocity[0] += min(abs(velocity[0]),self.reibung)
        else:
            velocity[0] -= min(abs(velocity[0]),self.reibung)
        x,y = velocity
        x2 = x*math.cos(-angle)+ y*-math.sin(-angle)
        y2 = x*math.sin(-angle)+y*math.cos(-angle)
        self.global_velocity = [x2,y2,z_velocity]
        
    def steer(self,angle):
        self.direction += 90
auto = Car()
if __name__ == "__main__":        
    pygame.init()
    dis = pygame.display.set_mode((1000,600))
    dis.fill((255,255,255))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    auto.accelerate()
                if event.key == pygame.K_DOWN:
                    auto.bremsen()
                if event.key == pygame.K_LEFT:
                    auto.steer(10)
                if event.key == pygame.K_RIGHT:
                    auto.steer(-10)
        x, y, _ = auto.position
        #dis.fill((255,255,255))
        #pygame.draw.rect(dis,(0,0,0),[x,y, 100, 10])
        pygame.draw.circle(dis,(0,0,0),[x,y],2)
        pygame.display.update()
        auto.update(0.03)
        time.sleep(0.03)
                    
        
