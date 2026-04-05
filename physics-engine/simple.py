
import copy, random
import numpy as np

import pygame


from mesh import mesh
from rigidbody import rigidbody




class surface(mesh):
  # cube should be made of these instead

  def __init__(self, pos, size, subsample, materials):


    dx = size/subsample


    super().__init__([],[],[],[])



class cuboid(mesh):

    def __init__(self, pos, dim, mat = None, displayed = True):
        self.pos = pos  # pos is the centre of mass
        self.dim = dim
        self.displayed = displayed

        l, h, w = (self.dim / 2) # half of full size so from centre

        verticies = [np.array([l, h, w]) + pos,
                     np.array([l, h, -w]) + pos,
                     np.array([l, -h, w]) + pos,
                     np.array([l, -h, -w]) + pos,
                     np.array([-l, h, w]) + pos,
                     np.array([-l, h, -w]) + pos,
                     np.array([-l, -h, w]) + pos,
                     np.array([-l, -h, -w]) + pos]

        triangles = [[1, 5, 7],
                     [1, 3, 7],
                     [5, 6, 7],
                     [4, 5, 6],
                     [2, 4, 6],
                     [0, 2, 4],
                     [0, 1, 3],
                     [0, 2, 3],
                     [0, 1, 4],
                     [1, 4, 5],
                     [2, 3, 6],
                     [3, 6, 7]]

        normals = [np.array([0, 0, -1]),
                   np.array([0, 0, -1]),
                   np.array([-1, 0, 0]),
                   np.array([-1, 0, 0]),
                   np.array([0, 0, 1]),
                   np.array([0, 0, 1]),
                   np.array([1, 0, 0]),
                   np.array([1, 0, 0]),
                   np.array([0, 1, 0]),
                   np.array([0, 1, 0]),
                   np.array([0, -1, 0]),
                   np.array([0, -1, 0])]

        materials = [mat for m in range(len(triangles))]

        mesh.__init__(self, verticies, triangles, normals, materials, displayed)


class cube(cuboid):  # inherit from cuboid

    def __init__(self, pos, l=1, mat = None):

        super().__init__(pos, l * np.ones(3), mat = mat)

class square_surface(mesh):
    def __init__(self, pos, l, w, mat, displayed = True):

        self.pos = pos

        verticies = [np.array([pos[0] - l / 2, pos[1], pos[2] - w / 2]),
                     np.array([pos[0] + l / 2, pos[1], pos[2] - w / 2]),
                     np.array([pos[0] - l / 2, pos[1], pos[2] + w / 2]),
                     np.array([pos[0] + l / 2, pos[1], pos[2] + w / 2])]

        poly = [[0, 1, 3, 2]]

        normals = [np.array([0,-1,0])]

        materials = [mat]

        mesh.__init__(self, verticies, poly, normals, materials, displayed)



class sphere(mesh):

    def __init__(self, pos, r):
        pass