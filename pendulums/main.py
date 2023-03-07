
import pygame
import numpy as np
from multiprocessing import Process


from pendulum import pendulum, singlependulum
from elasticpendulum import elasticpendulum
from doublependulum import doublependulum

from utils import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0,204,204)
ORANGE = (255,127,80)
GRAY = (80,80,80)
g = 9.81


width = 1000
height = 1000

display = pygame.display.set_mode((width, height))

pygame.display.set_caption("Pendulums")

clock = pygame.time.Clock()
TicksLastFrame = 0

crashed = False
go = False

a1 = np.pi - 0.01
a2 = np.pi - 0.01
da = 0.000000001


path = False

px, py = width / 2, height / 3

#pendulums = []
pendulums = n_pendulums(100, doublependulum, [px, py], np.pi*10**-8)

#EP = elasticpendulum([px, py], 1, 200, 50, 200, np.pi/2)
#DP = doublependulum([px, py], 200, np.pi/2, np.pi/2, BLUE)
#pendulums.append(DP)

points = []

display.fill(GRAY)

while not crashed:

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            crashed = True

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                crashed = True

            if event.key == pygame.K_SPACE:
                go = not go


    t = pygame.time.get_ticks()
    deltaTime = (t - TicksLastFrame) / 1000.0  # to seconds
    TicksLastFrame = t


    if go:
        #EP.update(deltaTime*10)
        for p in pendulums:
            p.update(deltaTime * 10)

    display.fill(GRAY)

    if go and path:
        #points.append(pendulum.getpos())
        #draw_path(display, points)
        pass
        

    for p in pendulums:
        p.draw(display)

    #EP.draw(display)

    pygame.display.update()


pygame.quit()