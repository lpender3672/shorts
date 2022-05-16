import multiprocessing
import sys

import numpy
import sympy
from sympy.utilities.lambdify import lambdify

import copy

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot, cm
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


def main():
    ###variable declarations
    nx = 41
    ny = 41
    nt = 200
    c = 1
    dx = 2 / (nx - 1)
    dy = 2 / (ny - 1)
    sigma = .009
    nu = 0.01
    dt = sigma * dx * dy / nu

    x = numpy.linspace(0, 2, nx)
    y = numpy.linspace(0, 2, ny)

    u = numpy.ones((ny, nx))  # create a 1xn vector of 1's
    v = numpy.ones((ny, nx))
    un = numpy.ones((ny, nx))
    vn = numpy.ones((ny, nx))
    comb = numpy.ones((ny, nx))

    ###Assign initial conditions

    ##set hat function I.C. : u(.5<=x<=1 && .5<=y<=1 ) is 2
    u[int(.5 / dy):int(1 / dy + 1), int(.5 / dx):int(1 / dx + 1)] = 2
    ##set hat function I.C. : u(.5<=x<=1 && .5<=y<=1 ) is 2
    v[int(.5 / dy):int(1 / dy + 1), int(.5 / dx):int(1 / dx + 1)] = 2

    udata = []
    vdata = []

    for n in range(nt + 1):  ##loop across number of time steps

        print(n)

        un = u.copy()
        vn = v.copy()

        u[1:-1, 1:-1] = (un[1:-1, 1:-1] -
                         dt / dx * un[1:-1, 1:-1] *
                         (un[1:-1, 1:-1] - un[1:-1, 0:-2]) -
                         dt / dy * vn[1:-1, 1:-1] *
                         (un[1:-1, 1:-1] - un[0:-2, 1:-1]) +
                         nu * dt / dx ** 2 *
                         (un[1:-1, 2:] - 2 * un[1:-1, 1:-1] + un[1:-1, 0:-2]) +
                         nu * dt / dy ** 2 *
                         (un[2:, 1:-1] - 2 * un[1:-1, 1:-1] + un[0:-2, 1:-1]))

        v[1:-1, 1:-1] = (vn[1:-1, 1:-1] -
                         dt / dx * un[1:-1, 1:-1] *
                         (vn[1:-1, 1:-1] - vn[1:-1, 0:-2]) -
                         dt / dy * vn[1:-1, 1:-1] *
                         (vn[1:-1, 1:-1] - vn[0:-2, 1:-1]) +
                         nu * dt / dx ** 2 *
                         (vn[1:-1, 2:] - 2 * vn[1:-1, 1:-1] + vn[1:-1, 0:-2]) +
                         nu * dt / dy ** 2 *
                         (vn[2:, 1:-1] - 2 * vn[1:-1, 1:-1] + vn[0:-2, 1:-1]))

        u[0, :] = 1
        u[-1, :] = 1
        u[:, 0] = 1
        u[:, -1] = 1

        v[0, :] = 1
        v[-1, :] = 1
        v[:, 0] = 1
        v[:, -1] = 1


        udata.append(un)
        vdata.append(vn)

    print("done computation")


    X, Y = numpy.meshgrid(x, y)

    def update_surfaces(frame, graph, data, surfaceplots):

        surfaceplots[0].remove()
        surfaceplots[0] = graph.plot_surface(X, Y, data[frame], cmap=cm.viridis)


    fig = pyplot.figure(figsize=(16, 9), dpi=100)
    #ax = p3.Axes3D(fig)

    ugraph = fig.add_subplot(1, 2, 1, projection='3d')

    ugraph.set_xlim(0, 2)
    ugraph.set_ylim(0, 2)
    ugraph.set_zlim(1, 2.5)

    vgraph = fig.add_subplot(1, 2, 2, projection='3d')

    vgraph.set_xlim(0, 2)
    vgraph.set_ylim(0, 2)
    vgraph.set_zlim(1, 2.5)

    usurfaces = [ugraph.plot_surface(X, Y, udata[0], cmap=cm.viridis)]
    #vsurfaces = [vgraph.plot_surface(X, Y, udata[0], cmap=cm.viridis)]

    #ax.plot_surface(X, Y, u[:]).set_3d_properties()


    uanimation = animation.FuncAnimation(fig, update_surfaces, nt, fargs=(ugraph, udata, usurfaces), interval=(dt*1000), blit=False)
    #vanimation = animation.FuncAnimation(fig, update_surfaces, nt, fargs=(ugraph, vdata, vsurfaces), interval=(dt*1000), blit=False)

    pyplot.show()



def f( x):
    return x * x



if __name__ == "__main__":
    main()
