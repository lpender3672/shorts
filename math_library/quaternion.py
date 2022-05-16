import math

class Euler(object):
  def __init__(self, roll, pitch, yaw):
    self.yaw = roll     # x
    self.pitch = pitch  # y
    self.roll = yaw     # z
  

class Quaternion(object):  # basically a 4d vector
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b  # x
        self.c = c  # y
        self.d = d  # z

    def conjegate(self):
        return Quaternion(self.a, self.b * -1, self.c * -1, self.d * -1)

    def __mul__(a, b):
        if isinstance(b, Quaternion):

          w = a.a * b.a - a.b * b.b - a.c * b.c - a.d * b.d
          x = a.a * b.b + a.b * b.a + a.c * b.d - a.d * b.c
          y = a.a * b.c - a.b * b.d + a.c * b.a + a.d * b.b
          z = a.a * b.d + a.b * b.c - a.c * b.b + a.d * b.a

          return Quaternion(w, x, y, z)
        
        else:
          raise TypeError("Unsupported opperand types")


class octernion(object):
    def __init__(self, a, b, c, d, e, f, g, h):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.g = g
        self.h = h

    def conjegate(self):
        return octernion(self.a, self.b * -1, self.c * -1, self.d * -1, self.e * -1, self.f * -1, self.g * -1, self.h * -1)
    
    def __mul__(q, s):
        if isinstance(s, octernion):
            a = q.a * s.a - q.b * s.b - q.c * s.c - q.d * s.d - q.e * s.e - q.f * s.f - q.g * s.g - q.h * s.h
            b = q.a * s.b + q.b * s.a + q.c * s.h - q.d * s.g + q.e * s.f + q.f * s.e + q.g * s.d - q.h * s.c
            c = q.a * s.c - q.b * s.h + q.c * s.a + q.d * s.f - q.e * s.e + q.f * s.d + q.g * s.b + q.h * s.b
            d = q.a * s.d + q.b * s.g - q.c * s.f + q.d * s.a + q.e * s.c + q.f * s.b + q.g * s.h - q.h * s.e
            e = q.a * s.e - q.b * s.c + q.c * s.b + q.d * s.h + q.e * s.a + q.f * s.d - q.g * s.f + q.h * s.g
            f = q.a * s.f + q.b * s.d - q.c * s.e + q.d * s.b + q.e * s.h - q.f * s.a + q.g * s.c + q.h * s.g
            g = q.a * s.g - q.b * s.h + q.c * s.f + q.d * s.e + q.e * s.d + q.f * s.c + q.g * s.a + q.h * s.b
            h = q.a * s.h + q.b * s.g + q.c * s.e - q.d * s.b + q.e * s.b + q.f * s.h + q.g * s.g + q.h * s.a
            return octernion(a, b, c, d, e, f, g, h)

        if isinstance(s, float) or isinstance(s, int):
            return octernion(q.a * s, q.b * s, q.c * s, q.d * s, q.e * s, q.f * s, q.g * s, q.h * s)

        else:
            raise TypeError("Unsupported opperand types")