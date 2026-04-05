import pygame


from functions import *


class mesh(object):

    def __init__(self, verticies, triangles, normals, materials, displayed = True):  # [v3] , [[0,1,2] triangle between verticies 0 1 2 ], [v3 normals] , [mat]

        self.verticies = verticies
        self.triangles = triangles
        self.normals = normals
        self.materials = materials
        self.displayed = displayed

    def angularInertia(self, density, axis):

        return density

    def render(self, camera, display):   # now it can render a polygon

        vs, ds = trace_Vector(np.array(self.verticies), camera)


        for t,n,m in zip(self.triangles,self.normals,self.materials):

            polyvs = []

            displayTriangle = self.displayed

            for i in t:

                if np.dot(n, ds[i]) > 0:
                    displayTriangle = False
                    break

            if displayTriangle:

                polyvs = [(vs[i, 0], vs[i, 1]) for i in t]

                pygame.draw.polygon(display, m.colour, polyvs)

                # this needs to be more advanced

                for i in range(len(polyvs)):
                    if i + 1 == len(polyvs):
                        pygame.draw.line(display, (0, 0, 0), polyvs[i], polyvs[0])
                        break

                    pygame.draw.line(display, (0, 0, 0), polyvs[i], polyvs[i + 1])





        return vs