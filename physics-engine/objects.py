from maths import *
from maths import vector3 as v3

import math

import pygame

class display(object):
    def __init__(self, width, height, factor):
        self.w = width
        self.h = height

        self.f = factor


class camera(object):

    def __init__(self, pos, anglex, angley, display, fov):
        self.pos = pos

        self.f = display.f

        camwidth,camheight = display.w/display.f, display.h/display.f

        vLeft = v3(-camwidth / 2, 0, 0)

        vLeft = vLeft.rotate(v3(0, 1, 0), angley)

        vUp = v3(0, camheight / 2, 0)

        vUp = vUp.rotate(vLeft, anglex)

        self.left = vLeft
        self.up = vUp

        normal = vLeft.cross(vUp).norm * -1

        h = display.w / (2 * math.tan((fov / 2) * (math.pi / 180)))
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



class mesh(object):

    def __init__(self, verticies, triangles, normals, materials, displayed):  # [v3] , [[0,1,2] triangle between verticies 0 1 2 ], [v3 normals] , [mat]

        self.verticies = verticies

        self.triangles = triangles
        self.normals = normals
        self.materials = materials
        self.displayed = displayed



    def render(self, camera, display):

        self.displayed = True

        vs = []
        for v in self.verticies:
            v2 = trace_Vector(v, camera)

            if v2.k < 1 and True:  # if rendered a vertex behind plane
                self.displayed = False # then dont render the mesh AT ALL
                break

            vs.append(v2)


        for t,n,m in zip(self.triangles,self.normals,self.materials):

            if n.dot(self.pos-camera.focalpos) < 0 and self.displayed: # trace triangle not perfect

                v1,v2,v3 = vs[t[0]], vs[t[1]], vs[t[2]]

                if n.dot(v1.ld) < 0 and n.dot(v2.ld) < 0 and n.dot(v3.ld) < 0:

                    pygame.draw.polygon(display, m.colour, [(v1.x, v1.y), (v2.x, v2.y), (v3.x, v3.y)] )

                    pygame.draw.line(display, (0, 0, 0), (v1.x, v1.y), (v2.x, v2.y))
                    pygame.draw.line(display, (0, 0, 0), (v2.x, v2.y), (v3.x, v3.y))
                    pygame.draw.line(display, (0, 0, 0), (v3.x, v3.y), (v1.x, v1.y))





class cuboid(mesh):

    def __init__(self, pos, dim, displayed = True, mat = None):
        self.pos = pos  # pos is the centre of mass
        self.dim = dim
        self.displayed = displayed

        l, h, w = (self.dim / 2).toList() # half of full size so from centre

        verticies =[v3( l,  h,  w) + pos,
                    v3( l,  h, -w) + pos,
                    v3( l, -h,  w) + pos,
                    v3( l, -h, -w) + pos,
                    v3(-l,  h,  w) + pos,
                    v3(-l,  h, -w) + pos,
                    v3(-l, -h,  w) + pos,
                    v3(-l, -h, -w) + pos]

        triangles = [[1,5,7],
                     [1,3,7],
                     [5,6,7],
                     [4,5,6],
                     [2,4,6],
                     [0,2,4],
                     [0,1,3],
                     [0,2,3],
                     [0,1,4],
                     [1,4,5],
                     [2,3,6],
                     [3,6,7]]

        normals = [v3( 0, 0, 1),
                   v3( 0, 0, 1),
                   v3( 1, 0, 0),
                   v3( 1, 0, 0),
                   v3( 0, 0,-1),
                   v3( 0, 0,-1),
                   v3(-1, 0, 0),
                   v3(-1, 0, 0),
                   v3( 0,-1, 0),
                   v3( 0,-1, 0),
                   v3( 0, 1, 0),
                   v3( 0, 1, 0)]

        materials = [mat for m in range(len(triangles))]

        super().__init__(verticies, triangles, normals, materials, displayed)



    def translate(self, v):
        self.pos = self.pos + v
        # displacement vector change pos

    def rotate(self, axis, angle):
        for v in self.verticies:
            v.rotate(axis, angle)

    def draw(self, cam, display):

        for t in self.triangles:

            t2d = t.convert2D(cam)

            if t2d.displayed:
                vs = t2d.verticies
                pygame.draw.line(display, (0, 0, 0), (vs[0].x, vs[0].y), (vs[1].x, vs[1].y))
                pygame.draw.line(display, (0, 0, 0), (vs[1].x, vs[1].y), (vs[2].x, vs[2].y))
                pygame.draw.line(display, (0, 0, 0), (vs[2].x, vs[2].y), (vs[0].x, vs[0].y))



        return


    def getInertialFrame(self):
        pass
        # return list of triangles


class cube(cuboid):  # inherit from cuboid

    def __init__(self, pos, l=1, mat = None):

        super().__init__(pos, v3(l, l, l), mat = mat)



class sphere(object):

    def __init__(self, pos, r):
        pass