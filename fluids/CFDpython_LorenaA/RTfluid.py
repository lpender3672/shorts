# real time fluid
# https://www.youtube.com/watch?v=qsYE1wMEMPA

import numpy as np

nx, ny = 41,41

lx,ly = 2,2

dx = lx/(nx-1)
dy = ly/(nx-1)

x = np.linspace(0,lx, nx)
y = np.linspace(0,ly, ny)



V = np.zeros((nx,ny,2)) # velocities array
D = np.ones((nx,ny)) # density array
T = np.zeros((nx,ny)) # temp array

nt = 100
dt = 0.1

