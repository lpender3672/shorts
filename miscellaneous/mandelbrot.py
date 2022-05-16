
import pygame

import numpy as np
from numpy import newaxis

width,height = 800,400

asp = height/width

k=0
zoom = 3*np.exp(k)



N_max = 50

omx,omy = 0,0
px,py = -1,-1

crashed = False
pan = False

pygame.init()
display = pygame.display.set_mode((width, height))

while not crashed:

    mx, my = pygame.mouse.get_pos()

    events = pygame.event.get()

    for event in events:

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                crashed = True

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 4:
                k+=0.1
            if event.button == 5:
                k-=0.1

            if event.button == 1:
                pan = True

        if event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:
                pan = False

    zoom = 3 * np.exp(k)

    if pan:
        px += 10 * zoom * (mx-omx)/width
        py += 10 * zoom * asp * (my-omy)/height

    x = np.linspace(px, zoom + px, width)
    y = np.linspace(py, zoom * asp  + py, height)

    C = (x[:, newaxis] + 1j * y[newaxis, :])

    Z = np.zeros((width, height), dtype=complex)
    M = np.full((width, height), True, dtype=bool)
    for i in range(int(10-10*k)):
        Z[M] = Z[M] * Z[M] + C[M]
        M[np.abs(Z) > 2] = False

    print(255*M)

    surf = pygame.surfarray.make_surface(255*M)

    display.blit(surf, (0,0))
    pygame.display.update()

    omx,omy = mx,my

