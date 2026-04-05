import numpy as np
import cupy as cp

from objects.line import line
from objects.plane import plane




def getRotationMatrix(axis, angle):
    # https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula

    K = np.array(   [[      0,-axis[2],  axis[1]],
                     [ axis[2],      0,  -axis[0]],
                     [-axis[1], axis[0],       0]])

    R = np.identity(3) + K * np.sin(angle) + np.matmul(K, K) * (1 - np.cos(angle))

    return R





def trace_Vector(verticies, cam):  # instead of triangles


    fps = np.array([cam.focalpos] * len(verticies))
    ops = np.array([cam.planeOrigin] * len(verticies))

    ds = verticies - fps

    a, b, c, d = cam.plane.cartesian()

    dx,dy,dz = -ds[:,0],-ds[:,1],-ds[:,2]

    px, py, pz = -fps[:,0], -fps[:,1], -fps[:,2]

    det = (a * dx + b * dy + c * dz)
    det = 1 / det

    X = det * (dx * d
               + (b * dy + c * dz) * px
               - b * dx * py
               - c * dx * pz)

    Y = det * (dy * d
               - a * dy * px
               + (a * dx + c * dz) * py
               - c * dy * pz)

    Z = det * (dz * d
               - a * dz * px
               - b * dz * py
               + (a * dx + b * dy) * pz)

    v3onPlane = np.array([X, Y, Z]).T - ops


    x = np.dot(v3onPlane, cam.right)/ np.linalg.norm(cam.right)
    y = np.dot(v3onPlane, cam.down)/ np.linalg.norm(cam.down)

    v2 = np.array([x, y]).T * cam.f

    return v2, ds