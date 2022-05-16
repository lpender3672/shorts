from pendulum import pendulum
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0,204,204)
ORANGE = (255,127,80)
GRAY = (80,80,80)
g = 9.81

class elasticpendulum(object):

    def __init__(self, pos, m, l, k, l0, a, de = 0, da = 0, colour = WHITE):

        self.P = pendulum(pos, l, a, da)
        self.P.de = de
        self.P.e = l - l0

        self.m = m
        self.k = k
        self.l0 = l0

        self.colour = colour

    def update(self, dt):

        # new ddl, dda from current data

        self.P.dda = - ( g * np.sin(self.P.a) + 2 * self.P.de * self.P.da) / self.P.l

        self.P.dde = self.P.l * self.P.da**2 + g * np.cos(self.P.a) - (self.k * self.P.e) / (self.m * self.l0) #+ (self.k * self.P.e**2) / (2 * self.m * self.P.l**2)

        self.P.update(dt)

        self.P.de += dt*self.P.dde
        self.P.e += dt*self.P.de

        self.P.l = self.l0 + self.P.e


    def draw(self, surface):

        self.P.draw(surface, self.colour)
