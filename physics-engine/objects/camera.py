import numpy as np
import cupy as cp

from functions import getRotationMatrix

from objects.plane import plane



class camera(object):

    def __init__(self, pos, anglex, angley, display, fov):
        self.pos = pos

        self.f = display.f

        camwidth,camheight = display.w/display.f, display.h/display.f

        Yaxis = np.array([0, 1, 0])

        vLeft = np.array([-camwidth / 2, 0, 0])

        vLeft = np.matmul(getRotationMatrix(Yaxis, angley), vLeft)

        vUp = np.array([0, camheight / 2, 0])

        vUp = np.matmul(getRotationMatrix(vLeft, anglex), vUp)

        self.left = vLeft
        self.up = vUp
        self.right = vLeft * -1
        self.down = vUp * -1

        normal = np.cross(vLeft,vUp) * -1
        normal = normal/np.linalg.norm(normal)

        h = display.w / (2 * np.tan((fov / 2) * (np.pi / 180)))
        focalpos = normal * h

        self.norm = normal
        self.focalpos = focalpos + pos

        self.plane = plane(normal, pos)

        self.planeOrigin = pos + vLeft + vUp
        # so first we need the viewing planes equation..
        # ax+by+cz = d where a,b,c is the normal vector to the plane
        # and d is result of the normal vector dotted with the pos
        # the normal vector is found by cross product of 2 vectors on the plane
        # these two vectors are found by rotating ( -width/2 0 0) around ( 0 1 0 )
        # then rotate ( 0 -height/2 0 ) by the