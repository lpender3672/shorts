
import numpy as np
import cupy as cp

from functions import *

class rigidbody(object):

    def __init__(self, mesh, mass = 1):  # [v3] , [[0,1,2] triangle between verticies 0 1 2 ], [v3 normals] , [mat]

        self.mesh = mesh

        self.pos = mesh.pos
        self.mass = mass

        self.resultantForce = np.zeros(3)

        self.resultantTorque = np.zeros(3)
        self.axis = np.zeros(3)

        self.a = np.zeros(3)
        self.v = np.zeros(3)

        self.angle = 0
        self.angularV = 0


    def rotate(self, axis, angle, point = None):

        if point == None:
            point = self.pos

        R = getRotationMatrix(axis, angle)



        newVs = []
        for v in self.mesh.verticies:
            v = v - point
            Rv = np.matmul(R , v)
            newVs.append(Rv + point)

        self.mesh.verticies = newVs

        newNs = []
        for n in self.mesh.normals:
            Rn = np.matmul(R, n)
            newNs.append(Rn)

        self.mesh.normals = newNs

    def translate(self, V):

        self.pos = self.pos + V
        newVs = []
        for v in self.mesh.verticies:
            newVs.append(v+V)

        self.mesh.verticies = newVs

    def scale(self):
        pass



    def addTorque(self, torque):

        self.resultantTorque += torque

    def addForce(self, force, point = np.zeros(3)): # point relative to pos

        self.resultantForce += force

        if point != np.zeros(3):

            torque = force.cross(point)
            self.addTorque(torque)

    def update(self,dt):

        # update position with forces

        dp = self.resultantForce * dt

        dv = dp/self.mass

        self.v += dv
        self.translate(self.v*dt)

        # ANGULAR this is where it gets hard

        dpa = self.resultantTorque * dt

        normdpa = np.linalg.norm(dpa)
        if normdpa != 0:
            self.axis = dpa

        dva = normdpa/self.mesh.angularInertia(self.mass, self.resultantTorque)  # should really input axis here

        self.angularV += dva
        self.rotate(self.axis, self.angularV * dt)












    def intersecting(self, rb2):

        # true or false if intersecting this other body
        pass
