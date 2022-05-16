import time
import numpy
import sympy
from sympy.utilities.lambdify import lambdify

import copy

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot, cm
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


w = h = 10.
# intervals in x-, y- directions, mm
dx = dy = 0.1
# Thermal diffusivity of steel, mm2.s-1
D = 4.

Tcool, Thot = 300, 700

nx, ny = int(w/dx), int(h/dy)

dx2, dy2 = dx*dx, dy*dy
dt = dx2 * dy2 / (2 * D * (dx2 + dy2))

print(cm.cmaps_listed)

nt = 5000

# =========================================

x = numpy.linspace(0, w, nx)
y = numpy.linspace(0, h, ny)

u = Tcool * numpy.ones((ny, nx))

un = Tcool * numpy.ones((ny, nx))


###Assign initial conditions

##set hat function I.C. : u(.5<=x<=1 && .5<=y<=1 ) is 2


r, cx, cy = 3, 5, 5
r2 = r**2
for i in range(nx):
    for j in range(ny):
        p2 = (i*dx-cx)**2 + (j*dy-cy)**2
        if p2 < r2:
            u[i,j] = Thot

udata = []
step = 20
# start:stop:step
#   du(x,y) = dt * k * ((u+1 + 2u - u-1)/(dx**2) + (u+1 + 2u - u-1)/(dy**2))

# u X+1 = u[2:, 1:-1]
# u X-1 = u[0:-2, 1:-1]

# u y+1 = u[1:-1, 2:]
# u y-1 = u[1:-1, 0:-2]


for n in range(nt + 1):  ##loop across number of time steps
    un = u.copy()

    u[1:-1, 1:-1] = (un[1:-1, 1:-1] +
                    dt * D * (   (un[2:, 1:-1] - 2 * un[1:-1, 1:-1] + un[0:-2, 1:-1])/dx2
                               + (un[1:-1, 2:] - 2 * un[1:-1, 1:-1] + un[1:-1, 0:-2])/dy2))

    u[1:-1 , 0] = u[1:-1 , 1]
    u[1:-1, -1] = u[1:-1, -2]

    u[0, 1:-1] = u[1, 1:-1]
    u[-1,1:-1] = u[-2,1:-1]

    u[0,0] = u[1,1]
    u[0, -1] = u[1, -2]
    u[-1, 0] = u[-2, 1]
    u[-1, -1] = u[-2, -2]



    if n%step == 0:
        udata.append(un)

print("done computation")

X, Y = numpy.meshgrid(x, y)



def update_surfaces(frame, graph, data, surfaceplots):

    surfaceplots[0].remove()
    surfaceplots[0] = graph.plot_surface(X, Y, data[frame], cmap=cm.inferno, vmin=Tcool, vmax=Thot)



fig = pyplot.figure(figsize=(16, 9), dpi=100)


#ax = p3.Axes3D(fig)

ugraph = fig.add_subplot(1, 2, 1, projection='3d')

ugraph.set_xlim(0, w)
ugraph.set_ylim(0, h)
ugraph.set_zlim(Tcool, Thot)


usurfaces = [ugraph.plot_surface(X, Y, udata[0], cmap=cm.inferno, vmin=Tcool, vmax=Thot)]


fig.colorbar(usurfaces[0], shrink=0.5, aspect=5)

uanimation = animation.FuncAnimation(fig, update_surfaces, nt//step, fargs=(ugraph, udata, usurfaces), interval=(dt*step*1000), blit=False)

pyplot.show()