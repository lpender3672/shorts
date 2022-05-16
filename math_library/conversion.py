import math

from quaternion import *


def RAD(degrees):
  return degrees * (math.pi/180)

def DEG(radians):
  return radians * (180/math.pi)


def EulerToQuaternion(E):

    cy = math.cos(E.yaw * 0.5)
    sy = math.sin(E.yaw * 0.5)
    cp = math.cos(E.pitch * 0.5)
    sp = math.sin(E.pitch * 0.5)
    cr = math.cos(E.roll * 0.5)
    sr = math.sin(E.roll * 0.5)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy

    return Quaternion(w, x, y, z)


def QuaternionToEuler(Q):

    w, x, y, z = Q.a, Q.b, Q.c, Q.d

    # roll (x-axis rotation)
    t0 = 2 * (w * x + y * z)
    t1 = 1 - 2 * (x * x + y * y)
    roll = math.atan2(t0, t1)

    # pitch (y-axis rotation)
    t2 = 2 * (w * y - z * x)
    t2 = 1 if t2 > 1 else t2
    t2 = 1 if t2 < -1 else t2
    pitch = math.asin(t2)

    # yaw (z-axis rotation)
    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(t3, t4)

    return Euler(roll, pitch, yaw)

