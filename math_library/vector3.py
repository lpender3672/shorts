import math
from .matrix import MATRIX
from .quaternion import Quaternion

class vector3(object):
    def __init__(self, x, y, z):

        self.x, self.y, self.z = x, y, z

        self.mod = math.sqrt(x**2 + y**2 + z**2)

        if self.mod == 0:
            self.norm = None
        elif round(self.mod, 9) == 1:
            self.norm = self
        else:
            self.norm = vector3(x / self.mod, y / self.mod, z / self.mod)

    def zero():
        return vector3(0, 0, 0)

    def ones():
        return vector3(1, 1, 1)

    def __mul__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector3(self.x * b, self.y * b, self.z * b)

        else:
            raise TypeError("Unsupported opperand types")

    def __truediv__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            if b == 0:
                raise ValueError("div by 0")
            return vector3(self.x / b, self.y / b, self.z / b)

        else:
            raise TypeError("Unsupported opperand types")

    def dot(self, b):  # the dot dot product

        if isinstance(b, vector3):
            return self.x * b.x + self.y * b.y + self.z * b.z

        else:
            raise TypeError("Unsupported opperand types")

    def cross(self, b):

        # https://mathinsight.org/cross_product_formula

        x1, y1, z1 = self.x, self.y, self.z
        x2, y2, z2 = b.x, b.y, b.z

        xmat = MATRIX([[y1, z1], [y2, z2]])
        ymat = MATRIX([[x1, z1], [x2, z2]])
        zmat = MATRIX([[x1, y1], [x2, y2]])

        return vector3(xmat.determinant(), -ymat.determinant(),
                       zmat.determinant())

    def __add__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector3(self.x + b, self.y + b, self.z + b)

        if isinstance(b, vector3):
            return vector3(self.x + b.x, self.y + b.y, self.z + b.z)

        else:
            raise TypeError("Unsupported opperand types")

    def __sub__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector3(self.x - b, self.y - b, self.z - b)

        if isinstance(b, vector3):
            return vector3(self.x - b.x, self.y - b.y, self.z - b.z)

        else:
            raise TypeError("Unsupported opperand types")

    def toQuaternion(self):

        return Quaternion(0, self.x, self.y, self.z)

    def angleBetween(self, v):
        dot = self.dot(v)

        return math.acos(dot / (self.mod * v.mod))

    def rotate(self, A, a):  # rotate

        # rotate V around axis A by angle a
        # q = (cos a/2 , A.x * sin a/2, A.y * sin a/2, A.z * sin a/2)
        # V' = q V q.conjegate

        V = self.toQuaternion()

        q = Quaternion(
            math.cos(a / 2), A.norm.x * math.sin(a / 2),
            A.norm.y * math.sin(a / 2), A.norm.z * math.sin(a / 2))

        Rv = q * V * q.conjegate()

        return vector3(Rv.b, Rv.c, Rv.d)

    def toList(self):
        return [self.x, self.y, self.z]

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z)



class zeros(vector3):
  def __init__(self):
    super().__init__(0,0,0)

class ones(vector3):
  def __init__(self):
    super().__init__(1,1,1)