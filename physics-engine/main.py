import tkinter as tk

from maths import *
from maths import vector3 as v3

import pygame

import objects
import material

import math, random
### some helpful sources

# https://math.stackexchange.com/questions/164700/how-to-transform-a-set-of-3d-vectors-into-a-2d-plane-from-a-view-point-of-anoth

print("RUN")  # why does REPL NOT RUN

###


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

width,height = 800,800

display = pygame.display.set_mode((width, height))
crashed = False

#print((c + b).arr)


verticies = [v3(1, 2, 3), v3(4, 6, 2), v3(1, 2, 9)]

disp = objects.display(width, height, 100)

campos = v3(0, 2, -2)
camyaw = 0
campitch = 0
#MATRIX([[random.randint(0,100) for i in range(9)] for j in range(9)]).inverse().print()

while not crashed:

  events = pygame.event.get()

  for event in events:
    if event.type == pygame.QUIT:
      crashed = True

    if event.type == pygame.KEYDOWN:
      forward = v3(cam.norm.x, 0, cam.norm.z)
      left = v3(cam.norm.z, 0, -cam.norm.x)

      if event.key == pygame.K_w:
        campos = campos + forward
      if event.key == pygame.K_s:
        campos = campos - forward

      if event.key == pygame.K_a:
        campos = campos + left
      if event.key == pygame.K_d:
        campos = campos - left



    #print(campos, camyaw, campitch)

  x,y = pygame.mouse.get_pos()

  camyaw =    ((x-width/2)/width) * 2 * math.pi
  campitch = -((y-height/2)/height) * 2 * math.pi

  display.fill(WHITE)

  cam = objects.camera(campos, campitch, camyaw, disp, 60) # need a

  for x in range(1):
    for z in range(1):

      c = objects.cube(v3(x,0,z), 1, material.RED())
      c.render(cam, display)



  pygame.display.update()

pygame.quit()
