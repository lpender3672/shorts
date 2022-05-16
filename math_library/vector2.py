import math
from .matrix import MATRIX
from .quaternion import Quaternion

class vector2(object):
    def __init__(self, x, y):

        self.x, self.y = x, y

        self.mod = math.sqrt(x ** 2 + y ** 2)

        if self.mod == 0:
            self.norm = None
        elif round(self.mod, 9) == 1:
            self.norm = self
        else:
            self.norm = vector2(x / self.mod, y / self.mod)

    def __mul__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector2(self.x * b, self.y * b)

        else:
          raise TypeError("Unsupported opperand types")

    def __truediv__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            if b == 0:
                raise ValueError("div by 0")
            return vector2(self.x / b, self.y / b)

        else:
          raise TypeError("Unsupported opperand types")

  
    def __add__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector2(self.x + b, self.y + b)

        elif isinstance(b, vector2):
            return vector2(self.x + b.x, self.y + b.y)
          
        else:
          raise TypeError("Unsupported opperand types")

    def __sub__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector2(self.x - b, self.y - b)

        elif isinstance(b, vector2):
            return vector2(self.x - b.x, self.y - b.y)
          
        else:
          raise TypeError("Unsupported opperand types")

    def dot(self, v):
      
        if isinstance(v, vector2):
          return self.x * v.x + self.y * v.y
        
        else:
          raise TypeError("Unsupported opperand types")

    def angleBetween(self, v):
        dot = self.dot(v)

        return math.acos(dot / (self.mod * v.mod))

    def toQuaternion(self):

        return Quaternion(0, self.x, self.y, 0)

    def rotate(self, A, a):  # rotate

        # rotate V around axis A by angle a
        # q = (cos a/2 , A.x * sin a/2, A.y * sin a/2, A.z * sin a/2)
        # V' = q V q.conjegate

        V = self.toQuaternion()

        q = Quaternion(
            math.cos(a / 2),
            A.norm.x * math.sin(a / 2),
            A.norm.y * math.sin(a / 2),
                                    0)

        Rv = q * V * q.conjegate()

        return vector2(Rv.b, Rv.c, Rv.d)

    def toList(self):
        return [self.x, self.y, self.z]

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z)


      
class zeros(vector2):
  def __init__(self):
    super().__init__(0,0)

class ones(vector2):
  def __init__(self):
    super().__init__(1,1)