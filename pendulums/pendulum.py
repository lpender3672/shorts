
import pygame
import numpy as np
from multiprocessing import Process

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0,204,204)
ORANGE = (255,127,80)
GRAY = (80,80,80)
g = 9.81

class pendulum(object): # template of a pendulum

    def __init__(self, pos, l, a, da = 0, colour = BLACK):
        self.pos = pos
        self.l = l

        self.colour = colour

        self.a = a
        self.da = da
        self.dda = 0

    def update(self, dt):

        self.da += dt * self.dda
        self.a += dt * self.da

        while self.a > 2*np.pi:
            self.a -= 2*np.pi
        while self.a < -2*np.pi:
            self.a += 2*np.pi

    def getpos(self):
        x = self.pos[0] + abs(self.l) * np.sin(self.a)
        y = self.pos[1] + abs(self.l) * np.cos(self.a)
        return [x,y]

    def draw(self, surface):
        pos = self.getpos()

        pygame.draw.line(surface, self.colour, self.pos, pos, 3)

        #pygame.draw.circle(surface, colour, pos, 10)




class singlependulum(pendulum):
    
    def __init__(self, pos, l, a, da = 0, colour = BLACK):
        super().__init__(pos, l, a, da, colour)
    
    def update(self, dt):
        self.dda = - ( g * np.sin(self.a) + 2 * self.da * self.da) / self.l
        super().update(dt)