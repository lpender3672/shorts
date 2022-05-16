import math

from matrix import MATRIX


class line(object):
    def __init__(self, direction, point):
        self.d = direction
        self.p = point

    def getpoint(self, k):
        return self.p + self.d * k


    def rotate(self, axis, angle):
        OA = self.p
        OB = self.p + self.d

        ROA = OA.rotate(axis, angle)
        ROB = OB.rotate(axis, angle)

        return line(ROB - ROA, ROA)





class plane(object):
    def __init__(self, normal, point):
        self.n = normal
        self.p = point

    def cartesian(self):
        return [self.n.x, self.n.y, self.n.z, self.n.dot(self.p)]

    def rotate(self, axis, angle):
        l = line(self.n, self.p)
        l = l.rotate(axis, angle)

        return plane(l.d, l.p)
      
    def minDistToPoint(self, point):
      l = line(self.n, point)

      a, b, c, d = self.cartesian()

      M1 = MATRIX([[a, b, c,     0],
                  [1, 0, 0, -l.d.x],
                  [0, 1, 0, -l.d.y],
                  [0, 0, 1, -l.d.z]])

      M2 = MATRIX([[d], [l.p.x], [l.p.y], [l.p.z]])

      res = M1.inverse() * M2
      k = res.arr[3][0]

      return k*self.n.mod
