import numpy as np
import cupy as cp

from mesh import mesh

class cuboid(mesh):

    def __init__(self, pos, dim, mat = None, displayed = True):
        self.pos = pos  # pos is the centre of mass
        self.dim = dim
        self.displayed = displayed

        l, h, w = (self.dim / 2).toList() # half of full size so from centre

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

        normals = [np.array([0, 0, 1]),
                   np.array([0, 0, 1]),
                   np.array([1, 0, 0]),
                   np.array([1, 0, 0]),
                   np.array([0, 0, -1]),
                   np.array([0, 0, -1]),
                   np.array([-1, 0, 0]),
                   np.array([-1, 0, 0]),
                   np.array([0, -1, 0]),
                   np.array([0, -1, 0]),
                   np.array([0, 1, 0]),
                   np.array([0, 1, 0])]

        materials = [mat for m in range(len(triangles))]

        mesh.__init__(self, verticies, triangles, normals, materials, displayed)