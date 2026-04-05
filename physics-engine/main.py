import time

import numpy as np
import cupy as cp



import pygame

from objects.camera import camera
from objects.display import display

import material
from rigidbody import rigidbody as rb

from objects.plane import plane
from objects.line import line

from simple import *





BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

width,height = 1920,1080

crashed = False
go = False

# print((c + b).arr)


campos = np.array([0, 3, -2])

sensitivity = 0.2
camyaw = 0
campitch = 0
fov = 90
zoom = 200


disp = display((width, height), zoom)
surface = pygame.display.set_mode((width, height))

cam = camera(campos, campitch, camyaw, disp, fov)

TicksLastFrame = 0
clock = pygame.time.Clock()
unpausedTotal = 0
pausedTotal = 0
deltaTime = 0

s = rb(square_surface(np.zeros(3), 10, 10, material.GREEN()))

o = rb(cuboid(np.array([0,0,0]), np.array([1,2,3]), material.BLUE()))



pygame.init()



while not crashed:

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            crashed = True

        if event.type == pygame.KEYDOWN:
            forward = 2*np.linalg.norm(np.array([cam.norm[0], 0, cam.norm[2]]))
            left = 2*np.linalg.norm(np.array([cam.norm[2], 0, -cam.norm[0]]))

            if event.key == pygame.K_w:
                campos = campos + forward
            if event.key == pygame.K_s:
                campos = campos - forward

            if event.key == pygame.K_a:
                campos = campos - left
            if event.key == pygame.K_d:
                campos = campos + left

            if event.key == pygame.K_KP_ENTER:
                go = not go


            if event.key == pygame.K_ESCAPE:
                crashed = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                zoom+=10
            if event.button == 5:
                zoom-=10
                if zoom == 0:
                    zoom = 1

        # print(campos, camyaw, campitch)
    t = pygame.time.get_ticks()
    deltaTime = (t - TicksLastFrame) / 1000.0  # to seconds
    if go:

        unpausedTotal += deltaTime

    else:
        pausedTotal += deltaTime

    TicksLastFrame = t



    x, y = pygame.mouse.get_pos()

    camyaw = sensitivity * ((x - width / 2) / width) * 2 * np.pi
    campitch = sensitivity * -((y - height / 2) / height) * 0.5 * np.pi

    surface.fill(material.WHITE().colour)

    disp = display((width, height), zoom)
    cam = camera(campos, campitch, camyaw, disp, fov)

    objectlist = []

    for x in range(0):
        for z in range(0):
            pass
            m = cube(np.array([x, 0, z]), 1, material.BLUE())

            objectlist.append(rb(m))


    #o.translate(v3(0,0,0.01))

    if 1 < unpausedTotal < 2:
        o.addTorque(np.array([0.1, 0.2, 0]))

    elif 3 < unpausedTotal < 4:
        o.addTorque(np.array([0.1,0,0]))


    else:
        o.resultantTorque = np.zeros(3)


    #objectlist.append(s)
    objectlist.append(o)
    # objectlist.append(cube(v3(0,0,1), 1, material.BLUE()))
    # objectlist.append(cube(v3(0,0,3), 2, material.RED()))

    if go:
        for obj in objectlist:
            obj.update(deltaTime)

    distanceSortedObjects = sorted(objectlist, key=lambda a: cam.plane.minDistToPoint(a.pos), reverse=False)
    # very bad solution but kind of works
    # renders objects whos centre positions are furthest from the viewing plane first
    # then closer objects pos to the viewing plane are rendered on top...

    # need a ray trace solution...

    font = pygame.font.Font('freesansbold.ttf', 32)


    displayVN = []
    displayVNR = []
    for obj in distanceSortedObjects:
        vs = obj.mesh.render(cam, surface)

        for i in range(0):

            displayVN.append(font.render(str(i), True, material.RED().colour))
            displayVNR.append(displayVN[-1].get_rect())
            displayVNR[-1].left,displayVNR[-1].top = vs[i,0], vs[i,1]






    # debug

    if deltaTime!=0:
        fps = 1/deltaTime
    else:
        fps = 0


    timetext = font.render("T: " + str(round(unpausedTotal, 2)), True, material.RED().colour)
    fpstext = font.render("fps: " + str(round(fps, 2)), True, material.RED().colour)
    timeRect = timetext.get_rect()
    fpsRect = fpstext.get_rect()
    timeRect.top, timeRect.left = 0,0
    fpsRect.top, fpsRect.left = 0, 150
    if not go:
        pausetext = font.render("Paused", True, material.BLUE().colour)
        pauseRect = pausetext.get_rect()
        pauseRect.top, pauseRect.left = 0, disp.w - pauseRect.width
        surface.blit(pausetext, pauseRect)
    surface.blit(timetext, timeRect)
    surface.blit(fpstext, fpsRect)

    for v,R in zip(displayVN, displayVNR):
        surface.blit(v,R)

    pygame.display.update()


pygame.quit()
