import numpy as np



class axes(object):

    def __init__(self, l):
        self.n = len(l)
        self.mats = np.zeros_like((self.n,3,3))

    def solve_kinematics(self, pos): # returns solved rotations from 3d pos
        pass

    def get_axis_pos(self,i):
        return self.mats[i]
