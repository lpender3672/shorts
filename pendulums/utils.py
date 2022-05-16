import pygame
import numpy as np
from multiprocessing import Process


from pendulum import pendulum, singlependulum
from elasticpendulum import elasticpendulum
from doublependulum import doublependulum

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0,204,204)
ORANGE = (255,127,80)
GRAY = (80,80,80)
g = 9.81


def gaussian(x, a, b, c, d=0):
    return a * np.exp(-(x - b)**2 / (2 * c**2)) + d

map = [
    [0.0, (0,0,0)],
    [0.30, (0, 0, .5)],
    [0.60, (0, .5, 0)],
    [0.90, (.5, 0, 0)],
    [1.00, (.75, .75, 0)],
]
trailmap = [
    [0.0, (80/255,80/255,80/255)],
    [0.60, (0, 1, 0)],
    [0.90, (1, 0, 0)],
    [1.00, (.75, .75, 0)],
]
spread = 1.0


def n_pendulums(n, pendulum_class, pos, arange, lrange = 0):
    pendulums = []

    A = np.pi/2
    a = np.linspace(A - arange/2, A + arange/2, n)
    l = np.linspace(280 - lrange/2, 300 + lrange/2, n)
    
    for i in range(n):

        R = sum([gaussian(i, m[1][0], m[0] * n, n / (spread * len(map))) for m in map])
        G = sum([gaussian(i, m[1][1], m[0] * n, n / (spread * len(map))) for m in map])
        B = sum([gaussian(i, m[1][2], m[0] * n, n / (spread * len(map))) for m in map])

        colour = (  int(255*min(1.0, R)),
                    int(255*min(1.0, G)),
                    int(255*min(1.0, B))    )

        if pendulum_class == singlependulum:
            pendulums.append(pendulum_class(pos, l[i], a[i], 0, colour))
        
        elif pendulum_class == elasticpendulum:
            pendulums.append(pendulum_class(pos, 0.5, l[i], 20, l[i], a[i], 0, 0, colour))
        
        elif pendulum_class == doublependulum:
            pendulums.append(pendulum_class(pos, l[i]/2, a[i], a[i], colour))

    #l=250
    #P.append(doublependulum([px, py], l, a[i], a[i], colour))
    return pendulums



def draw_path(surface, points):
    colours = []
    n = len(points)
    if n > 2:
        for i in range(n - 1):

                if i == 500:
                    del points[0]
                    continue

                R = sum([gaussian(i, m[1][0], m[0] * n, n / (spread * len(trailmap))) for m in trailmap])
                G = sum([gaussian(i, m[1][1], m[0] * n, n / (spread * len(trailmap))) for m in trailmap])
                B = sum([gaussian(i, m[1][2], m[0] * n, n / (spread * len(trailmap))) for m in trailmap])

                colours.append(    (    int(255 * min(1.0, R)),
                                        int(255 * min(1.0, G)),
                                        int(255 * min(1.0, B))  )     )

        pygame.draw.lines(surface, colours, points[-500:-1], points[-499:0], 2)
        