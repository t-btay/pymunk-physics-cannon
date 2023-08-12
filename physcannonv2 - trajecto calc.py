# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 14:48:44 2023

@author: Tony
"""

import pygame as pg
import pymunk as munk
import pymunk.pygame_util
import math
import numpy as np
from random import randrange
from math import cos, sin #<shorten calls to cos, sin tan at some point instead of math.cos etc. get rid of tan variable?
import time

###############################################################################

pg.init()

munk.pygame_util.positive_y_is_up = False
RES = WIDTH, HEIGHT = 1000, 750
FPS = 60


screen = pg.display.set_mode((RES))
clock = pg.time.Clock()
draw_options = munk.pygame_util.DrawOptions(screen)
cannon_image = r"sprites\cannon\cannon.png"
target_image = r"sprites\target2.png"
base_font = pg.font.Font(None, 14)
opp = 0
adj = 0
hyp = 0
tan = 0
theta = 0
status_timer = FPS*50
g = -9.8

target_present = False
targetmarker_present = False

space = munk.Space()
space.gravity = (0,-g)

bullet = False

run = True
dt = 1/FPS

###############################################################################

#classes

class Cannon:
    
    def __init__(self, pos, image):
        self.pos = pos
        self.xpos = pos[0]
        self.ypos = pos[1]
        self.image = pg.image.load(image)
        self.rect = self.image.get_rect(center = pos)
        self.origsurface = pg.image.load(image)

class Projectile:
    
    
    def __init__(self, name, pos, image):
        self.name = name
        self.pos = pos
        self.xpos = pos[0]
        self.ypos = pos[1]
        if image:
            self.image = image
            self.surface = pg.image.load(image)
            self.rect = self.image.get_rect(center = pos)
            self.origsurface = pg.image.load(image)
        
        self.body = munk.Body()
        self.body.position = pos
        self.shape = munk.Circle(self.body, 10)
        self.shape.friction = 10
        self.shape.mass = 5
        self.shape.elasticity = 0.8
    
    def spawn(self, space, pos, anglerad, force):
        global target_present
        
        target_present = True
        
        if pos:
            self.body.position = pos
        space.add(self.body, self.shape)
        if anglerad and force:
            if type(force) == type((0,0)):
                self.body.apply_impulse_at_local_point(force)
                
            
            elif type(force) == type(0.0) or type(force) == type(0):  
                forcex = force*math.cos(anglerad)
                forcey = force*math.sin(anglerad)
                self.body.apply_impulse_at_local_point((forcex, -forcey))

                
        
        return self.shape
    
    def remove(self):
        space.remove(self.body, self.shape)
        
class target_marker:
    
    def __init__(self, pos, image):
        self.pos = pos
        self.xpos = pos[0]
        self.ypos = pos[1]
        
        if image:
            self.surface = pg.image.load(image)
            self.rect = self.surface.get_rect(center = pos)
        else:
            self.surface = pg.image.load(target_image)
            self.rect = self.image.get_rect(center = pos)

        
        
        
        
cannon = Cannon((70, 685), cannon_image) #70, 685 for lower left corner placement
bullet1 = Projectile("bullet", cannon.pos, None)
targetmarker = target_marker((100,100), target_image)

print(f"mass = {bullet1.shape.mass}")

###############################################################################

#functions

def munkdraw(space, window, draw_options):
    screen.fill((255,255,255))
    space.debug_draw(draw_options)
    
    #cleanly center and draw cannon
    mx, my = cannon.xpos, cannon.ypos
    screen.blit(cannon.image, (mx - cannon.image.get_width()/2, my - cannon.image.get_height()/2))
    
    #draw debug lines
    liney = pg.draw.line(screen, (230,230,230), (pg.mouse.get_pos()[0], cannon.ypos), pg.mouse.get_pos(), 1)
    linex = pg.draw.line(screen, (230,230,230), cannon.pos, (pg.mouse.get_pos()[0], cannon.ypos), 1)
    lineh = pg.draw.line(screen, (200,200,200), cannon.pos, pg.mouse.get_pos(), 1)
    circle = pg.draw.circle(screen, (230,230,230), cannon.pos, 5)

    if targetmarker_present:
        screen.blit(targetmarker.surface, (targetmarker.rect.x, targetmarker.rect.y))
     
    global opp
    global adj
    global hyp
    
    draw_trajectory(hyp)
    
    #draw text for triangle/cursor/6debug info
    opptext_surface = base_font.render(f"{opp/10} m", True, (150,150,150))
    screen.blit(opptext_surface, ((pg.mouse.get_pos()[0]+5),(pg.mouse.get_pos()[1] + (opp/2))))
    adjtext_surface = base_font.render(f"{adj/10} m", True, (150,150,150))
    screen.blit(adjtext_surface, ((pg.mouse.get_pos()[0] - (adj/2)),(pg.mouse.get_pos()[1] + opp + 5)))
    hyptext_surface = base_font.render(f"{hyp/10} m", True, (150,150,150))
    screen.blit(adjtext_surface, ((pg.mouse.get_pos()[0] - (adj/2)),(pg.mouse.get_pos()[1] + (opp/2) - 18)))
    
    thetatext_surface = base_font.render(f"Ө = {round(theta, 1)}", True, (150,150,150))
    screen.blit(thetatext_surface, (cannon.xpos+20, cannon.ypos+5))
    
    mouspostext_surface = base_font.render(f"{pg.mouse.get_pos()}", True, (150,150,150))
    screen.blit(mouspostext_surface, (pg.mouse.get_pos()[0]+10,pg.mouse.get_pos()[1]+10))
    
    pg.display.update()

def create_boundaries(space, width, height):
    
    rects = [
        [(width/2, height - 10), (width, 20)],
        [(width/2, 10), (width, 20)],
        [(10, height/2), (20, height)],
        [(width - 10, height/2), (20, height)]
    ]
    
    for pos, size in rects:
        
        body = munk.Body(body_type = munk.Body.STATIC)
        body.position = pos
        shape = munk.Poly.create_box(body, size)
        shape.elasticity = 0.5
        shape.friction = 0.5
        space.add(body, shape)

def create_basiclevel(space, width, height):
    
    rects = [
        [(width/2 - 315, height - 150), (width/3, 20)],
        [(width/2 + 150, 430), (width//2.5, 20)]   
    ]
    
    for pos, size in rects:
        
        body = munk.Body(body_type = munk.Body.KINEMATIC)
        body.position = pos
        shape = munk.Poly.create_box(body, size)
        shape.elasticity = 0.5
        shape.friction = 0.5
        shape.color = ((100,100,100,100))
        space.add(body, shape)
        
def create_armthing(space):

    g_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    g_body.position = (300, 300)
       
       
       
    g_throwarm = pymunk.Body()
    g_throwarm.position = (300, 300)
      
    pivot = pymunk.Circle(g_body, 40, (0,0))
    line = pymunk.Segment(g_throwarm, (57,0), (220,0), 15)
    circle = pymunk.Circle(g_throwarm, 24, (64.5, 0))
    
    pivot.friction = 5
    pivot.group = 1
    line.friction = 5
    line.mass = 8
    line.group = 2
    circle.friction = 2
    circle.mass = 30
    circle.elasticity = 0.95
    circle.group = 3
    
    
    
    spring_joint = pymunk.DampedRotarySpring(g_body, g_throwarm, 0, 5000, 100)
    rotation_center_joint = pymunk.PivotJoint(g_body, g_throwarm, (0,0), (0.5,0))
    
    
    space.add(g_body,pivot,circle, line, g_throwarm,rotation_center_joint, spring_joint)
    
def create_brick_wall(mass, size):
    box_mass, box_size = mass, size
    for x in range(600, (WIDTH - 300), box_size[0]):
        for y in range(HEIGHT // 2, HEIGHT - 20, box_size[1]):
            box_moment = pymunk.moment_for_box(box_mass, box_size)
            box_body = pymunk.Body(box_mass, box_moment)
            box_body.position = x, y
            box_shape = pymunk.Poly.create_box(box_body, box_size)
            box_shape.elasticity = 0.1
            box_shape.friction = 1
            box_shape.color = [randrange(256) for i in range(4)]
            space.add(box_body, box_shape)

def calc_trajectory_lowangle(targetx, targety):
    
    global bullet
    global bullet1
    
    print("auto aiming...")

    maxvel = 200 #max initial velocity, starts at max value then automaticall turn down if needed.
    finished = False
    
    for theta in range(-300,1800):
        
        radians = math.radians(theta/20)
        xvel = maxvel*cos(radians)
        yvel = maxvel*sin(radians)
        
        
        for r in range(0, WIDTH - 30, 1):
            
            t = r/(maxvel*cos(radians)) - cannon.xpos/(maxvel*cos(radians))
            h = -(maxvel*sin(radians)*t + 0.5*(g*t**2)) + cannon.ypos
            
            aim = (r,round(h))
            tgt = (targetx, targety)
            #pg.draw.circle(screen, (50,150,200,200), (aim[0], aim[1]), 1) un-comment this to check the scan arc for debugging
            
            if aim == tgt:
                #this section draws the calculated trajectory. un-comment if ya don't want it.
                for r2 in range(cannon.xpos, WIDTH - 30, 1):
                    t2 = r2/(maxvel*cos(radians)) - cannon.xpos/(maxvel*cos(radians))
                    h2 = -(maxvel*sin(radians)*t2 + 0.5*(g*t2**2)) + cannon.ypos
                    pg.draw.circle(screen, "green", (r2, h2), 2)
                pg.display.update()
                time.sleep(2) #inserted pause for visual feedback
                
                print(f"shot at: {theta/20} degrees, radians = {radians}")
                print(f"targetpos = {targetmarker.pos}, mousepos = {pg.mouse.get_pos()}")
                print(f"range = {aim[0]}, height = {aim[1]} at time = {t}")
                print(f"xvel = {xvel}, yvel = {yvel}")
                
                bullet1 = Projectile("bullet", cannon.pos, None)
                impulse = maxvel*bullet1.shape.mass
                impulsex = impulse*sin(radians)
                impulsey = impulse*cos(radians)
                bullet = bullet1.spawn(space, cannon.pos, radians, (impulse))
                
                print(f"impulse = {impulse}, impulsex = {impulse*cos(radians)}, impulsey = {impulse*sin(radians)}")
                print(f"inital velocity = {bullet.body.velocity}")
                
                finished = True
                break
            
            else:
                
                noshot = True
                targetmarker_present = False
                
        if finished:
            break
        
def draw_trajectory(impulse):
    
   global screen
   
   vel = hyp/5
   radians = math.radians(theta)
   
   for r in range(0, WIDTH - 65, 10):
       
       t = r/(vel*cos(radians))
       h = vel*sin(radians)*t + 0.5*(g*t**2)
       
      #print(h)
       
       pg.draw.circle(screen, "black", (r+cannon.xpos, -h+cannon.ypos), 2)
       
   
   ra = round((vel**2*(abs(sin(2*radians))))/9.8) #this range equation can pull the maximum horizontal range of a given trajectory, provided force its fired with and launch angle 
   ti = ra/vel*cos(radians)                       #defines time in terms of range, or x
   he = vel*sin(radians)*ti - 0.5*(g*ti**2)       #defines y, or height, in terms of  t
                                                  # effectively, only the initial impulse/velocity and luanch angle need to be provided and the entire trajectory can be predicted
  # print(f"r = {ra}, h = {he}")

    
    

    
###############################################################################

create_boundaries(space, WIDTH, HEIGHT)
#create_brick_wall(0.6, (35, 20))
#create_basiclevel(space, WIDTH , HEIGHT)



    
while run:

    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            pg.quit()
        
        if event.type == pg.MOUSEBUTTONDOWN:
            
            if event.button == 1:
                if not target_present: 
                     
                    bullet1 = Projectile("bullet", cannon.pos, None) #re initializes the bullet object to reset its orientation and properties. Shot trajectory will break without doing this.
                    bullet = bullet1.spawn(space, cannon.pos, theta, (adj, -opp))
                    
                    
                    print(str(pg.mouse.get_pos()[0]) + " " + str(pg.mouse.get_pos()[1]))
                    print(f"tan: {tan}")
                    print(f"opp = {opp}")
                    print(f"adj = {adj}")
                    print(f"hyp = {hyp}")
                    print(f"theta: {theta}")
                    print(f"target: {target_present}")
                    
                elif bullet and bullet1.body:
                    bullet.velocity = 0
                    bullet1.remove()
                    target_present = False
                    targetmarker_present = False
                
                
        
        if event.type == pg.KEYDOWN:
            
            if event.key == pg.K_RETURN:
                
                if bullet and bullet1.body:
                    bullet.velocity = 0
                    bullet1.remove()
                    target_present = False
                    targetmarker_present = False
                    
            if event.key == pg.K_a:
                print(f"bullet = {bool(bullet)}")
               
                if not target_present:
                    
                    targetmarker = target_marker(pg.mouse.get_pos(), target_image)
                    
                    target_present = True
                    targetmarker_present = True
                    munkdraw(space, screen, draw_options)
                    
                    
                    calc_trajectory_lowangle(targetmarker.rect.centerx, targetmarker.rect.centery)
                
                    print(str(pg.mouse.get_pos()[0]) + " " + str(pg.mouse.get_pos()[1]))
                    print(f"tan: {tan}")
                    print(f"opp = {opp}")
                    print(f"adj = {adj}")
                    print(f"hyp = {hyp}")
                    print(f"theta: {theta}")
                    print(f"target: {target_present}")
                    print("calculating trajectory... (low angle)")
                
                elif bullet and bullet1.body:
                    bullet.velocity = 0
                    bullet1.remove()
                    target_present = False
                    targetmarker_present = False
                
                else:
                    
                    target_present = False
                    targetmarker_present = False
                    
                    
            
    
    #update display info based on timer
    status_timer -= 1 
    if status_timer <= 0:
        print(str(pg.mouse.get_pos()[0]) + " " + str(pg.mouse.get_pos()[1]))
        print(f"tan: {tan}")
        print(f"opp = {opp}")
        print(f"adj = {adj}")
        print(f"hyp = {hyp}")
        print(f"theta: {theta}")
        print(f"target: {target_present}")
        print(f"target marker: {targetmarker_present}")
        status_timer = FPS*50
        
                

    
    if pg.mouse.get_pos()[0]-cannon.xpos: #< presence of conditional prevents dvision by zero error
        
        opp = (cannon.ypos-pg.mouse.get_pos()[1])
        adj = (pg.mouse.get_pos()[0]-cannon.xpos)
        hyp = math.sqrt(opp**2+adj**2)
        tan = opp/adj
        theta = math.atan(opp/adj) * 57.29582790879777 #180/3.14159, converts radians to degrees
        
        #rotates cannon to point at mouse
        if adj < 0:
            theta += 180
        
        
        cannon.image = pg.transform.rotate(cannon.origsurface,theta)
        cannon.rect = cannon.image.get_rect(midleft = cannon.rect.midleft)
        
        #draws parabolic trajectory projectile would take at given aim point
        
        
    
   
    munkdraw(space, screen, draw_options)
    
    
    
    space.step(dt)
    clock.tick()