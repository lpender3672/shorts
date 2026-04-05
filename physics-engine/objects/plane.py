import numpy as np
import cupy as cp

from .line import line

class plane(object):
    def __init__(self, normal, point):
        self.n = normal
        self.p = point

        self.d = self.n.dot(self.p)

    def cartesian(self):
        return np.array([self.n[0], self.n[1], self.n[2], self.n.dot(self.p)])


    def minDistToPoint(self, point):

        return abs(self.n.dot(point) - self.d)/ np.linalg.norm(self.n)




    def intersect(self, obj):

        if isinstance(obj, plane):

            d = np.cross(self.n, obj.n)

            var = np.array([self.n, obj.n, d])
            equ = np.array([self.d, obj.d, 0])

            try:
                res = np.linalg.solve(var, equ)
                return line(d, res)

            except np.linalg.LinAlgError:
                # if planes are parallel
                return None

        elif isinstance(obj, line):

            ddotn = (obj.d.dot(self.n))

            if ddotn != 0:

                k = (self.p - obj.p).dot(self.n)/ddotn

                return obj.getpoint(k)

            else:
                return None

