from pendulum import pendulum
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0,204,204)
ORANGE = (255,127,80)
GRAY = (80,80,80)
g = 9.81

class doublependulum(object):

    def __init__(self, pos, l, a1, a2, colour = BLACK):
        self.pos = pos
        self.l = l

        self.P1 = pendulum(pos, l, a1)
        self.P2 = pendulum(self.P1.getpos(), l, a2)

        self.colour = colour

    def update(self, dt):
        Da = self.P1.a - self.P2.a

        A = np.array([[2, np.cos(Da)],
                      [np.cos(Da), 1]])
        B = np.array([-self.P2.da ** 2 * np.sin(Da) - 2 * g * np.sin(self.P1.a) / self.l,
                       self.P1.da ** 2 * np.sin(Da) - g * np.sin(self.P2.a) / self.l])

        C = np.linalg.solve(A, B)

        self.P1.dda = C[0] - 0*self.P1.da
        self.P2.dda = C[1] - 0*self.P2.da
        # calc da
        self.P1.update(dt)
        self.P2.update(dt)

        self.P2.pos = self.P1.getpos()

    def draw(self, surface):

        self.P1.draw(surface, self.colour)
        self.P2.draw(surface, self.colour)