import time
import pygame
from math import cos, sin, pi
class Car():
    position = [500,300,0]
    velocity = [0,0,0]
    acceleration = 0
    max_speed = 1
    direction = pi/2
    max_acceleration = 1
    gravity = -9.81
    jump_force = 10
    counter = 0
    acceleration_time = 0.03
    reibung = 10
    def accelerate(self,direction):
        self.counter = 0
        self.acceleration = direction*self.max_acceleration
    def steer(self,angle):
        self.direction += angle/180*pi
    def jump(self):
        self.velocity[2] = self.jump_force
    def move(self):
        x,y,z = self.position
        x2,y2,z2 = self.velocity
        x += x2
        y += y2
        z += z2
        if z<0:
            z=0
        self.position = [x,y,z]
    def add_acceleration(self,velocity,time):
        if self.counter >= self.acceleration_time/time: # Stopping the acceleration after a certain amount of time
            self.acceleration = 0
        self.counter += 1
        x,y,z = velocity
        old_y = y
        y += self.acceleration
        if (y<=0 and old_y>0) or (y>=0 and old_y<0):#Checking if we went from forward to backward or backward to forward
            y = 0
            self.acceleration = 0
            
        if abs(y)>self.max_speed: # Checking for the max speed
            #Not working as intended, when drifting the total speed can be higher than the max speed
            y = y/abs(y) *self.max_speed
        velocity[1] = y
        
        return velocity
    def rotation_matrix(self,velocity,angle): # Transform the velocity from the global coordinate system to a 
                                            # local reference system (y is the direction the car is traveling)
        x,y, z = velocity
        x2 = x*cos(angle) - y*sin(angle)# This isn't magic just math (2d rotation matrix)
        y2 = x*sin(angle) + y*cos(angle)
        velocity = [x2,y2 ,z]
        return velocity
    def calc_gravity(self,time):
        if self.position[2]>0:
            self.velocity[2] -= self.gravity*time
        else:
            self.velocity[2] = 0
        
    def calc_friction(self,velocity): # Getting closer to 0 velocity along the other axis of the car
        b = 0
        if abs(velocity[0])-0.0001>0:
            b = velocity[1]
        if velocity[0]<0:
            velocity[0] += min(abs(velocity[0]),self.reibung)
        else:
            velocity[0] -= min(abs(velocity[0]),self.reibung)
        
        #print(velocity[0])
        return velocity, b
    def update(self,time):
        self.move() #Move the Car
        
        local_velocity = self.rotation_matrix(self.velocity,self.direction) # Convert the velocity to another reference system
        #print(local_velocity)
        local_velocity = self.add_acceleration(local_velocity,time)# Accelerating/Decelerating the car
        self.calc_gravity(time)# Calculating the gravity
        local_velocity, a = self.calc_friction(local_velocity)
        self.velocity = self.rotation_matrix(local_velocity,-self.direction)
        return a
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
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.car.accelerate(1)
                elif event.key == pygame.K_DOWN:
                    self.car.accelerate(-1)
                elif event.key == pygame.K_LEFT:
                    self.car.steer(45)
                elif event.key == pygame.K_RIGHT:
                    self.car.steer(-45)
    def update(self):
        self.dis.fill((255,255,255))
        x, y, _ = self.car.position
        if x>1000 or x<0:
            self.car.position[0] = 500
        if y>600 or y<0:
            self.car.position[1] = 300
        coordinates = [[0,0,0],[0,100,0],[10,100,0],[10,0,0]]
        for i in range(len(coordinates)):
            coor = coordinates[i]
            coor = self.car.rotation_matrix(coor,-self.car.direction)
            coor = [coor[0]+x,coor[1]+y]
            coordinates[i] = coor
        pygame.draw.polygon(self.dis,(0,0,0),coordinates)
        #pygame.draw.rect(self.dis,(0,0,0),[x,y,100,10])
        pygame.display.update()
    def main(self):
        self.running = True
        while self.running:
            self.car.update(0.03)
            self.event_Handling(pygame.event.get())
            self.update()
            
            time.sleep(0.03) # I know that pygame has a clock, and it would probably be more elegant to use it
import matplotlib.pyplot as plt
def test():
    
    for angle in range(1,91,5):
        times = [0]
        element = [1]
        car = Car()
        car.accelerate(1)
        a = car.update(0.03)
        for i in range(round(360/angle)):
            
            car.steer(angle)
            a = car.update(0.03)
            times.append(i*angle)
            element.append(a)
        #print((a/1)**90)
        times.append((i+1)*angle)
        element.append(a)
        plt.plot(times,element)

    plt.legend()

    plt.show(block = True)

test()