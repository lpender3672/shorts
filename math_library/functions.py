
import math, copy

from sympy import im

from quaternion import *
from matrix import *
from objects import *

from vector2 import vector2
from vector3 import vector3



def convertfraction(n, factor=""):
    if round(n, 3) == int(n):
        if int(n) == 1:
            return factor
        return str(int(n)) + factor

    for i in range(2, 1000):
        if round(n * i, 3) % 1 == 0:
            if int(n * i) == 1:
                return factor + "/" + str(i)
            return str(int(n * i)) + factor + "/" + str(i)


def simp(n):
    if convertfraction(n):
        return convertfraction(n)

    irrationals = {"pi": math.pi, "sqrt(2)": math.sqrt(2), "sqrt(3)": math.sqrt(3), "sqrt(5)": math.sqrt(5),
                   "sqrt(7)": math.sqrt(7)}
    # also need e and logs
    for name in irrationals:
        if convertfraction(n / irrationals[name]):
            return convertfraction(n / irrationals[name], name)




def trace_Vector(v3, cam):  # instead of triangles

    l = line(v3 - cam.focalpos, cam.focalpos)

    a, b, c, d = cam.plane.cartesian()

    dx = - l.d.x
    dy = - l.d.y
    dz = - l.d.z

    px = l.p.x
    py = l.p.y
    pz = l.p.z

    det = (a * dx + b * dy + c * dz )
    det = 1 / det;

    m00 =    ( dx )
    m01 =    ( b * dy + c * dz )
    m02 =  - ( b * dx)
    m03 =  - ( c * dx )
    X = det * (m00 * d + m01 * px + m02 * py + m03 * pz)

    m10 =    ( dy)
    m11 =  - ( a * dy )
    m12 =    ( a * dx + c * dz )
    m13 =  - ( c * dy )
    Y = det * (m10 * d + m11 * px + m12 * py + m13 * pz)

    m20 =    ( dz )
    m21 =  - ( a * dz )
    m22 =  - ( b * dz )
    m23 =    ( a * dx + b * dy )
    Z = det * (m20 * d + m21 * px + m22 * py + m23 * pz)

    v3onPlane = vector3(X,Y,Z) - cam.planeOrigin

    d = v3onPlane.mod
    a = v3onPlane.angleBetween(cam.left * -1)
    b = v3onPlane.angleBetween(cam.up * -1)

    if b > math.pi / 2:
        a *= -1

    if a > math.pi / 2:
        b *= -1

    x = d * math.cos(a)
    y = d * math.sin(a)

    v2 = vector2(x, y) * cam.f

    v2.ld = l.d

    return v2




"""
class triangle2(object):
    def __init__(self, verticies, normal, displayed = True, mat = None):
        self.verticies = verticies
        self.norm = normal
        self.displayed = displayed
        self.mat = mat

        # and dont inherit from triangle3


class triangle3(object):
    def __init__(self, verticies, normal=vector3.zero(), displayed = True,  mat=None):

        self.displayed = displayed
        self.verticies = verticies
        self.norm = normal
        self.mat = mat

        # if normal vector facing away from viewer, dont display
        # if normal vector is 0,0,0 or facing towards viewer, display triangle

        # all triangles of all objects are put in a big list then tested, then rendered
        # then rasturised into an image to display

class mesh(object):

"""

"""
    def convert2D(self, camera):

        # advanced...



        a, b, c, d = camera.plane.cartesian()

        # camera focalpos from origin
        p = camera.focalpos

        # find the line that goes through the vector and the focalpos

        # then find the 3d vector that this line intersects the plane using:
        # louis' Matrix

        vector2s = []

        if self.norm.dot(camera.plane.n) > 0:  # if triangle not facing the camera
            return triangle2(vector2s, camera.norm, False, self.mat)


        for v in self.verticies:
            l = line(v - p, p)

            M1 = MATRIX([[a, b, c,      0],
                         [1, 0, 0, -l.d.x],
                         [0, 1, 0, -l.d.y],
                         [0, 0, 1, -l.d.z]])

            M2 = MATRIX([[d], [l.p.x], [l.p.y], [l.p.z]])

            res = M1.inverse() * M2

            # planeVector = vector3(res.arr[0][0], res.arr[1][0], res.arr[2][0]) - camera.planeOrigin BAD METHOD?

            planeVector = l.getpoint(res.arr[3][0]) - camera.planeOrigin  # vector on plane   IF lambda MORE THAN 1 then vector is getting traced forwards

            # find the angle it makes with camera.left
            a = planeVector.angleBetween(camera.left * -1)

            # can now get x and y of the 2d vector
            x = planeVector.mod * math.cos(a)
            y = planeVector.mod * math.sin(a)

            vector2s.append(vector2(x, y))


        return triangle2(vector2s, camera.norm, True, self.mat)
"""
